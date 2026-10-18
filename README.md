# CachyOS Issues & Fixes

A personal reference of issues I ran into on CachyOS and how I fixed them - kept
here so I don't have to rediscover the same solutions twice.

---

## Issues & Solutions

<details>
<summary><strong>1. Run Cachy-Update in a specific terminal emulator (e.g., Kitty)</strong></summary>

**The issue:**
`gio` launches the `arch-update` terminal UI when the systray applet is clicked, but
it only recognises a short hardcoded list of terminal emulators. If your terminal isn't
on that list, clicking the applet does nothing. If multiple terminals are installed, you
may also want to pin which one is used.

**The fix:**
Configure the preferred terminal through `xdg-terminal-exec`.

**Step 1 — Install `xdg-terminal-exec` from the AUR:**
```bash
yay -S xdg-terminal-exec   # or: paru -S xdg-terminal-exec
```

**Step 2 — Point it at your terminal's `.desktop` entry:**
```bash
echo "kitty.desktop" > ~/.config/xdg-terminals.list
```

Not sure of the exact `.desktop` filename? Find it with:
```bash
find /usr/share/applications ~/.local/share/applications -name "*.desktop" 2>/dev/null | grep -i kitty
```

**Step 3 — Done.**
Next time you click the systray applet, `gio` delegates terminal resolution to
`xdg-terminal-exec`, which reads `~/.config/xdg-terminals.list` and launches Kitty.

**Notes:**
- The file accepts multiple entries (one per line) in order of preference — acts as
  a fallback chain.
- To switch terminals later, just replace the entry (e.g. `Alacritty.desktop`,
  `foot.desktop`).

