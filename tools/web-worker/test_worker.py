"""Local transport regressions: no VM, network, GitHub, or credential access."""
import base64
import io
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
import urllib.error


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_job
import publish_result


class WorkerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="bc23-worker-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "live"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "remote", "add", "origin",
                        "https://github.com/terryvanbelle/battlecode23-vibe.git"], check=True)
        self.request = self.root / "request.json"
        self.job = self.root / "job.py"
        self.output = self.root / "output"

    def prepare(self, code="print('hello')\n", **overrides):
        self.job.write_text(code)
        request = {"id": "job-test-01", "sha256": hashlib.sha256(self.job.read_bytes()).hexdigest(), "timeout_seconds": 5}
        request.update(overrides)
        self.request.write_text(json.dumps(request))
        return request

    def result(self, **overrides):
        request = self.prepare()
        result = {"id": request["id"], "sha256": request["sha256"], "status": "finished", "exit_code": 0,
                  "duration_seconds": 0.1, "stdout_dropped_bytes": 0, "stderr_dropped_bytes": 0}
        result.update(overrides)
        self.output.mkdir()
        (self.output / "result.json").write_text(json.dumps(result))
        return result

    def test_hash_mismatch_cannot_execute_or_create_output(self):
        self.prepare("from pathlib import Path\nPath('should-not-run').write_text('bad')\n", sha256="0" * 64)
        with self.assertRaisesRegex(ValueError, "hash"):
            run_job.run(self.request, self.job, self.repo, self.output)
        self.assertFalse((self.repo / "should-not-run").exists())
        self.assertFalse(self.output.exists())

    def test_invalid_identifiers_and_timeout_are_rejected_before_execution(self):
        for bad in ("../escape", "/absolute", "", "a" * 81, "line\nbreak"):
            with self.subTest(id=bad):
                self.prepare(id=bad)
                with self.assertRaisesRegex(ValueError, "id"):
                    run_job.read_request(self.request)
        for bad in (0, -1, 1801, True, "30", 1.5):
            with self.subTest(timeout=bad):
                self.prepare(timeout_seconds=bad)
                with self.assertRaisesRegex(ValueError, "timeout"):
                    run_job.read_request(self.request)
        self.prepare(timeout_seconds=1800)
        self.assertEqual(run_job.read_request(self.request)["timeout_seconds"], 1800)

    def test_project_environment_excludes_actions_and_other_tokens(self):
        with mock.patch.dict(os.environ, {
            "HOME": str(self.root), "PATH": "/usr/bin", "USER": "driver", "LANG": "C.UTF-8",
            "GOOGLE_APPLICATION_CREDENTIALS": "/local/file-only-selector", "SSH_AUTH_SOCK": "/local/agent",
            "GH_TOKEN": "should-not-reach-job", "GITHUB_TOKEN": "should-not-reach-job",
            "ACTIONS_RUNTIME_TOKEN": "should-not-reach-job", "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "should-not-reach-job",
            "GITHUB_ENV": "/dangerous-output", "GITHUB_OUTPUT": "/dangerous-output",
            "BC23_WORKER_STATE": "/state-that-jobs-must-not-modify",
            "CUSTOM_SECRET": "should-not-reach-job",
        }, clear=True):
            env = run_job.job_environment(self.repo, self.output)
        self.assertEqual(env["BC23_WORKER_REPO"], str(self.repo))
        self.assertEqual(env["BC23_WORKER_OUTPUT"], str(self.output))
        self.assertEqual(env["GOOGLE_APPLICATION_CREDENTIALS"], "/local/file-only-selector")
        self.assertEqual(env["SSH_AUTH_SOCK"], "/local/agent")
        for name in ("GH_TOKEN", "GITHUB_TOKEN", "ACTIONS_RUNTIME_TOKEN", "ACTIONS_ID_TOKEN_REQUEST_TOKEN", "GITHUB_ENV", "GITHUB_OUTPUT", "BC23_WORKER_STATE", "CUSTOM_SECRET"):
            self.assertNotIn(name, env)

    def test_job_uses_live_cwd_and_preserves_existing_checkout(self):
        dirty = self.repo / "uncommitted.txt"
        dirty.write_text("preserve existing work")
        config = (self.repo / ".git/config").read_bytes()
        self.prepare("import json, os\nprint(json.dumps({'cwd': os.getcwd(), 'actions_token': os.environ.get('ACTIONS_RUNTIME_TOKEN')}))\n")
        with mock.patch.dict(os.environ, {"ACTIONS_RUNTIME_TOKEN": "must-not-inherit"}):
            result = run_job.run(self.request, self.job, self.repo, self.output)
        self.assertEqual(result["exit_code"], 0)
        observed = json.loads((self.output / "stdout.txt").read_text())
        self.assertEqual(observed, {"cwd": str(self.repo), "actions_token": None})
        self.assertEqual(dirty.read_text(), "preserve existing work")
        self.assertEqual((self.repo / ".git/config").read_bytes(), config)

    def test_wrong_origin_and_nested_checkout_are_rejected(self):
        self.prepare()
        child = self.repo / "subdirectory"
        child.mkdir()
        with self.assertRaises(ValueError):
            run_job.run(self.request, self.job, child, self.output)
        subprocess.run(["git", "-C", str(self.repo), "remote", "set-url", "origin", "https://github.com/someone/other.git"], check=True)
        with self.assertRaises(ValueError):
            run_job.run(self.request, self.job, self.repo, self.output)
        self.assertFalse(self.output.exists())

    def test_supervisor_bounds_and_redacts_both_logs(self):
        self.prepare("import sys\nprint('x' * 100000)\nprint('Bearer fake-bearer-value ghp_FAKE_TOKEN_ONLY github_pat_FAKE_TOKEN_ONLY')\nprint('sk-FAKE_TEST_SECRET_123456', file=sys.stderr)\n")
        result = run_job.run(self.request, self.job, self.repo, self.output)
        stdout = (self.output / "stdout.txt").read_text()
        stderr = (self.output / "stderr.txt").read_text()
        self.assertGreater(result["stdout_dropped_bytes"], 0)
        self.assertLessEqual(len(stdout), run_job.MAX_LOG)
        self.assertIn("[REDACTED]", stdout)
        for value in ("fake-bearer-value", "ghp_FAKE_TOKEN_ONLY", "github_pat_FAKE_TOKEN_ONLY"):
            self.assertNotIn(value, stdout)
        self.assertNotIn("sk-FAKE_TEST_SECRET_123456", stderr)

    def test_cli_exports_nonzero_results_only_after_validation(self):
        self.prepare("raise SystemExit(4)\n")
        actions_output = self.root / "actions-output"
        env = os.environ.copy()
        env.update(BC23_WORKER_REPO=str(self.repo), BC23_WORKER_OUTPUT=str(self.output), BC23_WORKER_STATE=str(self.root / "state"),
                   GITHUB_OUTPUT=str(actions_output))
        completed = subprocess.run([sys.executable, str(HERE / "run_job.py"), "--request", str(self.request), "--job", str(self.job)],
                                   env=env, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(actions_output.read_text(), "export_ready=true\n")
        self.assertEqual(json.loads((self.output / "result.json").read_text())["exit_code"], 4)

    def test_symlink_output_cannot_overwrite_or_be_marked_for_export(self):
        external = self.root / "must-preserve.txt"
        external.write_text("preserve")
        self.prepare("import os\nfrom pathlib import Path\nPath(os.environ['BC23_WORKER_OUTPUT'], 'stdout.txt').symlink_to(" + repr(str(external)) + ")\n")
        actions_output = self.root / "actions-output"
        env = os.environ.copy()
        env.update(BC23_WORKER_REPO=str(self.repo), BC23_WORKER_OUTPUT=str(self.output), BC23_WORKER_STATE=str(self.root / "state"),
                   GITHUB_OUTPUT=str(actions_output))
        completed = subprocess.run([sys.executable, str(HERE / "run_job.py"), "--request", str(self.request), "--job", str(self.job)],
                                   env=env, capture_output=True, text=True)
        self.assertNotEqual(completed.returncode, 0)
        self.assertFalse(actions_output.exists())
        self.assertEqual(external.read_text(), "preserve")

    def test_preexisting_wrapper_files_fifo_and_hardlinks_cannot_export(self):
        external = self.root / "must-preserve.txt"
        external.write_text("preserve")
        for kind, creation in (
            ("file", "target.write_text('job-owned output')"),
            ("fifo", "os.mkfifo(target)"),
            ("hardlink", "os.link(" + repr(str(external)) + ", target)"),
        ):
            with self.subTest(kind=kind):
                self.prepare("import os\nfrom pathlib import Path\ntarget = Path(os.environ['BC23_WORKER_OUTPUT'], 'stdout.txt')\n" + creation + "\n")
                actions_output = self.root / ("actions-output-" + kind)
                env = os.environ.copy()
                env.update(BC23_WORKER_REPO=str(self.repo), BC23_WORKER_OUTPUT=str(self.root / ("output-" + kind)),
                           BC23_WORKER_STATE=str(self.root / ("state-" + kind)),
                           GITHUB_OUTPUT=str(actions_output))
                completed = subprocess.run([sys.executable, str(HERE / "run_job.py"), "--request", str(self.request), "--job", str(self.job)],
                                           env=env, capture_output=True, text=True, timeout=10)
                self.assertNotEqual(completed.returncode, 0)
                self.assertFalse(actions_output.exists())
                self.assertEqual(external.read_text(), "preserve")

    def test_request_id_is_reserved_and_cannot_execute_twice(self):
        code = "from pathlib import Path\np = Path('test-execution-count')\np.write_text(str(int(p.read_text()) + 1 if p.exists() else 1))\n"
        self.prepare(code)
        state = self.root / "persistent-state"
        result = run_job.run(self.request, self.job, self.repo, self.output, state=state)
        self.assertEqual(result["exit_code"], 0)
        with self.assertRaises(ValueError):
            run_job.run(self.request, self.job, self.repo, self.root / "duplicate-output", state=state)
        self.assertEqual((self.repo / "test-execution-count").read_text(), "1")
        self.assertFalse((self.root / "duplicate-output").exists())
        self.prepare(code, id="job-test-02")
        run_job.run(self.request, self.job, self.repo, self.root / "new-request-output", state=state)
        self.assertEqual((self.repo / "test-execution-count").read_text(), "2")

    def test_timeout_kills_parent_and_child_process_group(self):
        self.prepare("""import os, signal, subprocess, sys, time
from pathlib import Path
signal.signal(signal.SIGTERM, signal.SIG_IGN)
child = subprocess.Popen([sys.executable, '-c', 'import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(60)'])
Path(os.environ['BC23_WORKER_OUTPUT'], 'test-child.pid').write_text(str(child.pid))
time.sleep(60)
""", timeout_seconds=1)
        started = time.monotonic()
        result = run_job.run(self.request, self.job, self.repo, self.output)
        self.assertEqual(result["status"], "timeout")
        self.assertLess(time.monotonic() - started, 8)
        pid = int((self.output / "test-child.pid").read_text())
        proc = Path("/proc") / str(pid) / "status"
        # An orphaned zombie is terminated and awaiting init's reap; it cannot
        # execute or hold output pipes. Never signal unrelated process groups.
        try:
            status = proc.read_text()
        except FileNotFoundError:
            live = False
        else:
            live = not any(line.startswith("State:") and "Z" in line for line in status.splitlines())
        if live:
            os.kill(pid, signal.SIGKILL)
        self.assertFalse(live, "A timed-out job left its child running")

    def test_publisher_rejects_mismatched_result_provenance(self):
        self.result(id="another-request")
        with self.assertRaisesRegex(ValueError, "provenance"):
            publish_result.make_response(self.request, self.output)
        result = json.loads((self.output / "result.json").read_text())
        result.update(id="job-test-01", sha256="f" * 64)
        (self.output / "result.json").write_text(json.dumps(result))
        with self.assertRaisesRegex(ValueError, "provenance"):
            publish_result.make_response(self.request, self.output)

    def test_publisher_refuses_log_symlinks(self):
        self.result()
        external = self.root / "unapproved-source.txt"
        external.write_text("do not publish")
        (self.output / "stdout.txt").symlink_to(external)
        with self.assertRaisesRegex(ValueError, "symlink"):
            publish_result.make_response(self.request, self.output)

    def test_publisher_bounds_redacts_and_discards_unapproved_fields(self):
        self.result(unapproved_secret="must-not-publish-this-field")
        (self.output / "stdout.txt").write_text("x" * 100000 + " ghp_FAKE_TOKEN_ONLY")
        (self.output / "stderr.txt").write_text("Bearer fake-bearer-value")
        with mock.patch.dict(os.environ, {"BC23_WORKER_ARTIFACT_ID": "12345", "GITHUB_RUN_ID": "999"}):
            response = publish_result.make_response(self.request, self.output)
        self.assertNotIn("unapproved_secret", response)
        self.assertNotIn("must-not-publish-this-field", json.dumps(response))
        self.assertLessEqual(len(response["stdout"]), run_job.MAX_LOG)
        self.assertNotIn("ghp_FAKE_TOKEN_ONLY", response["stdout"])
        self.assertNotIn("fake-bearer-value", response["stderr"])
        self.assertEqual(response["artifact_id"], "12345")
        self.assertEqual(response["workflow_run_id"], "999")

    def test_setup_failure_has_validated_request_identity(self):
        request = self.prepare()
        response = publish_result.make_response(self.request, self.output)
        self.assertEqual(response["id"], request["id"])
        self.assertEqual(response["sha256"], request["sha256"])
        self.assertEqual(response["status"], "setup_failed")
        self.assertEqual(response["stdout"], "")
        self.assertEqual(response["stderr"], "")

    def test_rejected_exports_ignore_all_job_created_files(self):
        self.result()
        external = self.root / "unapproved-source.txt"
        external.write_text("do not publish")
        (self.output / "stdout.txt").symlink_to(external)
        (self.output / "stderr.txt").write_text("unapproved job output")
        response = publish_result.make_response(self.request, self.output, False)
        self.assertEqual(response["status"], "setup_failed")
        self.assertEqual(response["stdout"], "")
        self.assertEqual(response["stderr"], "")
        self.assertNotIn("do not publish", json.dumps(response))
        self.assertNotIn("unapproved job output", json.dumps(response))


class PublicationTest(unittest.TestCase):
    def setUp(self):
        self.env = mock.patch.dict(os.environ, {
            "GITHUB_REPOSITORY": publish_result.CONTROL_REPO, "GITHUB_REF": "refs/heads/main",
            "GITHUB_API_URL": "https://api.github.com", "GH_TOKEN": "test-only-auth-placeholder",
        }, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.response = {"id": "job-test-01", "sha256": "a" * 64, "status": "finished", "exit_code": 0}

    @staticmethod
    def stream(value):
        return io.BytesIO(json.dumps(value).encode())

    @staticmethod
    def missing():
        return urllib.error.HTTPError("https://api.github.com/", 404, "missing", None, None)

    def private_metadata(self):
        return self.stream({"private": True, "full_name": publish_result.CONTROL_REPO})

    def test_public_or_wrong_repository_is_rejected_before_content_requests(self):
        for metadata in ({"private": False, "full_name": publish_result.CONTROL_REPO},
                         {"private": True, "full_name": "someone/other"},
                         {"full_name": publish_result.CONTROL_REPO}):
            with self.subTest(metadata=metadata):
                with mock.patch("urllib.request.urlopen", return_value=self.stream(metadata)) as opening:
                    with self.assertRaises(ValueError):
                        publish_result.publish(self.response)
                    self.assertEqual(opening.call_count, 1)
                    self.assertNotIn("/contents/", opening.call_args.args[0].full_url)

    def test_wrong_scope_or_endpoint_never_sends_a_request(self):
        for key, value in (("GITHUB_REPOSITORY", "terryvanbelle/battlecode23-vibe"),
                           ("GITHUB_REF", "refs/heads/other"),
                           ("GITHUB_API_URL", "https://untrusted.invalid")):
            with self.subTest(key=key), mock.patch.dict(os.environ, {key: value}), mock.patch("urllib.request.urlopen") as opening:
                with self.assertRaises(ValueError):
                    publish_result.publish(self.response)
                opening.assert_not_called()

    def test_invalid_response_id_cannot_modify_a_different_path(self):
        self.response["id"] = "../other"
        with mock.patch("urllib.request.urlopen") as opening:
            with self.assertRaisesRegex(ValueError, "id"):
                publish_result.publish(self.response)
            opening.assert_not_called()

    def test_new_response_uses_only_expected_private_path(self):
        with mock.patch("urllib.request.urlopen", side_effect=[self.private_metadata(), self.missing(), self.stream({"content": {"sha": "created"}})]) as opening:
            publish_result.publish(self.response)
        self.assertEqual(opening.call_count, 3)
        put = opening.call_args.args[0]
        self.assertEqual(put.get_method(), "PUT")
        self.assertEqual(put.full_url, "https://api.github.com/repos/terryvanbelle/battlecode23-control/contents/responses/job-test-01.json")
        body = json.loads(put.data)
        self.assertEqual(body["branch"], "main")
        self.assertNotIn("sha", body)
        self.assertEqual(json.loads(base64.b64decode(body["content"])), self.response)

    def test_existing_response_is_preserved_without_update(self):
        with mock.patch("urllib.request.urlopen", side_effect=[self.private_metadata(), self.stream({"sha": "old-sha"})]) as opening:
            publish_result.publish(self.response)
        self.assertEqual(opening.call_count, 2)
        lookup = opening.call_args_list[1].args[0]
        self.assertTrue(lookup.full_url.endswith("responses/job-test-01.json?ref=main"))
        self.assertTrue(all(call.args[0].get_method() == "GET" for call in opening.call_args_list))

    def test_api_errors_are_reported_without_token_or_response_body(self):
        error = urllib.error.HTTPError("https://api.github.com/", 403, "test-only-auth-placeholder", None, io.BytesIO(b"private failure body"))
        for prefix in ([], [self.private_metadata()], [self.private_metadata(), self.missing()]):
            with self.subTest(stage=len(prefix)), mock.patch("urllib.request.urlopen", side_effect=prefix + [error]):
                with self.assertRaises(RuntimeError) as failure:
                    publish_result.publish(self.response)
                self.assertIn("403", str(failure.exception))
                self.assertNotIn("test-only-auth-placeholder", str(failure.exception))
                self.assertNotIn("private failure body", str(failure.exception))


if __name__ == "__main__":
    unittest.main()
