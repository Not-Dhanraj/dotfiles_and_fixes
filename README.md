# Dotfiles & Issue fixes

A personal dotfiles collection and reference of issues I ran into on CachyOS and how I fixed them - kept
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

#### Noctalia hotspot plugin: keep SSID and profile in sync

The `cleboost/hotspot` plugin reads its settings from the live Noctalia state file,
`~/.local/state/noctalia/settings.toml` (the older
`~/.config/noctalia/noctalia-config.toml` may be stale). SSIDs are case-sensitive;
the plugin's `ssid` and the NetworkManager profile's `802-11-wireless.ssid` must match
exactly. A mismatch can leave the old network active or create a duplicate profile when
the plugin creates a new one.

For example, to use `15ACH6` with the existing `Hotspot` profile:

```bash
noctalia config validate ~/.local/state/noctalia/settings.toml
nmcli connection modify Hotspot 802-11-wireless.ssid 15ACH6
nmcli -g 802-11-wireless.ssid connection show Hotspot  # should print: 15ACH6
```

Set the plugin's SSID to the same exact value in Noctalia. Keep its password and the
NetworkManager profile's saved Wi-Fi password identical; never put the password in this
README or share it in logs. After changing settings, restart the hotspot and connect again.
Before deleting any duplicate profiles, inspect them with
`nmcli -f NAME,UUID,TYPE connection show` and retain the profile matching the plugin.

`noctalia config validate` may report warnings for settings belonging to unloaded plugins
or unknown widget settings while still declaring the config valid. Review each warning
before removing saved settings; validation warnings alone do not establish that the data is
safe to delete.

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

<details>
<summary><strong>8. ONLYOFFICE: oversized active border and padding around the window on niri</strong></summary>

**Fixed:** 2026-10-19. Tested with `onlyoffice-bin 10.0.0-1`, `niri 26.04-1.1`,
`xwayland-satellite 0.8.3-1.1`, and Noctalia on CachyOS.

**Reapplied 2026-11-07:** the preference had returned to `titlebar=custom`. Switched
it back to `system` after closing the empty window, removed the temporary Niri rule,
and visually confirmed that the focus ring meets the application frame.

**The issue:**
ONLYOFFICE had a thick-looking blue active border. After removing the blue fill, a visible
gap still separated niri's thin focus outline from the actual application frame.

**Cause — custom client-side shadows, not an oversized focus ring:**
ONLYOFFICE was running through XWayland with `titlebar=custom`. Its custom frame reserved
transparent space for its own shadow. The live X11 window advertised:

```text
_GTK_FRAME_EXTENTS = 26, 26, 24, 28
```

These are the left, right, top, and bottom margins in pixels. Capturing the application
surface confirmed the transparent margins. Niri's focus-colour background showed through
them, making the border look thick. Niri's focus-ring width was already **2 px** and was
not the cause.

The problem was reported after an update, but the investigation did **not** establish
which release introduced it; the available package log only showed installation and
reinstallation of ONLYOFFICE 10.0.0.

**The permanent fix — use ONLYOFFICE's system-title-bar mode:**

1. Save all documents and fully quit ONLYOFFICE before editing its preferences. Do not
   force-kill an instance with unsaved documents.
2. Edit `~/.config/onlyoffice/DesktopEditors.conf`. Under the existing `[General]` section,
   change only `titlebar=custom` to:

   ```ini
   [General]
   titlebar=system
   ```

   Preserve all other keys and sections, including saved window geometry. Do not replace
   the entire file with this excerpt. ONLYOFFICE also advertises the supported
   `--system-title-bar` option in `onlyoffice-desktopeditors --help`.
3. Reopen ONLYOFFICE normally:

   ```bash
   onlyoffice-desktopeditors
   ```

No compositor restart or re-login is needed. This disables ONLYOFFICE's custom shadow
frame, so the active outline sits directly against the application surface.

**The earlier workaround — removed after the permanent fix:**

The following app-specific rule was initially added to
`~/.config/niri/cfg/99-user-overrides.kdl`:

```kdl
window-rule {
    match app-id=r"^ONLYOFFICE$"
    draw-border-with-background false
}
```

This removed the thick blue **fill**, but did **not** remove the transparent shadow
padding. Once `titlebar=system` fixed the geometry, this rule and its explanatory comment
were removed. Leave the normal **2 px** focus-ring setting unchanged; no special
ONLYOFFICE border rule is required for the final configuration.

**Verified result and UI tradeoff:**

- Reopened the real application using the normal launcher and inspected full-display
  screenshots of both the home screen and a presentation editor.
