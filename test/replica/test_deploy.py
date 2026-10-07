#!/usr/bin/env python3
"""Offline checks of tools/replica/deploy (the replica's host guards and web front). Standard library only.

Run: python3 test/replica/test_deploy.py   (or: python3 -m unittest discover -s test/replica -p 'test_*.py')
The live checks (egress really blocked, HTTPS/401) are tools/replica/deploy/verify.sh, which needs the VM.
"""
import os
import re
import subprocess
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEPLOY = os.path.join(REPO, "tools", "replica", "deploy")
VM_SETUP = os.path.join(DEPLOY, "vm-setup.sh")
HASH = "$2a$14$" + "abcdefghijklmnopqrstuu" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ01234"  # 53 chars after the cost


def run(*args):
    return subprocess.run(["bash", VM_SETUP, *args], capture_output=True, text=True)


def config():
    out = subprocess.run(["bash", "-c", 'source "$1"; set', "_", os.path.join(DEPLOY, "config.sh")],
                         capture_output=True, text=True, check=True).stdout
    return dict(re.findall(r"^([A-Z_0-9]+)=(.*)$", out, re.M))


class DeployScripts(unittest.TestCase):
    def test_bash_syntax(self):
        for name in sorted(os.listdir(DEPLOY)):
            if name.endswith(".sh"):
                r = subprocess.run(["bash", "-n", os.path.join(DEPLOY, name)], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, f"{name}: {r.stderr}")

    def test_config_pins(self):
        c = config()
        self.assertRegex(c["CADDY_SHA256"], r"^[0-9a-f]{64}$")
        self.assertRegex(c["CADDY_SHA512"], r"^[0-9a-f]{128}$")
        self.assertEqual(c["REPLICA_USER"], "bcreplica")
        self.assertEqual(c["REPLICA_PORT"], "8023")
        self.assertEqual(c["PASSWORD_FILE"], "/home/terryvanbelle/.bc23-replica-password")
        self.assertEqual(c["PUBLIC_READ_ONLY"], "1")

    def test_no_secret_or_official_host_in_deploy_files(self):
        pw = os.path.expanduser("~/.bc23-replica-password")
        secret = None
        if os.path.exists(pw):
            with open(pw) as f:
                secret = f.read().strip()
        for name in os.listdir(DEPLOY):
            with open(os.path.join(DEPLOY, name), errors="replace") as f:
                text = f.read()
            for host in ("battlecode.org", "mitbattlecode", "challonge", "mailjet", "googleapis"):
                self.assertNotIn(host, text, f"{name} mentions {host}")
            self.assertNotRegex(text, r"\$2[aby]\$\d\d\$[./A-Za-z0-9]{53}", f"{name} holds a bcrypt hash")
            if secret:
                self.assertNotIn(secret, text, f"{name} holds the password")


