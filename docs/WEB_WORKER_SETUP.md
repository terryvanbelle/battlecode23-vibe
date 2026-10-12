# One-time setup: control claude-driver from the web chat

The web chat remains the controller. GitHub delivers jobs to a worker service on `claude-driver`, which already has
access to `battlecode-dev`. This setup uses outbound HTTPS and does not require Tailscale, cloud VPN settings, new SSH
keys, or a CLI agent. It has been tested with local fixtures; the real VM connection is not yet verified.

## 1. Create and connect the private control repository

Open https://github.com/new while signed in as **terryvanbelle**.

- Name: **battlecode23-control**.
- Visibility: **Private**.
- Select **Add a README**, then create the repository.
- Keep it private and restrict write access to yourself and the intended ChatGPT/Codex GitHub connection. Its writers
  can run commands as your existing driver account.

In the existing ChatGPT/Codex GitHub connection, include this new repository. If your GitHub App installation uses
selected repositories, open https://github.com/settings/installations, choose **Configure** for that connection,
add `battlecode23-control`, and save. If it already uses all repositories, no selection change is needed.

Return to the web chat and report that the repository is created and connected. The web agent will verify private
access and publish the worker files plus a read-only inspection request. Do not copy the workflow into the public
`battlecode23-vibe` repository. No registration token belongs in chat.

## 2. Open the existing driver's shell

Use the terminal where your normal GCloud command works:

```bash
gcloud compute ssh claude-driver --zone=us-west1-b --project=tvanbelle-vibecode
```

At the resulting VM shell prompt, use the existing account that owns `~/projects/vibe/2023`. Run the following in
the shell, not inside a Codex or Claude prompt. You do not need to stop the tmux session or existing training jobs.

```bash
setup_file=$(mktemp /tmp/bc23-web-worker.XXXXXX)
curl --fail --location --proto '=https' --tlsv1.2 \
  'https://raw.githubusercontent.com/terryvanbelle/battlecode23-vibe/codex/continue-bc23/tools/web-worker/bootstrap.sh' \
  --output "$setup_file"
printf '%s  %s\n' \
  'a8e92fe0f62affa2b07250503b2ffa16113fb9ff6f9bbc175324fbf382ea3b83' \
  "$setup_file" | sha256sum --check && bash "$setup_file"
```

The checksum must report **OK**. The installer checks the hostname, account, existing checkout origin, and repository
visibility. It downloads a pinned GitHub runner, verifies its checksum before extraction, and installs it separately
in `~/actions-runner-bc23-control`. It does not update or synchronize the live Battlecode checkout.

If it says the checkout is missing, stop and report the message. Do not clone a replacement or run the installer as
root. If the known checkout has a different path, the web agent can supply the exact non-secret path override.

## 3. Register the worker when the installer asks

In your browser open:

https://github.com/terryvanbelle/battlecode23-control/settings/actions/runners/new

Choose **Linux**, **x64**. In the displayed configuration command, copy only the value after `--token`. GitHub creates
a registration token valid for one hour. Paste it into the installer's **masked token prompt in the VM terminal**;
do not paste the complete GitHub command, put the token in shell history, or send it to chat.

Accept the default runner group if asked. The installer supplies the runner name, label and work directory. If asked
to replace an existing runner, decline and report it here. The service install/start may ask for your normal sudo
password in the terminal; do not send it to chat.

If GitHub reports missing system dependencies, the installer prints the exact dependency installation command.
Run that command, then repeat the setup block. The installer preserves a completed registration on a retry.

When the service reports running, open the repository's **Settings > Actions > Runners**. The runner
**claude-driver-bc23** should appear **Idle** or **Active** with label **bc23-driver**. Report that status here. All
subsequent work stays in this web chat. No VM credential files are copied to this environment.

## First inspection and ongoing operation

The first request uses `tools/web-worker/inspect_driver.py`: hostname/account, checkout status and recent commit
subjects, disk space, program locations, own ladder state, and engine checksum. It does not read opponent code,
credentials, start games, update code, or stop processes. The web agent must verify its request ID and job hash in the
returned response before trusting the connection.

Only the exact private control repo, main-branch pushes and authorized actor can trigger the workflow. Do not broaden
these guards if a job is skipped. The web agent will inspect the real push actor and, if needed, give the exact value
for repository variable `BC23_CONTROLLER_ACTOR`.

Requests specify a unique ID, SHA-256 of the job, and a deadline of at most 30 minutes. Jobs execute in the original
driver checkout with existing file-based GCP credentials, while Actions service tokens are excluded from job
environments. Logs are bounded and common token forms are redacted; jobs must still avoid printing credentials.
Only wrapper-owned result metadata and the two bounded log files are uploaded. The response is written to
`responses/<request-id>.json` in the private repository; result commits do not trigger another job.
Only request-file changes trigger execution; helper updates do not replay the previous job. The runner permanently
reserves each request ID before execution and preserves the first response. Use a fresh ID for retries, including
read-only jobs; Actions' rerun button does not rerun a reserved request.

Long-running training belongs on `battlecode-dev` through the established queue/replica tools. Driver jobs should
inspect, submit and poll that work rather than run volume games on the driver. Use one registered driver runner and
one authoritative project checkout. Before adopting changes, follow the live-state preservation steps in
[CONTINUATION.md](CONTINUATION.md) and run the official-jar test suite on the driver.

To disconnect later, stop the private runner service from its directory with `sudo ./svc.sh stop` and remove that
repository-scoped runner in GitHub settings. Existing Battlecode jobs and VM SSH configuration are independent.