**Reference:**
- [CachyOS cachy-update documentation](https://github.com/CachyOS/cachy-update#run-cachy-update-in-a-specific-terminal-emulator)

</details>

<details>
<summary><strong>2. Add your terminal to CachyOS tools (e.g., CachyOS Hello, limine-snapper-restore)</strong></summary>

**The issue:**
Some CachyOS tools — CachyOS Hello, `limine-snapper-restore`, `limine-snapper-sync` —
have a hardcoded allowlist of terminal emulators (e.g. `gnome-terminal`, `konsole`,
`foot`). If your terminal isn't on the list, the tool fails to launch silently, making
things like snapshot restoration inaccessible.

**The fix:**
Edit each tool's config or script to add your terminal.

### CachyOS Hello

1. Edit the terminal helper script:
   ```bash
   sudo nano /usr/share/cachyos-hello/scripts/terminal-helper
   ```
2. Find `declare -A terminals=(` and add your terminal's launch command:
   - **WezTerm:** `["wezterm"]="wezterm start -- $cmd"`
   - **Ptyxis:** `["ptyxis"]="ptyxis -e $cmd"`
3. Find `declare -a term_order=(` and prepend your terminal ID to the front of the list.

### limine-snapper-restore

1. Edit the restore script:
   ```bash
   sudo nano /usr/bin/limine-snapper-restore
   ```
2. Inside `get_terminal_command()`, append your terminal after the existing checks:
   ```bash
   elif command -v ptyxis &>/dev/null; then echo ptyxis
   ```

### limine-snapper / limine-snapper-sync

1. Edit the configuration file:
   ```bash
   sudo nano /etc/default/limine
   ```
2. Find the `Terminal=` or `TERMINAL=` line (uncomment if needed) and set your terminal:
   ```ini
   TERMINAL=wezterm
   ```

**Reference:**
- [Reddit: Add your terminal to CachyOS tools](https://www.reddit.com/r/cachyos/comments/1rry7qh/guide_add_your_terminal_to_cachyos_tools_like/)

</details>

<details>
<summary><strong>3. Enable cursor trail effect in Kitty terminal</strong></summary>

**The effect:**
When the cursor moves, it leaves a short animated trail behind it. Built into Kitty
since v0.38.0 — no plugins or scripts needed.

**The fix:**
Add these two lines to `~/.config/kitty/kitty.conf`:

```ini
cursor_shape beam
cursor_trail 1
```

- `cursor_shape beam` — thin vertical bar; the most visible shape for the trail
- `cursor_trail 1` — enables the trail; higher values (e.g. `3`) give a longer, more
  pronounced trail

**Optional tuning:**

```ini
cursor_trail_decay 0.1 0.4       # fade-in and fade-out duration in seconds
cursor_trail_start_threshold 2   # min cells of movement before trail appears
```

**Apply without restarting:**
Press `Ctrl+Shift+F5` to reload the config live.

</details>

<details>
<summary><strong>4. KDE Connect blocked by UFW firewall</strong></summary>

**The issue:**
KDE Connect fails to connect to your phone even though both devices are on the same
network. No pairing prompt appears on either side. The root cause is UFW blocking
KDE Connect's traffic — it uses a fixed port range that must be explicitly allowed.

**The fix:**
Allow KDE Connect's port range (1714-1764) through UFW for both TCP and UDP:

```bash
sudo ufw allow 1714:1764/tcp
sudo ufw allow 1714:1764/udp
sudo ufw reload
```

**Verify it's working:**

```bash
sudo ufw status numbered | grep 1714
# Should show ALLOW IN for both tcp and udp on both IPv4 and IPv6
```

**Why this range:**
KDE Connect uses ports 1714-1764 for all communication — device discovery, file
transfer, clipboard sync, notifications, etc. All must be open for full functionality.

</details>

<details>
<summary><strong>5. Docker GPU access fails — <code>AMD CDI spec not found</code> despite NVIDIA toolkit being installed</strong></summary>

**The issue:**
Running a GPU-enabled container with `--gpus all` throws:
```text
docker: Error response from daemon: AMD CDI spec not found
```
Despite `nvidia-ctk --version` confirming the toolkit is installed, `docker info | grep -A5 Runtimes` shows no `nvidia` runtime — only `runc` and `io.containerd.runc.v2`. The misleading "AMD" error is a red herring; the real problem is that the NVIDIA runtime was never registered with Docker.

**The fix:**

**Step 1 — Register the NVIDIA runtime with Docker:**
```bash
sudo nvidia-ctk runtime configure --runtime=docker
```
This writes the `nvidia` runtime entry into `/etc/docker/daemon.json`.

**Step 2 — Restart Docker:**
```bash
sudo systemctl restart docker
```

**Step 3 — Verify:**
```bash
docker info | grep -A5 Runtimes
# Expected: Runtimes: io.containerd.runc.v2 nvidia runc
```

**Step 4 — Test GPU access:**
```bash
docker run --rm --gpus all nvidia/cuda:12.9.0-base-ubuntu24.04 nvidia-smi
```
If the GPU is listed inside the container, you're done.

**If the issue persists after the above steps — CDI fallback:**

Check if a stale AMD CDI spec exists but no NVIDIA one:
```bash
ls /etc/cdi
```
If you see `amd.yaml` but no `nvidia.yaml`, generate one:
```bash
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
```

**What `/etc/docker/daemon.json` should look like after configuration:**
```json
{
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
```

**Notes:**
- Installing `nvidia-container-toolkit` alone is not enough — Docker must be explicitly configured to use it.
- Required sequence: install driver → install toolkit → `nvidia-ctk runtime configure` → restart Docker → validate.
- For Nuclio GPU deployments, confirm `nvidia` appears in Docker runtimes before deploying with `--resource-limit nvidia.com/gpu=1`.

</details>

<details>
<summary><strong>6. Wi-Fi hotspot: clients associate but never get an IP</strong></summary>

**Machine:** Lenovo IdeaPad (`15ach`) — MediaTek MT7921 (`mt7921e`, supports AP mode),
Realtek `eno1` ethernet, NetworkManager 1.58.

**The issue:**
The hotspot turns on and the SSID is visible from phones, but clients sit on
"Obtaining IP address…" and then fail. The same laptop hotspots fine under Windows.

**Root cause:**
`ufw` is active with `DEFAULT_INPUT_POLICY="DROP"` and has no rule allowing DHCP.

1. NetworkManager's hotspot profile uses `ipv4.method: shared`, which spawns an internal
   dnsmasq on `10.42.0.1` serving DHCP (UDP/67) and DNS (53).
2. The phone associates successfully — the WPA2 handshake completes, so the network
   *looks* like it is almost working.
3. The phone broadcasts a DHCP DISCOVER to `255.255.255.255:67`. That packet hits
   `wlan0` INPUT and ufw drops it.
4. No IP lease → client gives up → "Couldn't connect to network."

`DEFAULT_FORWARD_POLICY="DROP"` is a **second** blocker behind it: even once DHCP works,
clients would get an IP but no internet, because ufw drops forwarded traffic regardless
of the NAT rules NetworkManager installs.

Windows works because Windows Firewall auto-installs an ICS ruleset permitting DHCP/DNS
on the Mobile Hotspot adapter. Linux does not do this for you.

**The fix — firewall rules:**

```bash
sudo ufw allow in on wlan0 to any port 67 proto udp comment 'hotspot DHCP'
sudo ufw allow in on wlan0 to any port 53 comment 'hotspot DNS'
sudo ufw route allow in on wlan0 out on eno1 comment 'hotspot NAT'
sudo ufw reload
```

The third rule shares the **ethernet** uplink — the only sane option on a single-radio
card that cannot run AP and client mode at once.

Verify with `sudo ufw status verbose`: the three rules should be listed under
`Default: deny (incoming), deny (routed)`.

**Pin the hotspot to 2.4 GHz (recommended):**
The default profile has `band: --` and `channel: 0` (auto). Under regulatory domain `IN`
this can land the AP on 5 GHz or a channel some phones won't join.

```bash
sudo nmcli connection modify Hotspot 802-11-wireless.band bg 802-11-wireless.channel 6
```

**If there is no `Hotspot` profile yet:**

```bash
nmcli device wifi hotspot ifname wlan0 con-name Hotspot ssid Hotspot password 'YOUR_PASSWORD'
sudo nmcli connection modify Hotspot 802-11-wireless.band bg 802-11-wireless.channel 6
sudo nmcli connection modify Hotspot connection.autoconnect no
```

Working profile settings for reference:

| Setting | Value |
|---|---|
| `802-11-wireless.mode` | `ap` |
| `802-11-wireless.band` | `bg` |
| `802-11-wireless.channel` | `6` |
| `802-11-wireless-security.key-mgmt` | `wpa-psk` |
| `802-11-wireless-security.proto` | `rsn` |
| `802-11-wireless-security.pairwise` | `ccmp` |
| `802-11-wireless-security.group` | `ccmp` |
| `ipv4.method` | `shared` |
| `ipv6.method` | `ignore` |
| `connection.autoconnect` | `no` |

**Required package:**
`shared` mode needs dnsmasq present. NM runs its own instance; the system
`dnsmasq.service` should stay **inactive**.

```bash
sudo pacman -S --needed dnsmasq
systemctl is-active dnsmasq   # should print: inactive
```

---

#### Gotcha: Wi-Fi radio gets left disabled

The Noctalia bar toggle can leave the radio off at **two** independent layers. Symptom is
`wlan0` showing `unavailable` in `nmcli device status`. Both must be clear —
`rfkill unblock` alone is not enough, NetworkManager keeps its own radio state separately.

```bash
rfkill list wifi          # check for "Soft blocked: yes"
rfkill unblock wifi

nmcli radio all           # check WIFI column for "disabled"
nmcli radio wifi on
```

This machine has two rfkill switches, `ideapad_wlan` and `phy0`; `rfkill unblock wifi`
clears both.

---

#### Gotcha: stale dnsmasq blocks restart (most common recurring failure)

**Symptom:** hotspot works the **first** time after a boot, then every subsequent off/on
fails immediately with *"Connection activation failed: IP configuration could not be
reserved (no available address, timeout, etc.)"*. Only a reboot clears it.

**Log signature** (`journalctl -b -u NetworkManager`) — two halves, minutes apart:

```text
# teardown: NM cannot reap its own child
kill child process 'dnsmasq' (434627): unexpected error sending SIGTERM (15): Permission denied (13)

# next start: the orphan is still squatting on 10.42.0.1
dnsmasq: failed to create listening socket for 10.42.0.1: Address already in use
dnsmasq-manager: dnsmasq exited with error: Network access problem (address in use, permissions) (2)
device (wlan0): state change: activated -> failed (reason 'ip-config-unavailable')
```

The radio comes up fine — this is **not** a Wi-Fi failure. It fails at IP config.

**Root cause — AppArmor blocks NM from reaping its own dnsmasq.** Confirmed 2026-09-11.
The `Permission denied` is an LSM denial, not an abrupt teardown:

- `/etc/apparmor.d/usr.sbin.dnsmasq` (Arch stock, **enforce**) allows signals only from
  libvirtd. Once a profile contains *any* signal rule, every other signal is denied, and
  there is no `peer=NetworkManager` rule.
- NetworkManager is a **confined peer** because the `apparmor.d` AUR profile set drops in
  `/etc/apparmor.d/NetworkManager`. That package ships no dnsmasq profile of its own, so
  NM's label hits Arch's libvirtd-only allowlist and the SIGTERM is refused. The stock
  `apparmor` package alone does not cause this.

Ruled out: NM runs as root **and** holds `cap_kill`, so this is not a capability problem.

**Permanent fix** — local override. The stock profile ends with
`include if exists <local/usr.sbin.dnsmasq>`, so this survives package updates:

```bash
sudo install -d /etc/apparmor.d/local
printf 'signal (receive) peer=NetworkManager,\n' | sudo tee /etc/apparmor.d/local/usr.sbin.dnsmasq
sudo apparmor_parser -r /etc/apparmor.d/usr.sbin.dnsmasq
```

Blunter alternatives:

```bash
sudo aa-complain /usr/bin/dnsmasq      # drops enforcement on dnsmasq entirely
yay -R apparmor.d                      # removes the third-party profile set
```

**Clearing an orphan that is already stuck** — the override stops new orphans, it does not
kill one already running. An orphan has a long ELAPSED, `--listen-address=10.42.0.1`, and
NM as its parent:

```bash
ps -eo pid,ppid,user,etime,args | grep '[d]nsmasq'
sudo pkill -f 'nm-dnsmasq-wlan0'

# or the blunt reset, which also clears client-connection flapping
sudo systemctl restart NetworkManager

# confirm nothing still holds the address
sudo ss -lnptu | grep 10.42.0.1     # expect no output when the hotspot is down
```

---

#### Gotcha: no internet for clients — `nm-shared` NAT rules fail to install

**Symptom:** hotspot starts, phone associates and gets a `10.42.0.x` lease, but has **no
internet**. Distinct from the DHCP failure above — the lease works here.

**Log signature** (`journalctl -b -u NetworkManager | grep firewall`):

```text
firewall: nft[494534]: command exited with status 1: (stderr: "Error: Could not process rule:
No such file or directory / add rule ip nm-shared-wlan0 nat_postrouting ip saddr 10.42.0.0/24
ip daddr != 10.42.0.0/24 masquerade")
```

**Root cause — the running kernel's module tree was deleted by an upgrade.** Confirmed
2026-09-11. Not AppArmor, not a firewall issue; it reproduces as unconfined root. The table
and nat chain create fine, only the `masquerade` expression fails, because it needs the
`nft_masq` module and the kernel cannot autoload it:

```bash
modinfo -n nft_masq              # ERROR: Module nft_masq not found
zgrep NFT_MASQ /proc/config.gz   # CONFIG_NFT_MASQ=m  -- so it *should* exist
uname -r                         # 7.2.0-1-cachyos
ls /usr/lib/modules/             # 7.2.3-1-cachyos, 6.18.48-1-cachyos-lts  -- 7.2.0 is GONE
```

A `linux-cachyos` upgrade replaced `/usr/lib/modules/<running-kernel>`. Everything already
resident in memory keeps working, which is why the machine seems fine — but **any module
not yet loaded at upgrade time can never be loaded again until reboot**. Docker's NAT
survives because it uses `xt_MASQUERADE` via `nft_compat`, which was already loaded.

**The fix: reboot.** There is no config change to make. Verify afterwards, hotspot up:

```bash
uname -r                                    # should match a dir in /usr/lib/modules/
modinfo -n nft_masq                         # should print a path
sudo nft list table ip nm-shared-wlan0      # chains nat_postrouting + filter_forward present
```

> **General rule:** on Arch/CachyOS, after any `linux*` package upgrade, treat modules as
> broken until reboot. Symptoms are arbitrary and delayed — a feature works all session,
> then fails the first time something needs a module it has not touched yet.

---

#### Gotcha: duplicate hotspot profiles

You end up with `Hotspot`, `Hotspot-1`, `Noctalia-Hotspot`, … and it is unclear which one
is live. Band/channel settings applied to the wrong one silently do nothing.

It is *not* every toggle. `nmcli device wifi hotspot` looks for an existing profile matching
the ssid/password/ifname you pass — match found, it reuses it; no match, it creates a new
one auto-named `Hotspot-1`, `Hotspot-2`, … So a duplicate appears each time you **change the
SSID or password in the plugin settings**. Editing band/channel afterwards does not break
the match.

```bash
nmcli -f NAME,UUID,TYPE,AUTOCONNECT connection show | grep -i hotspot
nmcli -g 802-11-wireless.ssid,connection.timestamp connection show <name>   # timestamp 0 = never used
nmcli connection delete <orphan-name>
```

Keep exactly one, whose SSID matches the plugin setting in
`~/.local/state/noctalia/settings.toml` under `[plugin_settings."cleboost/hotspot"]`.

> The live Noctalia config is `~/.local/state/noctalia/settings.toml`.
> `~/.config/noctalia/noctalia-config.toml` is an older location and may be stale —
> editing it has no effect.

---

#### Gotcha: client connection fights the AP for the radio

The MT7921 reports `#channels <= 1`, so a Wi-Fi *client* connection on `wlan0` competes with
AP mode. Symptom is repeated `Activation: failed for connection '<SSID>'` with MAC resets
between them, and hotspot activations failing with *"device is not available"*.

Before starting the hotspot on the ethernet-uplink setup, stop the client auto-reconnecting:

```bash
sudo nmcli connection modify <SSID> connection.autoconnect no
```

---

#### Gotcha: MT7921 suspend/resume bug

After a suspend/resume cycle the card can come back half-broken:

```text
mt7921e 0000:04:00.0: Message 00020007 (seq 2) timeout
mt7921e 0000:04:00.0: PM: dpm_run_callback(): pci_pm_resume returns -110
```

If the hotspot misbehaves *specifically after waking from sleep*, reset the card. This is a
known `mt7921e` power-management bug, unrelated to the firewall issue:

```bash
sudo modprobe -r mt7921e && sudo modprobe mt7921e
```

---

**Verification checklist:**

```bash
# 1. Radio is up at both layers
rfkill list wifi
nmcli radio all

# 2. Start the hotspot
nmcli connection up Hotspot

# 3. AP is actually running on the expected address
ip addr show wlan0 | grep 'inet '     # expect 10.42.0.1/24
iw dev wlan0 info | grep type         # expect: type AP

# 4. dnsmasq is listening for the hotspot
sudo ss -lunp | grep ':67'

# 5. Connect a phone, then confirm the lease was handed out
iw dev wlan0 station dump             # should list the client MAC
```

If a client still fails, watch the drops live while it tries to connect. Any
`[UFW BLOCK] IN=wlan0 … DPT=67` line means the firewall rules did not apply:

```bash
sudo journalctl -kf | grep 'UFW BLOCK'
```

</details>

<details>
<summary><strong>7. Electron apps fail to launch under niri on a hybrid GPU laptop</strong></summary>

**Machine:** Lenovo IdeaPad Gaming 3 15ACH — AMD Renoir iGPU + NVIDIA RTX 3050 Mobile
(driver 610.57.04, open module), niri 26.04 + noctalia. Fixed 2026-08-18.

**The issue:**
An Electron AppImage that launched instantly under GNOME took 5–30s under niri, frequently
never showed a window at all, and sometimes dumped core. Closing and immediately relaunching
reliably produced a permanent hang with no UI. Every Electron app on the machine is exposed
to it.

**Root cause — NVIDIA dmabuf import failure:**
niri was configured to composite on the NVIDIA dGPU. Chromium hands the compositor a dmabuf,
NVIDIA rejects the modifier, and the GPU process kills itself:

```text
ERROR:angle_platform_impl.cc(44) ImageEGL.cpp:112: eglCreateImage failed with 0x00003009
ERROR:native_pixmap_egl_binding.cc(113) Unable to initialize binding from pixmap
ERROR:gpu_service_impl.cc(1164) Exiting GPU process because some drivers can't recover from errors
ERROR:gpu_process_host.cc(1007) GPU process exited unexpectedly: exit_code=8704
```

`0x3009` = `EGL_BAD_MATCH`. Chromium restarts the GPU process 3×, then falls back to
`--use-angle=swiftshader-webgl` (CPU rendering). That fallback is what was slow, and it often
never presented a window at all.

This is driver-level — no Chromium flag fixes it. Measured, all with niri on NVIDIA:

| flags | window | gpu crashes |
|---|---|---|
| (baseline) | never | 3 |
| `--use-angle=gl` | never | 3 |
| `--use-angle=vulkan` | never | 0 |
| `--in-process-gpu` | never | 0 (GL context permanently lost) |
| `--disable-gpu` | never | 0 |

With niri compositing on the **AMD iGPU** instead, the app launches in ~5s.

**The fix — `~/.config/niri/cfg/misc.kdl`:**

```kdl
debug {
    render-drm-device "/dev/dri/by-path/pci-0000:06:00.0-render"
    wait-for-frame-completion-before-queueing
}
```

- **`render-drm-device` → AMD iGPU** — avoids the NVIDIA dmabuf bug entirely.
- **by-path, not `renderD12X`** — those numbers are assigned in driver probe order and can
  swap between GPUs across boots. PCI addresses are fixed by the board.
  `06:00.0` = AMD, `01:00.0` = NVIDIA.
- **`wait-for-frame-completion-before-queueing`** — required, not optional. Both external
  monitors are physically wired to the NVIDIA card (only the laptop panel is on AMD), so
  compositing on AMD means a cross-GPU copy per frame, which caused flickering artifacts on
  the externals. This option fixes that. **Do not remove one without the other.**

Requires a re-login; debug options are read at niri startup.

**The dGPU is NOT disabled.** `render-drm-device` only selects the compositor's render GPU.
Games (`prime-run %command%`), CUDA and NVENC are unaffected — verified with `prime-run
glxinfo -B`, `vulkaninfo --summary` (RADV RENOIR *and* RTX 3050 both present) and
`nvidia-smi`. Side benefit: the dGPU can now runtime-suspend when idle, which it could not
while niri composited on it.

**Known remaining issue:**
Even with niri on the iGPU, every launch produces 9× `Cannot create bo with format=RGBA_8888
and usage=SCANOUT` and 3 GPU-process crashes. Chromium usually recovers in ~4s. Occasionally
recovery deadlocks instead — renderer and gpu-process both parked in `futex_wait` — and no
window ever appears. Successful and failed runs have byte-identical error counts; the only
difference is the race outcome. `--disable-gpu` removes the crashes entirely and the window
*still* never appears, so the crashes are not what blocks startup. No known workaround;
relaunching after a hang is the practical answer.

**Dead ends — do not re-investigate:**

- **xdg-desktop-portal** — fine. niri ships `/usr/share/xdg-desktop-portal/niri-portals.conf`.
- **XWayland** — fine. niri 26.04 starts xwayland-satellite automatically; do NOT add a manual
  `spawn-at-startup` for it, that creates a duplicate.
- **Fontconfig** — NOT broken, despite ~90 lines of `xsi:nil` / `invalid constant` warnings per
  launch. `fc-match sans` runs clean and configs are stock package-owned symlinks. Cosmetic
  noise from fontconfig 2.18.3 surfaced via Chromium's parse path.
- **Menu vs terminal launcher** — NOT a factor. A menu-launched process has an identical
  environment, including `ELECTRON_OZONE_PLATFORM_HINT=auto`, `WAYLAND_DISPLAY` and
  `NIRI_SOCKET`. Apparent menu-only failures were the race above.
- **GPUCache / DawnCache corruption** — NOT a factor. Launches succeeded with the cache present
  and failed right after it was regenerated.
- **Hiding NVIDIA from the app** (`VK_DRIVER_FILES`, `__EGL_VENDOR_LIBRARY_FILENAMES`,
  `__GLX_VENDOR_LIBRARY_NAME`, `DRI_PRIME=0`) — does stop the app touching `/dev/nvidiactl`,
  but does NOT fix the crash loop. Redundant once niri is on the iGPU.

**Debugging notes for next time:**

```bash
# which GPU niri actually chose
journalctl --user -b | grep "using as the render node"

# detect the window by App ID, not title -- title matching also hits your terminal
niri msg windows | grep 'App ID: "<app-id>"'
```

**Upstream references:**

- [niri #3674](https://github.com/niri-wm/niri/issues/3674) — external monitor lag on hybrid
  laptops, `render-drm-device` undocumented
- [niri #3777](https://github.com/niri-wm/niri/discussions/3777) — Electron apps flickering on
  NVIDIA, `wait-for-frame-completion-before-queueing`
- [NVIDIA forum](https://forums.developer.nvidia.com/t/570-124-04-prime-offload-runtime-d3-power-management-broken-on-electron-app-launch-on-wayland/326907)
  — prime offload / D3 broken on Electron launch under Wayland

</details>

---

## Other Guides

| Guide | Description |
|---|---|
| [CVAT + UFW Firewall Troubleshooting](./CVAT_UFW_Troubleshooting.md) | Fixing Docker/UFW networking conflicts that break CVAT auto-annotation with Nuclio serverless functions. Covers UFW forward policy, bridge forwarding rules, subnet allow rules, port desync, VRAM issues, and a post-reboot recovery checklist. |

---

## Scripts

Helper scripts kept in [`scripts/`](./scripts/).

### `steam-client-block.py`

Cuts the **Steam client's** network access while leaving games fully online — useful to stop
the client phoning home, auto-updating or overlaying without breaking anything you launch
through it.

```bash
./scripts/steam-client-block.py --dry-run   # classify running processes, no root needed
sudo ./scripts/steam-client-block.py        # interactive menu
sudo ./scripts/steam-client-block.py --status
```

**How it works:** Steam client processes are moved into the cgroup v2
`/sys/fs/cgroup/steamblock`, and an nftables OUTPUT rule drops that cgroup's traffic
(loopback stays allowed so the client's IPC and UI keep working). A background thread polls
4×/second — anything Steam launches inherits the blocked cgroup, so every process that is
*not* a Steam-client binary (games, Proton, wine, pressure-vessel, launchers) is moved back
out to `/sys/fs/cgroup/steamallow`. Unknown processes are moved out too, so a game can never
be blocked by accident.

> [!WARNING]
> Needs root and writes an nftables table named `steamblock`. It only adds and removes its
> own table, but run `--dry-run` first to see how your processes get classified. Run
> `--status` to check state, and use the menu's unblock option to tear the rules down.

---

## Dotfiles Backup

Config backups stored in [`dotfiles/`](./dotfiles/).

| Config | Source | What it is |
|---|---|---|
| [`dotfiles/niri/`](./dotfiles/niri/) | `~/.config/niri/` | Niri Wayland compositor — main config, noctalia theme override, and modular cfg split across `cfg/` |
| [`dotfiles/noctalia/`](./dotfiles/noctalia/) | `~/.config/noctalia/` | Noctalia panel — settings, color palette, plugin configs, and user templates |
| [`dotfiles/fish/`](./dotfiles/fish/) | `~/.config/fish/` | Fish shell — `config.fish`, custom functions, and greeting configuration (universal variables with credentials are intentionally excluded) |
| [`dotfiles/starship/`](./dotfiles/starship/) | `~/.config/starship.toml` | Starship prompt config |
| [`dotfiles/nvim/`](./dotfiles/nvim/) | `~/.config/nvim/` | Neovim — LazyVim setup, `init.lua`, `lua/config/`, `lua/plugins/`, and a pinned `lazy-lock.json` |

To restore, copy the relevant folder back:

```bash
cp -r dotfiles/niri/* ~/.config/niri/

cp -r dotfiles/noctalia/* ~/.config/noctalia/

cp -r dotfiles/fish/* ~/.config/fish/

cp dotfiles/starship/starship.toml ~/.config/starship.toml

cp -r dotfiles/nvim ~/.config/nvim   # then launch `nvim` once to install plugins
```

---

## Apps & Tools

A full categorized list of everything installed: → **[apps.md](./apps.md)**

---

## Wallpapers

**Main collection — iNiR-Walls:**

Clone the wallpaper pack used with this setup:

```bash
git clone https://github.com/snowarch/iNiR-Walls ~/Pictures/Wallpapers
```

**Extra wallpapers** (personal additions not in the iNiR-Walls repo) are backed up in
[`wallpapers/extra/`](./wallpapers/extra/) — 16 images, mostly from Pexels.

To restore them into the wallpapers folder:

```bash
cp wallpapers/extra/* ~/Pictures/Wallpapers/images/
```