class EgressRuleset(unittest.TestCase):
    def setUp(self):
        r = run("print-nft", "999", "8023")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.nft = r.stdout

    def test_only_own_table(self):
        code = "\n".join(l for l in self.nft.splitlines() if not l.lstrip().startswith("#"))
        self.assertNotIn("flush", code)
        self.assertEqual(set(re.findall(r"^table inet (\S+)", self.nft, re.M)), {"bc23_replica_egress"})
        self.assertIn("delete table inet bc23_replica_egress", self.nft)  # idempotent reload

    def test_rules_in_order(self):
        lines = [l.strip() for l in self.nft.splitlines()]
        self.assertIn("meta skuid 999 jump replica", " ".join(lines))
        order = ["ip daddr 169.254.169.254", 'oifname != "lo" counter drop', "ct state established,related accept",
                 "tcp dport { 8023 } accept", "counter drop comment \"no other loopback"]
        pos = [next(i for i, l in enumerate(lines) if l.startswith(o)) for o in order]
        self.assertEqual(pos, sorted(pos))
        self.assertTrue(lines[pos[0]].endswith('"') and " drop " in lines[pos[0]])

    def test_ports_and_bad_input(self):
        self.assertIn("tcp dport { 8023, 8030 }", run("print-nft", "999", "8023 8030").stdout)
        self.assertNotEqual(run("print-nft", "bcreplica", "8023").returncode, 0)
        self.assertNotEqual(run("print-nft", "999", "8023; drop").returncode, 0)

    def test_nftables_service_keeps_the_table(self):
        """nftables.service's 'flush ruleset' must load the egress table in the same transaction (security review)."""
        r = run("print-nft-dropin")
        self.assertEqual(r.returncode, 0, r.stderr)
        parts = dict((b.partition("\n")[0], b.partition("\n")[2]) for b in r.stdout.split("### ")[1:])
        dropin = parts["/etc/systemd/system/nftables.service.d/bc23-replica-egress.conf"]
        combined = parts["/etc/bc23-replica/nftables-with-egress.nft"]
        for line in ("ExecStart=", "ExecStart=/usr/sbin/nft -f /etc/bc23-replica/nftables-with-egress.nft",
                     "ExecReload=", "ExecReload=/usr/sbin/nft -f /etc/bc23-replica/nftables-with-egress.nft"):
            self.assertIn("\n" + line + "\n", dropin)
        self.assertNotIn("ExecStop", dropin)   # stop still flushes; PartOf= then stops the replica (fail closed)
        inc = re.findall(r'^include "([^"]+)"$', combined, re.M)
        self.assertEqual(inc, ["/etc/nftables.conf", "/etc/bc23-replica/egress.nft"])   # ours after the flush

    def test_dbus_policy(self):
        import xml.etree.ElementTree as ET   # never fetches the DTD named in the DOCTYPE
        r = run("print-dbus-policy")
        self.assertEqual(r.returncode, 0, r.stderr)
        root = ET.fromstring(r.stdout)
        self.assertEqual(root.tag, "busconfig")
        pols = root.findall("policy")
        self.assertEqual([p.get("user") for p in pols], ["bcreplica"])
        denied = {d.get("send_destination") for d in pols[0].findall("deny")}
        self.assertIn("org.freedesktop.resolve1", denied)
        self.assertEqual(pols[0].findall("allow"), [])


class Caddyfile(unittest.TestCase):
    def test_render(self):
        r = run("print-caddyfile", "136-86-167-127.sslip.io", HASH)
        self.assertEqual(r.returncode, 0, r.stderr)
        c = r.stdout
        self.assertIn("\n136-86-167-127.sslip.io {\n", c)
        self.assertIn(f"basic_auth {{\n\t\towner {HASH}\n\t}}", c)
        self.assertIn("reverse_proxy 127.0.0.1:8023 {\n\t\theader_up -Authorization", c)
        self.assertIn("admin unix//run/caddy/admin.sock", c)  # no TCP admin API on localhost:2019
        self.assertIn("protocols h1 h2", c)  # no HTTP/3: udp/443 is not opened
        # read-only front: basic_auth precedes respond in Caddy's directive order, so 401 comes before 405
        self.assertIn("@write not method GET HEAD", c)
        self.assertRegex(c, r'respond @write ".*" 405')
        self.assertEqual(c.count("{"), c.count("}"))

    def test_rejects_injection(self):
        for host in ("x.sslip.io {\n}", "evil.io:80", "a b.io", "UPPER.io", "nodot", ""):
            self.assertNotEqual(run("print-caddyfile", host, HASH).returncode, 0, repr(host))
        for h in ("plain", HASH + "\nfoo", HASH[:-1]):
            self.assertNotEqual(run("print-caddyfile", "1-2-3-4.sslip.io", h).returncode, 0, repr(h))



