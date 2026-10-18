#!/usr/bin/env python3
"""
steam-client-block.py — menu-driven blocker for the Steam CLIENT's network.
Games are never blocked.

  sudo ./steam-client-block.py            interactive menu
       ./steam-client-block.py --dry-run  show classification only (no root needed)
  sudo ./steam-client-block.py --status   print current state and exit

How it works
------------
* Steam client processes are moved into cgroup v2 "/sys/fs/cgroup/steamblock".
* An nftables OUTPUT rule drops that cgroup's traffic (loopback stays allowed so
  the client's internal IPC and UI keep working).
* A background thread polls 4x/second: anything Steam launches inherits the
  blocked cgroup, so every process that is NOT a Steam-client binary (games,
  Proton, wine, pressure-vessel, launchers, ...) is moved straight back out to
  "/sys/fs/cgroup/steamallow". Unknown processes are moved out too, so a game
  can never be blocked by accident.
"""

import argparse
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

CG_ROOT   = Path("/sys/fs/cgroup")
BLOCK_CG  = CG_ROOT / "steamblock"
ALLOW_CG  = CG_ROOT / "steamallow"
NFT_TABLE = "steamblock"
POLL      = 0.25  # seconds

# Binaries that ARE the Steam client (these get blocked)
CLIENT_NAMES = {
    "steam", "steam.sh", "steamwebhelper", "steamerrorreporter",
    "steamservice", "steam_monitor", "steamdeck", "steamerrorreporter64",
}
# Path fragments that mark a Steam-client binary
CLIENT_PATH_MARKERS = ("/ubuntu12_32/", "/ubuntu12_64/", "/usr/lib/steam", "/steam/bin/")
# Anything matching these is a GAME (or game tooling) -> never blocked
GAME_MARKERS = ("/steamapps/", "SteamLaunch", "/compatdata/", "/proton", "/Proton")

VERBOSE      = False
_moved_from  = {}     # pid -> original cgroup path
_firewall    = None   # "nft" | "iptables" | None
_stop        = threading.Event()
_sweeper     = None

C_OK, C_BAD, C_DIM, C_HDR, C_OFF = "\033[32m", "\033[31m", "\033[2m", "\033[1m", "\033[0m"
if not sys.stdout.isatty():
    C_OK = C_BAD = C_DIM = C_HDR = C_OFF = ""


def log(*a):
    print("  ", *a, flush=True)


def vlog(*a):
    if VERBOSE:
        log(C_DIM + " ".join(str(x) for x in a) + C_OFF)