- The final editor surface was `1904 × 1027`; its alpha channel was `255` everywhere,
  confirming that no transparent outer shadow margins remained.
- The focus outline sat directly against the window without a blue-filled gap.
- Document tabs remained visible in the real user profile. An earlier isolated-profile
  test had shown a blank header; that result did **not** represent the final live UI.
- ONLYOFFICE's custom minimize/maximize/close buttons disappeared. Use niri's normal
  window-management shortcuts instead.
- `niri validate` passed after removing the temporary compositor rule.

**Rollback:**
Save documents and fully quit ONLYOFFICE, change the same preference back to
`titlebar=custom`, then reopen it. This restores the custom window controls and shadow
padding. If the blue-filled border also returns, the app-specific rule above can suppress
the fill, but it remains only a partial workaround and will not eliminate the gap.

**References:**

- [niri: `draw-border-with-background`](https://github.com/niri-wm/niri/wiki/Configuration:-Window-Rules#draw-border-with-background)
- [ONLYOFFICE: title-bar mode and thin-frame selection](https://github.com/ONLYOFFICE/desktop-apps/blob/master/win-linux/src/utils.cpp)
- [ONLYOFFICE: custom frame margins and shadow drawing](https://github.com/ONLYOFFICE/desktop-apps/blob/master/win-linux/src/windows/platform_linux/cwindowplatform.cpp)

</details>

<details>
<summary><strong>9. input-remapper preset doesn't auto-start — AUR <code>input-remapper-bin</code> never enables the service</strong></summary>

**Fixed:** 2026-11-07. Tested with `input-remapper-bin 2.2.1-3`, `niri` on CachyOS (Wayland).

**The issue:**
A Razer Basilisk V3 Pro preset was set to autoload, but after login the remaps were
inactive. They only started working after opening `input-remapper-gtk` manually.

**Cause — the daemon is not running at login, not a bad preset:**
input-remapper has two parts: a root daemon (`input-remapper-service`) that does the
injection, and a client (`input-remapper-control` / the GUI) that asks it to load presets.
The preset and `~/.config/input-remapper-2/config.json` were correct:

```json
"autoload": { "Razer Razer Basilisk V3 Pro": "mouse" }
```

niri does start `xdg-desktop-autostart.target` (it is `WantedBy=niri.service`), so
`/etc/xdg/autostart/input-remapper-autoload.desktop` ran at login — but it failed because
the daemon was down:

```text
app-input\x2dremapper\x2dautoload@autostart.service   failed
ERROR: Service not running? The name is not activatable
ERROR: Daemon missing
```

Why the daemon was down:

1. `input-remapper.service` was **disabled** (`inactive (dead)`).
2. The package ships no D-Bus activation file
   (`/usr/share/dbus-1/system-services/inputremapper.Control.service`), so
   `input-remapper-control` cannot start the daemon on demand ("not activatable").
3. The upstream `.deb`'s `postinst` runs `systemctl enable input-remapper` and
   `systemctl start input-remapper`, but the AUR **`input-remapper-bin` PKGBUILD only
   extracts the files and never runs that `postinst`**. The service was therefore never
   enabled on this machine.

Opening the GUI works because it runs
`pkexec input-remapper-control --command start-daemon`, which starts the root daemon.

**Diagnose with:**
```bash
systemctl is-enabled input-remapper.service        # -> disabled
systemctl --user status 'app-input\x2dremapper\x2dautoload@autostart.service' --no-pager
journalctl -b | grep -i input-remapper | tail
```

**The fix — replicate the official postinst:**
```bash
# stop any daemon started manually by the GUI so the D-Bus name is free
for p in $(pgrep -f '^python3 /usr/sbin/input-remapper-service'); do sudo kill "$p"; done

# start the daemon at boot and enable it permanently
sudo systemctl enable --now input-remapper.service
```

**Verify:**
```bash
systemctl status input-remapper.service --no-pager
input-remapper-control --command autoload    # as your user, no sudo
```

Expected journal output:
```text
Loaded config from "/home/<user>/.config/input-remapper-2/config.json"
Autoloading for "Razer Razer Basilisk V3 Pro"
Loading preset from ".../presets/Razer Razer Basilisk V3 Pro/mouse.json"
Starting injecting the preset for "Razer Razer Basilisk V3 Pro"
kernel: input: input-remapper keyboard as /devices/virtual/input/inputXX
```

**Notes:**
- `ERROR: Could not find ".../xmodmap.json"` is harmless on Wayland; that file is only
  used for X11 symbol-name matching.
- No niri `spawn-at-startup` entry is needed — niri already pulls in the XDG autostart
  target.
- If you reinstall `input-remapper-bin` from scratch, re-run the `systemctl enable --now`
  step; the package does not do it for you.
- The old failed user unit is only cosmetic; clear it with:
  ```bash
  systemctl --user reset-failed 'app-input\x2dremapper\x2dautoload@autostart.service'
  ```

**Reference:**
- [input-remapper upstream (sezanzeb/input-remapper)](https://github.com/sezanzeb/input-remapper)

</details>

<details>
<summary><strong>10. Opening a folder launches Kitty instead of Nautilus (niri)</strong></summary>

**The issue:**
Clicking a folder — or anything that asks the system to "open the file manager" — launched
Kitty instead of Nautilus. Kitty itself is fine as the default *terminal*; the two settings
are unrelated.

Under niri, `inode/directory` has no explicit default handler, so GIO falls back to the first
application registered for that MIME type — which is `kitty-open.desktop`, because kitty's URL
launcher declares `inode/directory` in its `MimeType` list. GNOME's defaults in
`/usr/share/applications/gnome-mimeapps.list` (`inode/directory=org.gnome.Nautilus.desktop`)
are only honoured when `XDG_CURRENT_DESKTOP=GNOME`, so they are ignored on niri.

**Diagnose:**
```bash
xdg-mime query default inode/directory
# kitty-open.desktop

gio mime inode/directory
# Default application for "inode/directory": kitty-open.desktop
```

**The fix:**
```bash
xdg-mime default org.gnome.Nautilus.desktop inode/directory
```

**Verify:**
```bash
xdg-mime query default inode/directory
# org.gnome.Nautilus.desktop
```

This appends the association to `~/.config/mimeapps.list` (no root required):
```ini
[Default Applications]
inode/directory=org.gnome.Nautilus.desktop
```

**Notes:**
- This does **not** change the default terminal. "Open in Terminal" still launches Kitty
  through `~/.config/xdg-terminals.list` (see fix #1).
- Reverse it anytime with:
  ```bash
  xdg-mime default kitty-open.desktop inode/directory
  ```
- `kitty-open.desktop` also registers `application/x-sh`, `application/x-shellscript`,
  `x-scheme-handler/ssh`, `image/*`, and `text/*`. The same fallback can make those open in
  Kitty (or another unexpected app). If that happens, set an explicit default for the type,
  e.g.:
  ```bash
  xdg-mime default nvim.desktop text/plain
  xdg-mime default org.gnome.Loupe.desktop image/png
  ```

**Reference:**
- [XDG MIME Applications spec](https://specifications.freedesktop.org/mime-apps-spec/latest/)
- [GLib default terminal handling (Default Terminal Spec)](https://gitlab.gnome.org/GNOME/glib/-/blob/main/gio/gdesktopappinfo.c)

</details>

<details>
<summary><strong>11. Open a folder in Kitty from Nautilus</strong></summary>

**The fix:**
Install Kitty and the `nautilus-open-any-terminal` extension on CachyOS / Arch Linux:

```bash
sudo pacman -S kitty
yay -S nautilus-open-any-terminal   # or: paru -S nautilus-open-any-terminal
```

The extension is an AUR package and pulls in `python-nautilus`. Without an AUR helper,
see the manual installation instructions on the [AUR package page](https://aur.archlinux.org/packages/nautilus-open-any-terminal).

Set Kitty as the extension's terminal and restart Nautilus so it loads the extension:

```bash
gsettings set com.github.stunkymonkey.nautilus-open-any-terminal terminal kitty
nautilus -q
```

Reopen Nautilus and right-click a folder or an empty area inside one, then select the
terminal entry. Kitty opens in that folder. This setting is separate from the default
file-manager association in fix #10.

If `gsettings` reports that the schema is missing, verify the extension was installed;
the upstream settings instructions also explain how to compile the schema.

**Reference:**
- [nautilus-open-any-terminal installation and settings](https://github.com/Stunkymonkey/nautilus-open-any-terminal)

</details>

<details>
<summary><strong>12. Show both monitor audio outputs in Noctalia</strong></summary>

**The issue:**
The NVIDIA HDMI audio card detected both the TD1655 touch monitor and BenQ EX2510S,
but its default profile exposed only one output at a time. Noctalia could not list
the BenQ while the touch monitor's profile was active.

**The fix:**
The user-level WirePlumber rule at
`~/.config/wireplumber/wireplumber.conf.d/51-dual-hdmi.conf` matches
`alsa_card.pci-0000_01_00.1` and loads
`~/.config/wireplumber/hdmi-dual-profile.conf`. That profile combines the standard
`hdmi-stereo` and `hdmi-stereo-extra1` mappings, exposing both as separate stereo
outputs. The rule uses an absolute path to the profile; update it if the home path
changes. The laptop speakers use a different card and are unaffected.

Create `~/.config/wireplumber/hdmi-dual-profile.conf`:

```ini
[General]
auto-profiles = yes

[Mapping hdmi-stereo]
description = Digital Stereo (HDMI)
device-strings = hdmi:%f
paths-output = hdmi-output-0
channel-map = left,right
priority = 9
direction = output

[Mapping hdmi-stereo-extra1]
description = Digital Stereo (HDMI 2)
device-strings = hdmi:%f,1
paths-output = hdmi-output-1
channel-map = left,right
priority = 7
direction = output

[Profile dual-hdmi]
description = Two HDMI Stereo Outputs
output-mappings = hdmi-stereo hdmi-stereo-extra1
priority = 10000
```

Create `~/.config/wireplumber/wireplumber.conf.d/51-dual-hdmi.conf`:

```ini
monitor.alsa.rules = [
  {
    matches = [ { device.name = "alsa_card.pci-0000_01_00.1" } ]
    actions = {
      update-props = {
        device.profile-set = "/home/dhanraj/.config/wireplumber/hdmi-dual-profile.conf"
        device.profile = "dual-hdmi"
      }
    }
  }
]
```

After restoring the files, restart WirePlumber before activating the profile.

To activate the profile and check the outputs:

```bash
pactl set-card-profile alsa_card.pci-0000_01_00.1 dual-hdmi
wpctl status
```

Select the desired monitor in Noctalia. The profile selection is restored by
WirePlumber; restarting it reloads the configuration but interrupts active audio:

```bash
systemctl --user restart wireplumber
```

This mapping is specific to the current NVIDIA card and HDMI ports. If the hardware
or connections change, check `pactl list cards` for the detected ports and profiles.

**Reference:**
- [ArchWiki: multiple sinks on the same sound card](https://wiki.archlinux.org/title/PipeWire/Troubleshooting#Simultaneous_output_to_multiple_sinks_on_the_same_sound_card)

</details>

---

<details>
<summary><strong>13. USB DAC detected but silent (Shanling UA1s)</strong></summary>

**The issue:** The UA1s was the default PipeWire output and unmuted, but its separate ALSA playback volume at index 1 was at the minimum (0/127, -63.5 dB). Audio returned after raising it, but the setting reset on USB reconnect until the card state was saved.

**Find the card and its controls:** After a reinstall, install `alsa-utils` if `aplay`, `amixer`, or `alsactl` is missing (`sudo pacman -S alsa-utils` on CachyOS/Arch). Connect the DAC first, then run:

```bash
aplay -l                  # playback cards: e.g. card 0: UA1s [Shanling UA1s]
amixer -c UA1s controls   # list controls and their numid values
amixer -c UA1s contents   # show values, ranges, and switches
```

In `aplay -l`, `UA1s` is the ALSA card ID, `0` is its current card number, and the bracketed text is its descriptive name. Use the ID with `-c`; card numbers can change after reconnecting. The UA1s had two playback volume controls: `numid=4` (stereo) and `numid=5` (a separate control with `index=1`). `numid` is a control number, not a card number; look it up again because IDs and controls may differ between devices or after reconnecting. Inspect a control with:

```bash
amixer -c UA1s cget numid=5
```

**Fix and persist:** With headphones off and output volume reduced, raise the quiet control to a moderate value within the range reported by `cget`, then save this card's mixer state:

```bash
amixer -c UA1s cset numid=5 80
sudo alsactl store UA1s
```

Reconnect the DAC and test audio, gradually raising the listening volume. This machine's ALSA udev rule restores saved card state on device add; saving the UA1s state fixed the reconnect issue here. After reinstalling, check that `/usr/lib/udev/rules.d/90-alsa-restore.rules` exists; the saved state in `/var/lib/alsa/asound.state` belongs to the old installation unless restored from backup, so repeat the save step if needed. A reboot is a separate test.

For another DAC, find its card ID with `aplay -l`, replace `UA1s` in the commands, and use `controls` and `contents` to identify its playback volume and mute switches. Use the `numid` and range actually reported for that card; do not assume `5` or `80` applies. Not every silent device has this extra control, so also check the selected output, application volume, and mute state.

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

The complete portable configuration snapshot is in [`dotfiles/`](./dotfiles/).
It includes desktop, shell, terminal, editor, appearance, Noctalia live-state,
and standalone XDG configuration files. See [`dotfiles/README.md`](./dotfiles/README.md)
for the source mapping, restore commands, and the security-conscious exclusions.

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
