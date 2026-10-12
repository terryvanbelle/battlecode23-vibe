#!/usr/bin/env bash
# Install a private-repository GitHub worker under the existing driver account.
# This never pulls, resets, cleans, or synchronizes the live Battlecode checkout.
set +x
set -euo pipefail
umask 077

CONTROL_URL='https://github.com/terryvanbelle/battlecode23-control'
RUNNER_NAME='claude-driver-bc23'
RUNNER_VERSION='2.338.0'
RUNNER_SHA256='af4b794c1bc41d73d40535e3fe092a39f9679cd8d965954c2aca25a05ca41d32'
ARCHIVE="actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"
worker_repo="${BC23_WORKER_REPO:-$HOME/projects/vibe/2023}"
runner_dir="${BC23_RUNNER_DIR:-$HOME/actions-runner-bc23-control}"
stage_dir=''
preflight_dir=''

fail() { printf 'web worker setup: %s\n' "$*" >&2; exit 1; }
cleanup() {
  if [[ -n "$stage_dir" ]]; then rm -rf -- "$stage_dir"; fi
  if [[ -n "$preflight_dir" ]]; then rm -rf -- "$preflight_dir"; fi
}
trap cleanup EXIT

[[ "$(id -u)" != 0 ]] || fail 'Run as the existing driver account, without sudo.'
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || fail 'This installer requires Linux x86_64.'
[[ "$(hostname -s)" == claude-driver ]] || fail 'Run this installer on claude-driver, not a game VM or another machine.'
for utility in python3 git curl sha256sum tar mktemp sudo systemctl stat; do
  command -v "$utility" >/dev/null || fail "Required command is missing: $utility"
