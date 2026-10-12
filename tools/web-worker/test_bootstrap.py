"""Exercise installer refusal and resume paths without network, sudo, or systemd."""
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("bootstrap.sh")
PIN = "af4b794c1bc41d73d40535e3fe092a39f9679cd8d965954c2aca25a05ca41d32"
CONTROL = "https://github.com/terryvanbelle/battlecode23-control"
SERVICE = "actions.runner.terryvanbelle-battlecode23-control.claude-driver-bc23.service"


class BootstrapTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="bc23-bootstrap-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "live-checkout"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "remote", "add", "origin",
                        "https://github.com/terryvanbelle/battlecode23-vibe.git"], check=True)
        self.runner = self.root / "runner"
        self.events = self.root / "events"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.archive = self.root / "fixture.tar.gz"
        config = """#!/usr/bin/env bash
set -euo pipefail
[[ "$*" != *--token* ]]
printf 'register\\n' >> "$TEST_EVENTS"
python3 - <<'PY'
import json
from pathlib import Path
Path('.runner').write_text(json.dumps({'gitHubUrl': 'https://github.com/terryvanbelle/battlecode23-control', 'agentName': 'claude-driver-bc23', 'workFolder': '_work'}), encoding='utf-8-sig')
Path('.credentials').write_text('test-only placeholder')
PY
"""
        service = """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "$TEST_EVENTS"
if [[ "$1" == install ]]; then
  [[ "${2:-}" == driver ]]
  printf '%s\\n' 'actions.runner.terryvanbelle-battlecode23-control.claude-driver-bc23.service' > .service
fi
"""
        with tarfile.open(self.archive, "w:gz") as archive:
            for name, content in (("config.sh", config), ("svc.sh", service)):
                data = content.encode()
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mode = 0o755
                archive.addfile(info, io.BytesIO(data))
        # Substitute only the test fixture's hash in an isolated copy. Real
        # sha256sum and tar then test the verification-before-extraction order.
        self.script = self.root / "bootstrap.sh"
        self.script.write_text(SCRIPT.read_text().replace(PIN, hashlib.sha256(self.archive.read_bytes()).hexdigest()))
        self.env = os.environ.copy()
        self.env.update(PATH=str(self.bin) + os.pathsep + self.env["PATH"],
                        BC23_WORKER_REPO=str(self.repo), BC23_RUNNER_DIR=str(self.runner),
                        TEST_ARCHIVE=str(self.archive), TEST_EVENTS=str(self.events),
                        TEST_UID="1000", TEST_HTTP_STATUS="404", TEST_SERVICE_USER="driver")
        self.stub("id", "print(os.environ['TEST_UID'] if sys.argv[1] == '-u' else 'driver')")
        self.stub("stat", "print(os.environ['TEST_UID'])")
        self.stub("uname", "print('Linux' if sys.argv[1] == '-s' else 'x86_64')")
        self.stub("hostname", "print(os.environ.get('TEST_HOSTNAME', 'claude-driver'))")
        self.stub("systemctl", "print(os.environ['TEST_SERVICE_USER'])")
        self.stub("sudo", "raise SystemExit(subprocess.call(sys.argv[1:]))")
        self.stub("curl", """
args = sys.argv[1:]
destination = Path(args[args.index('--output') + 1])
if args[-1].startswith('https://api.github.com/'):
    destination.write_text('{}')
    print(os.environ['TEST_HTTP_STATUS'], end='')
else:
    with open(os.environ['TEST_EVENTS'], 'a') as log:
        log.write('download\\n')
    destination.write_bytes(Path(os.environ['TEST_ARCHIVE']).read_bytes())
""")

    def stub(self, name, body):
        path = self.bin / name
        path.write_text(f"#!{sys.executable}\nimport os, sys, subprocess\nfrom pathlib import Path\n" + body + "\n")
        path.chmod(0o755)

    def run_setup(self):
        return subprocess.run(["bash", str(self.script)], env=self.env, capture_output=True, text=True)

    def operations(self):
        return self.events.read_text().splitlines() if self.events.exists() else []

    def registered_runner(self, url=CONTROL, bom=False):
        self.runner.mkdir()
        with tarfile.open(self.archive) as archive:
            archive.extractall(self.runner, filter="data")
        (self.runner / ".runner").write_text(json.dumps(dict(gitHubUrl=url, agentName="claude-driver-bc23", workFolder="_work")),
                                              encoding="utf-8-sig" if bom else "utf-8")
        (self.runner / ".credentials").write_text("test-only placeholder")
        (self.runner / ".service").write_text(SERVICE + "\n")

    def test_release_pin_is_present(self):
        self.assertIn("RUNNER_VERSION='2.338.0'", SCRIPT.read_text())
        self.assertIn("RUNNER_SHA256='" + PIN + "'", SCRIPT.read_text())

    def test_workflow_limits_the_runner_and_artifact_boundary(self):
        workflow = SCRIPT.with_name("control-workflow.yml").read_text()
        self.assertIn("github.event.repository.private == true", workflow)
        self.assertIn("github.repository == 'terryvanbelle/battlecode23-control'", workflow)
        self.assertIn("github.ref == 'refs/heads/main'", workflow)
        self.assertIn("github.event_name == 'push'", workflow)
        self.assertIn("github.actor == 'terryvanbelle'", workflow)
        self.assertIn("runs-on: bc23-driver", workflow)
        self.assertIn("timeout-minutes: 40", workflow)
        self.assertNotIn("pull_request", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("id: execute", workflow)
        self.assertIn("if: always() && steps.execute.outputs.export_ready == 'true'", workflow)
        self.assertIn("BC23_WORKER_STATE: ${{ runner.workspace }}/.bc23-worker-state", workflow)
        self.assertIn("BC23_WORKER_EXPORT_READY: ${{ steps.execute.outputs.export_ready }}", workflow)
        trigger = workflow.split("    paths:\n", 1)[1].split("\npermissions:", 1)[0]
        self.assertEqual([line.strip() for line in trigger.splitlines() if line.strip()], ["- jobs/request.json"])
        self.assertIn("actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1", workflow)
        self.assertIn("actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9", workflow)
        artifact = workflow.split("path: |", 1)[1].split("if-no-files-found:", 1)[0]
        paths = [line.strip() for line in artifact.splitlines() if line.strip()]
        self.assertEqual(len(paths), 3)
        self.assertEqual({path.rsplit("/", 1)[1] for path in paths}, {"result.json", "stdout.txt", "stderr.txt"})
        self.assertTrue(all("${{ runner.temp }}/bc23-worker-results-" in path for path in paths))

    def test_root_is_rejected_without_download(self):
        self.env["TEST_UID"] = "0"
        result = self.run_setup()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("without sudo", result.stderr)
        self.assertEqual(self.operations(), [])
        self.assertFalse(self.runner.exists())

    def test_wrong_checkout_is_rejected_without_download(self):
        subprocess.run(["git", "-C", str(self.repo), "remote", "set-url", "origin", "https://github.com/someone/other.git"], check=True)
        result = self.run_setup()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checkout origin", result.stderr)
        self.assertEqual(self.operations(), [])

    def test_game_vm_is_rejected_without_download(self):
        self.env["TEST_HOSTNAME"] = "battlecode-dev"
        result = self.run_setup()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a game VM", result.stderr)
        self.assertEqual(self.operations(), [])

    def test_runner_inside_live_checkout_is_rejected(self):
        self.env["BC23_RUNNER_DIR"] = str(self.repo / "runner")
        result = self.run_setup()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("separate directories", result.stderr)
        self.assertEqual(self.operations(), [])

    def test_public_or_unknown_visibility_is_rejected(self):
        for status in ("200", "403", "500"):
            with self.subTest(status=status):
                self.env["TEST_HTTP_STATUS"] = status
                result = self.run_setup()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.operations(), [])
                self.assertFalse(self.runner.exists())

    def test_checksum_failure_never_extracts_or_registers(self):
        self.archive.write_bytes(b"corrupted download")
        result = self.run_setup()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checksum mismatch", result.stderr)
        self.assertEqual(self.operations(), ["download"])
        self.assertFalse(self.runner.exists())
        self.assertEqual(list(self.root.glob("runner.install.*")), [])

    def test_install_and_repeat_preserve_checkout_and_registration(self):
        dirty = self.repo / "uncommitted-work.txt"
        dirty.write_text("keep this")
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.operations(), ["download", "register", "install driver", "start", "status"])
        metadata = (self.runner / ".runner").read_bytes()
        self.assertTrue(metadata.startswith(b"\xef\xbb\xbf"))
        credentials = (self.runner / ".credentials").read_bytes()
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.operations(), ["download", "register", "install driver", "start", "status", "start", "status"])
        self.assertEqual((self.runner / ".runner").read_bytes(), metadata)
        self.assertEqual((self.runner / ".credentials").read_bytes(), credentials)
        self.assertEqual(dirty.read_text(), "keep this")

    def test_bom_registration_resumes_service_setup_without_reregistering(self):
        # The pinned .NET runner writes UTF-8 metadata with a byte order mark.
        # Reproduce a completed registration stopped before service install.
        self.registered_runner(bom=True)
        (self.runner / ".service").unlink()
        metadata = (self.runner / ".runner").read_bytes()
        credentials = (self.runner / ".credentials").read_bytes()
        self.assertTrue(metadata.startswith(b"\xef\xbb\xbf"))
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.operations(), ["install driver", "start", "status"])
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.operations(), ["install driver", "start", "status", "start", "status"])
        self.assertEqual((self.runner / ".runner").read_bytes(), metadata)
        self.assertEqual((self.runner / ".credentials").read_bytes(), credentials)

    def test_bom_wrong_identity_and_malformed_metadata_are_preserved(self):
        self.registered_runner(bom=True)
        valid = dict(gitHubUrl=CONTROL, agentName="claude-driver-bc23", workFolder="_work")
        invalid = [
            json.dumps(dict(valid, gitHubUrl="https://github.com/someone/other")),
            json.dumps(dict(valid, agentName="another-runner")),
            json.dumps(dict(valid, workFolder="another-work-directory")),
            "{malformed json",
            "[]",
            "null",
        ]
        for metadata in invalid:
            with self.subTest(metadata=metadata):
                (self.runner / ".runner").write_text(metadata, encoding="utf-8-sig")
                before = (self.runner / ".runner").read_bytes()
                result = self.run_setup()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("metadata does not match", result.stderr)
                self.assertEqual(self.operations(), [])
                self.assertEqual((self.runner / ".runner").read_bytes(), before)

    def test_registered_other_repository_is_preserved_and_rejected(self):
        self.registered_runner("https://github.com/someone/other")
        before = (self.runner / ".runner").read_bytes()
        result = self.run_setup()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("metadata does not match", result.stderr)
        self.assertEqual(self.operations(), [])
        self.assertEqual((self.runner / ".runner").read_bytes(), before)

    def test_service_under_another_account_is_not_started(self):
        self.registered_runner()
        self.env["TEST_SERVICE_USER"] = "another-user"
        result = self.run_setup()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("another account", result.stderr)
        self.assertEqual(self.operations(), [])

    def test_unfamiliar_directory_is_not_overwritten(self):
        self.runner.mkdir()
        marker = self.runner / "existing-file"
        marker.write_text("preserve")
        result = self.run_setup()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unfamiliar installation", result.stderr)
        self.assertEqual(self.operations(), [])
        self.assertEqual(marker.read_text(), "preserve")


if __name__ == "__main__":
    unittest.main()