class ServiceUnits(unittest.TestCase):
    """The replica's own systemd units (vm-setup.sh services) honour DEPLOY.md section 4."""

    def setUp(self):
        r = run("print-units")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.units = {}
        for block in r.stdout.split("### ")[1:]:
            name, _, text = block.partition("\n")
            self.units[name] = text

    def test_four_units(self):
        self.assertEqual(sorted(self.units), ["bc23-replica-api.service", "bc23-replica-autoscrim.service",
                                              "bc23-replica-autoscrim.timer", "bc23-replica-worker.service"])

    def test_contract(self):
        for name, text in self.units.items():
            if not name.endswith(".service"):
                continue
            for line in ("Requires=bc23-replica-egress.service", "User=bcreplica", "Group=bcreplica",
                         "Slice=bc23-replica.slice", "UMask=0027", "EnvironmentFile=/etc/bc23-replica/replica.env",
                         "ReadWritePaths=/home/bcreplica/replica", "ProtectSystem=strict", "NoNewPrivileges=yes"):
                self.assertIn("\n" + line + "\n", text, f"{name}: {line}")
            self.assertRegex(text, r"\nAfter=bc23-replica-egress\.service", name)
            self.assertNotIn("MemoryDenyWriteExecute", text)   # the JVM's JIT needs W+X pages
            # security review: no unix-socket path to systemd-resolved
            self.assertIn("\nInaccessiblePaths=-/run/systemd/resolve -/run/dbus/system_bus_socket\n", text, name)

    def test_private_network(self):
        """The worker (and the engines it starts) and autoscrim need no network; the API must stay reachable.
        Exactly the units in the host network namespace refuse to start without the nft table; in a private
        namespace that check cannot work (a '+' ExecStartPre still runs there and sees no table)."""
        guard = "\nExecStartPre=+/bin/sh -c 'exec /usr/sbin/nft list table inet bc23_replica_egress >/dev/null'\n"
        for name in ("bc23-replica-worker.service", "bc23-replica-autoscrim.service"):
            self.assertIn("\nPrivateNetwork=yes\n", self.units[name])
            self.assertNotIn(guard, self.units[name])
        api = self.units["bc23-replica-api.service"]
        self.assertNotIn("PrivateNetwork", api)   # Caddy connects to it
        self.assertIn(guard, api)

    def test_api_loopback_and_worker_stop(self):
        self.assertIn("serve --host 127.0.0.1 --port 8023\n", self.units["bc23-replica-api.service"])
        w = self.units["bc23-replica-worker.service"]
        self.assertIn("run-worker --slots ${REPLICA_SLOTS}", w)
        self.assertIn("KillMode=mixed", w)   # SIGTERM to the worker only, so it requeues its matches itself

    def test_autoscrim_timer_disabled_by_default(self):
        t = self.units["bc23-replica-autoscrim.timer"]
        self.assertIn("OnCalendar=*-*-* 00/4:00:00", t)
        self.assertIn("Unit=bc23-replica-autoscrim.service", t)
        self.assertIn("ExecCondition=/usr/bin/python3 -c", self.units["bc23-replica-autoscrim.service"])
        with open(VM_SETUP) as f:
            script = f.read()
        enables = [l for l in script.splitlines() if "systemctl enable" in l]
        self.assertTrue(enables)
        for l in enables:
            self.assertNotIn("TIMER_AUTOSCRIM", l)
            self.assertNotIn("UNIT_AUTOSCRIM", l)

    def test_env_and_cli(self):
        env = run("print-env").stdout
        for line in ("REPLICA_HOME=/home/bcreplica/replica", "REPLICA_REPO=/home/terryvanbelle/projects/vibe/2023",
                     "JAVA_HOME=/home/terryvanbelle/jdk/jdk8u504-b01",
                     "BENCH_ROOT=/home/terryvanbelle/projects/vibe/bc23-benchmarks", "REPLICA_SLOTS=4"):
            self.assertIn("\n" + line + "\n", env)
        cli = run("print-cli").stdout
        self.assertTrue(cli.startswith("#!/usr/bin/env bash\n"))
        self.assertIn('sudo -u "$RUN_AS" env -i', cli)
        self.assertLess(cli.index('nft list table inet "$NFT_TABLE"'), cli.index("exec sudo"))   # fence first
        r = subprocess.run(["bash", "-n"], input=cli, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=1)