def sh(cmd, check=True, inp=None):
    return subprocess.run(cmd, input=inp, text=True, check=check,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


# ---------------------------------------------------------------- proc helpers

def proc_exe(pid):
    try:
        return os.readlink(f"/proc/{pid}/exe")
    except OSError:
        return ""


def proc_comm(pid):
    try:
        return Path(f"/proc/{pid}/comm").read_text().strip()
    except OSError:
        return ""


def proc_cmdline(pid):
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
        return raw.decode("utf-8", "replace").replace("\0", " ").strip()
    except OSError:
        return ""


def proc_cgroup(pid):
    """Unified-hierarchy cgroup path of a pid, e.g. '/user.slice/...'."""
    try:
        for line in Path(f"/proc/{pid}/cgroup").read_text().splitlines():
            parts = line.split(":", 2)
            if parts[0] == "0":
                return parts[2]
    except OSError:
        pass
    return ""


def all_pids():
    try:
        for e in os.scandir("/proc"):
            if e.name.isdigit():
                yield int(e.name)
    except OSError:
        return


def classify(pid):
    """'client' -> block, 'game' -> never block, 'other' -> treated as game (safe)."""
    exe = proc_exe(pid)
    blob = exe + " " + proc_cmdline(pid)

    for m in GAME_MARKERS:
        if m in blob:
            return "game"

    name = os.path.basename(exe) or proc_comm(pid)
    if name in CLIENT_NAMES:
        return "client"
    if any(m in exe for m in CLIENT_PATH_MARKERS):
        return "client"
    return "other"


# -------------------------------------------------------------- cgroup helpers

def ensure_cgroups():
    if not (CG_ROOT / "cgroup.controllers").exists():
        sys.exit("error: cgroup v2 unified hierarchy not mounted at /sys/fs/cgroup")
    for cg in (BLOCK_CG, ALLOW_CG):
        cg.mkdir(exist_ok=True)


def pids_in(cg):
    try:
        return [int(x) for x in (cg / "cgroup.procs").read_text().split()]
    except OSError:
        return []


def move(pid, cg, remember=False):
    if remember and pid not in _moved_from:
        orig = proc_cgroup(pid)
        if orig:
            _moved_from[pid] = orig
    try:
        (cg / "cgroup.procs").write_text(str(pid))
        return True
    except OSError as e:
        vlog(f"could not move pid {pid} -> {cg.name}: {e}")
        return False


# ------------------------------------------------------------------- firewall

NFT_RULESET = f"""
table inet {NFT_TABLE} {{
    chain output {{
        type filter hook output priority filter; policy accept;
        meta oifname "lo" accept
        socket cgroupv2 level 1 "{BLOCK_CG.name}" meta l4proto tcp reject with tcp reset
        socket cgroupv2 level 1 "{BLOCK_CG.name}" counter drop
    }}
}}
"""


def nft_table_present():
    r = sh(["nft", "list", "table", "inet", NFT_TABLE], check=False)
    return r.returncode == 0


def firewall_up():
    global _firewall
    try:
        sh(["nft", "-f", "-"], inp=NFT_RULESET)
        _firewall = "nft"
        vlog("nftables rule installed")
        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        vlog("nft failed:", getattr(e, "stdout", e))

    try:  # fallback: legacy iptables cgroup match
        for tool in ("iptables", "ip6tables"):
            sh([tool, "-I", "OUTPUT", "1", "!", "-o", "lo",
                "-m", "cgroup", "--path", BLOCK_CG.name, "-j", "REJECT"])
        _firewall = "iptables"
        log("iptables rule installed (nftables unavailable)")
        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        log(C_BAD + f"could not install firewall rule: {getattr(e, 'stdout', e)}" + C_OFF)
        return False


def firewall_down():
    sh(["nft", "delete", "table", "inet", NFT_TABLE], check=False)
    for tool in ("iptables", "ip6tables"):
        sh([tool, "-D", "OUTPUT", "!", "-o", "lo",
            "-m", "cgroup", "--path", BLOCK_CG.name, "-j", "REJECT"], check=False)


# ------------------------------------------- tear down already-open sockets
# A socket remembers the cgroup it was created in, so Steam's existing
# long-lived connection would survive the new rule. Kill those once.

def drop_existing_sockets(pids):
    if not pids:
        return
    try:
        out = sh(["ss", "-tanp"], check=False).stdout
    except FileNotFoundError:
        return
    killed = 0
    for line in out.splitlines()[1:]:
        if "ESTAB" not in line or not any(f"pid={p}," in line for p in pids):
            continue
        cols = line.split()
        if len(cols) < 5:
            continue
        local, peer = cols[3], cols[4]
        if peer.startswith("127.") or peer.startswith("[::1]"):
            continue
        if sh(["ss", "-K", "src", local, "dst", peer], check=False).returncode == 0:
            killed += 1
    if killed:
        log(f"tore down {killed} existing Steam connection(s)")
    else:
        vlog("no sockets torn down (kernel may lack INET_DIAG_DESTROY)")


# ----------------------------------------------------------------- core logic

def sweep(announce=False):
    """Move Steam-client procs in; move everything else out."""
    blocked = set(pids_in(BLOCK_CG))

    for pid in blocked:                      # anything not the client -> out
        if classify(pid) != "client":
            name = proc_comm(pid)
            if move(pid, ALLOW_CG) and announce:
                log(f"{C_OK}allowing{C_OFF} pid {pid} ({name}) — not the Steam client")

    newly = []
    for pid in all_pids():                   # client procs not yet blocked -> in
        if pid in blocked:
            continue
        if proc_cgroup(pid) in (f"/{BLOCK_CG.name}", f"/{ALLOW_CG.name}"):
            continue
        if classify(pid) == "client":
            name = proc_comm(pid)
            if move(pid, BLOCK_CG, remember=True):
                newly.append(pid)
                if announce:
                    log(f"{C_BAD}blocking{C_OFF} pid {pid} ({name})")
    if newly:
        drop_existing_sockets(newly)
    return newly


def _sweep_loop():
    while not _stop.is_set():
        try:
            sweep()
        except Exception as e:               # never let the sweeper die silently
            vlog("sweep error:", e)
        _stop.wait(POLL)


def is_blocked():
    return _firewall is not None or (BLOCK_CG.exists() and nft_table_present())


def do_block():
    global _sweeper
    if is_blocked():
        log("already blocked")
        return
    ensure_cgroups()
    if not firewall_up():
        return
    n = sweep(announce=True)
    _stop.clear()
    _sweeper = threading.Thread(target=_sweep_loop, daemon=True)
    _sweeper.start()
    if n:
        log(f"{C_BAD}Steam client is now offline.{C_OFF} Games keep full network access.")
    else:
        log(f"{C_BAD}Rule active.{C_OFF} No Steam client running yet — "
            "it will be blocked as soon as it starts.")


def do_unblock():
    global _firewall, _sweeper
    if not is_blocked():
        log("not currently blocked")
        return
    _stop.set()
    if _sweeper and _sweeper.is_alive():
        _sweeper.join(timeout=2)
    _sweeper = None
    firewall_down()
    _firewall = None
    for cg in (BLOCK_CG, ALLOW_CG):          # put processes back where they were
        for pid in pids_in(cg):
            dest = _moved_from.get(pid)
            target = None
            if dest and dest not in ("/", f"/{BLOCK_CG.name}", f"/{ALLOW_CG.name}"):
                cand = CG_ROOT / dest.lstrip("/")
                if (cand / "cgroup.procs").exists():
                    target = cand
            move(pid, target or CG_ROOT)
    _moved_from.clear()
    for cg in (BLOCK_CG, ALLOW_CG):
        try:
            cg.rmdir()
        except OSError as e:
            vlog(f"could not remove {cg}: {e}")
    log(f"{C_OK}Steam client network restored.{C_OFF} "
        "It may take a moment to reconnect, or click Steam > 'Go Online'.")


def do_status():
    if os.geteuid() != 0:
        print(f"\n  {C_DIM}(not root — cannot read the firewall, state may read "
              f"as 'not blocked'){C_OFF}")
    on = is_blocked()
    print(f"\n  state      : {(C_BAD + 'BLOCKED' + C_OFF) if on else (C_OK + 'not blocked' + C_OFF)}")
    print(f"  nft table  : {'present' if nft_table_present() else 'absent'}")
    print(f"  sweeper    : {'running' if _sweeper and _sweeper.is_alive() else 'stopped'}")
    if BLOCK_CG.exists():
        b = pids_in(BLOCK_CG)
        print(f"  blocked    : {len(b)} process(es)")
        for pid in b:
            print(f"               {pid:>7}  {proc_comm(pid)}")
        print(f"  exempted   : {len(pids_in(ALLOW_CG))} process(es) moved out (games etc.)")
    print()


def do_dry_run():
    rows = []
    for pid in sorted(all_pids()):
        exe, cmd = proc_exe(pid), proc_cmdline(pid)
        low = (exe + cmd).lower()
        if "steam" not in low and "proton" not in low:
            continue
        rows.append((classify(pid), pid, os.path.basename(exe) or proc_comm(pid),
                     (exe or cmd)[:70]))
    if not rows:
        print("\n  no Steam-related processes found\n")
        return
    order = {"client": 0, "game": 1, "other": 2}
    print()
    for verdict, pid, name, path in sorted(rows, key=lambda r: (order[r[0]], r[1])):
        if verdict == "client":
            print(f"  {C_BAD}BLOCK{C_OFF}  {pid:>7}  {name:<22} {C_DIM}{path}{C_OFF}")
        else:
            print(f"  {C_OK}allow{C_OFF}  {pid:>7}  {name:<22} {C_DIM}{path}{C_OFF}")
    print(f"\n  {C_DIM}BLOCK = Steam client (loses network).  "
          f"allow = untouched.{C_OFF}\n")


# ---------------------------------------------------------------------- menu

MENU = f"""
{C_HDR}  Steam client network blocker{C_OFF}
  1) Block Steam client
  2) Unblock Steam client
  3) Status
  4) Show what would be blocked (dry run)
  5) Quit
"""


def menu():
    while True:
        state = (C_BAD + "BLOCKED" + C_OFF) if is_blocked() else (C_OK + "not blocked" + C_OFF)
        print(MENU)
        try:
            choice = input(f"  [{state}] choice> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            choice = "5"

        if choice == "1":
            do_block()
        elif choice == "2":
            do_unblock()
        elif choice == "3":
            do_status()
        elif choice == "4":
            do_dry_run()
        elif choice in ("5", "q", "quit", "exit"):
            if is_blocked():
                print(f"\n  {C_BAD}Steam is still blocked.{C_OFF} If you quit while blocked, "
                      "the sweeper stops\n  and a game Steam launches later could be caught "
                      "by the rule.")
                try:
                    ans = input("  Unblock before quitting? [Y/n] ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    ans = "y"
                if ans in ("", "y", "yes"):
                    do_unblock()
                else:
                    log(f"{C_BAD}left blocked{C_OFF} — run this script again and "
                        "choose 2 to undo")
            return
        else:
            log("pick 1-5")


def _on_signal(signum, frame):
    print()
    if is_blocked():
        log("signal received — unblocking before exit")
        do_unblock()
    sys.exit(0)


def main():
    global VERBOSE
    ap = argparse.ArgumentParser(
        description="Block the Steam client's network access, never the games.")
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("-n", "--dry-run", action="store_true",
                    help="print how each Steam-related process is classified, change nothing")
    ap.add_argument("-s", "--status", action="store_true", help="print state and exit")
    args = ap.parse_args()
    VERBOSE = args.verbose

    if args.dry_run:
        do_dry_run()
        return
    if args.status:
        do_status()
        return

    if os.geteuid() != 0:
        sys.exit("error: must run as root — try: sudo " + sys.argv[0])

    for s in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(s, _on_signal)

    if BLOCK_CG.exists() or nft_table_present():
        log(f"{C_BAD}found leftover state from a previous run{C_OFF} "
            "— choose 2 to clean it up")
    menu()


if __name__ == "__main__":
    main()
