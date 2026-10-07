#!/usr/bin/env bash
# Create or rotate the HTTP basic-auth password of the replica web site (login "owner"). Run on the driver.
#   tools/replica/deploy/set-password.sh            reuse the driver's password file when it exists, else generate one
#   tools/replica/deploy/set-password.sh --rotate   always generate a new one (the old one stops working at once)
# The clear password (20 random letters and digits) is kept in /home/terryvanbelle/.bc23-replica-password, mode 600,
# on the driver AND on the VM. The Caddyfile holds only its bcrypt hash. The password travels on ssh stdin, never on a
# command line, and is never printed.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"
# shellcheck source=../../vm.sh
source "$HERE/../../vm.sh"; IP="${IP:-10.138.0.3}"
[ "$(hostname -s)" != "$BC_VM" ] || { echo "set-password: run this on the driver" >&2; exit 1; }

rotate=0; [ "${1:-}" = --rotate ] && rotate=1
umask 077
if [ $rotate = 1 ] || [ ! -s "$PASSWORD_FILE" ]; then
  python3 -c 'import secrets, string, sys
a = string.ascii_letters + string.digits
print("".join(secrets.choice(a) for _ in range(int(sys.argv[1]))))' "$PASSWORD_LEN" > "$PASSWORD_FILE.new"
  mv -f "$PASSWORD_FILE.new" "$PASSWORD_FILE"
  echo "generated a new password"
fi
chmod 600 "$PASSWORD_FILE"
gssh "umask 077; cat > '$PASSWORD_FILE.new' && chmod 600 '$PASSWORD_FILE.new' && mv -f '$PASSWORD_FILE.new' '$PASSWORD_FILE'" \
  < "$PASSWORD_FILE"
gssh "sudo $LIB_DIR/vm-setup.sh password < '$PASSWORD_FILE'"
echo "password for '$OWNER_LOGIN' is in $PASSWORD_FILE (driver and VM, mode 600); Caddy has only its bcrypt hash"