done
[[ "$worker_repo" == /* && "$runner_dir" == /* ]] || fail 'Checkout and runner paths must be absolute.'
[[ -d "$worker_repo" ]] || fail 'The existing Battlecode checkout was not found. Use its existing owner account.'
repo_top="$(git -C "$worker_repo" rev-parse --show-toplevel 2>/dev/null)" || fail 'The Battlecode path is not a Git checkout.'
[[ "$(cd "$worker_repo" && pwd -P)" == "$(cd "$repo_top" && pwd -P)" ]] || fail 'BC23_WORKER_REPO must name the checkout root.'
[[ "$(stat -c %u "$worker_repo")" == "$(id -u)" ]] || fail 'Use the account that owns the existing checkout.'
python3 - "$worker_repo" "$runner_dir" <<'PY'
from pathlib import Path
import sys
repo, runner = (Path(value).resolve() for value in sys.argv[1:])
if repo == runner or repo in runner.parents or runner in repo.parents:
    raise SystemExit("The runner installation and live checkout must use separate directories.")
PY
origin="$(git -C "$worker_repo" config --get remote.origin.url)" || fail 'The checkout has no origin remote.'
case "$origin" in
  https://github.com/terryvanbelle/battlecode23-vibe|https://github.com/terryvanbelle/battlecode23-vibe.git|git@github.com:terryvanbelle/battlecode23-vibe|git@github.com:terryvanbelle/battlecode23-vibe.git|ssh://git@github.com/terryvanbelle/battlecode23-vibe|ssh://git@github.com/terryvanbelle/battlecode23-vibe.git) ;;
  *) fail 'The checkout origin is not terryvanbelle/battlecode23-vibe.' ;;
esac
unset origin
[[ ! -L "$runner_dir" ]] || fail 'The runner directory must not be a symlink.'
if [[ -e "$runner_dir" ]]; then
  [[ -d "$runner_dir" ]] || fail 'The runner path is not a directory.'
  [[ "$(stat -c %u "$runner_dir")" == "$(id -u)" ]] || fail 'The runner directory belongs to another account.'
fi

# A public repository is unsafe for this account's VM credentials. A 404 can
# mean private or absent; successful registration later proves existence.
# Disable curlrc so this probe is genuinely unauthenticated.
preflight_dir="$(mktemp -d "${TMPDIR:-/tmp}/bc23-runner-preflight.XXXXXX")"
http_status="$(curl --disable --silent --show-error --location --retry 3 \
  --proto '=https' --tlsv1.2 --max-time 30 \
  --output "$preflight_dir/repository.json" --write-out '%{http_code}' \
  'https://api.github.com/repos/terryvanbelle/battlecode23-control')" \
  || fail 'Unable to check control-repository visibility. No registration was attempted.'
case "$http_status" in
  404) ;;
  200) fail 'The control repository is publicly visible. Make battlecode23-control private before proceeding.' ;;
  *) fail "Unexpected GitHub visibility-check response ($http_status). No registration was attempted." ;;
esac

if [[ ! -f "$runner_dir/.runner" ]]; then
  [[ ! -e "$runner_dir/.credentials" && ! -e "$runner_dir/.service" ]] || fail 'Incomplete runner registration exists; refusing to overwrite it.'
  if [[ ! -f "$runner_dir/.bc23-bootstrap-package" ]]; then
    # Download and verify in a separate staging directory before extraction.
    # Existing unfamiliar contents are preserved instead of overwritten.
    if [[ -d "$runner_dir" ]]; then
      [[ -z "$(find "$runner_dir" -mindepth 1 -maxdepth 1 -print -quit)" ]] || fail 'The runner directory contains an unfamiliar installation.'
    fi
    mkdir -p -- "$(dirname "$runner_dir")"
    stage_dir="$(mktemp -d "${runner_dir}.install.XXXXXX")"
    curl --disable --fail --location --retry 3 --proto '=https' --tlsv1.2 --max-time 300 \
      --output "$stage_dir/$ARCHIVE" \
      "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${ARCHIVE}"
    printf '%s  %s\n' "$RUNNER_SHA256" "$stage_dir/$ARCHIVE" | sha256sum --check --status \
      || fail 'Runner checksum mismatch. Nothing was extracted or installed.'
    mkdir "$stage_dir/unpacked"
    tar --extract --gzip --file "$stage_dir/$ARCHIVE" --directory "$stage_dir/unpacked" --no-same-owner --no-same-permissions
    [[ -x "$stage_dir/unpacked/config.sh" ]] || fail 'The verified archive has no executable config.sh.'
    printf '%s %s\n' "$RUNNER_VERSION" "$RUNNER_SHA256" > "$stage_dir/unpacked/.bc23-bootstrap-package"
    if [[ -d "$runner_dir" ]]; then rmdir -- "$runner_dir"; fi
    mv -- "$stage_dir/unpacked" "$runner_dir"
  else
    [[ "$(cat "$runner_dir/.bc23-bootstrap-package")" == "$RUNNER_VERSION $RUNNER_SHA256" ]] || fail 'An unfamiliar bootstrap package is present.'
    [[ -x "$runner_dir/config.sh" ]] || fail 'The previous runner installation is incomplete.'
  fi
  printf '%s\n' \
    'Open the PRIVATE battlecode23-control repository on GitHub:' \
    'Settings > Actions > Runners > New self-hosted runner > Linux / x64.' \
    'Copy its one-hour registration token into the masked token prompt below.' \
    'Do not put that token in chat or a shell command. Accept the default runner group.'
  (
    cd "$runner_dir"
    # Omitting --token keeps credentials out of arguments and shell history.
    ./config.sh --url "$CONTROL_URL" --name "$RUNNER_NAME" \
      --no-default-labels --labels bc23-driver --work _work
  ) || fail "Runner registration failed. If dependencies are missing, run: sudo '$runner_dir/bin/installdependencies.sh', then repeat this installer."
fi

[[ -s "$runner_dir/.credentials" && -x "$runner_dir/svc.sh" ]] || fail 'Runner credentials or service helper are missing; refusing to overwrite registration.'
# .runner is non-secret metadata; never read the credential files.
python3 - "$runner_dir/.runner" "$CONTROL_URL" "$RUNNER_NAME" <<'PY'
import json, sys
try:
    # GitHub runner's IOUtil.SaveObject uses Encoding.UTF8 with a BOM.
    # utf-8-sig accepts both that format and older plain UTF-8 metadata.
    with open(sys.argv[1], encoding="utf-8-sig") as source:
        config = json.load(source)
    valid = (config.get("gitHubUrl", "").rstrip("/") == sys.argv[2]
             and config.get("agentName") == sys.argv[3]
             and config.get("workFolder") == "_work")
except (OSError, ValueError, TypeError, AttributeError):
    valid = False
if not valid:
    raise SystemExit("Existing runner metadata does not match the private control repository; refusing to change it.")
PY
cd "$runner_dir"
if [[ ! -f .service ]]; then
  sudo ./svc.sh install "$(id -un)"
fi
[[ -f .service ]] || fail 'The service installer did not create service metadata.'
service_name="$(cat .service)"
[[ "$service_name" =~ ^actions\.runner\.[A-Za-z0-9_.-]+\.service$ ]] || fail 'Unrecognized existing service metadata.'
service_user="$(systemctl show "$service_name" --property=User --value)"
[[ "$service_user" == "$(id -un)" ]] || fail 'The existing runner service runs as another account or is not installed; refusing to change it.'
sudo ./svc.sh start
sudo ./svc.sh status
printf '%s\n' 'Setup complete. Report the runner status in the web chat; ongoing commands will come from there.'
