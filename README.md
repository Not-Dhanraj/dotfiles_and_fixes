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
paru -S xdg-terminal-exec   # or: yay -S xdg-terminal-exec
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

---

## Other Guides

| Guide | Description |
|---|---|
| [CVAT + UFW Firewall Troubleshooting](./CVAT_UFW_Troubleshooting.md) | Fixing Docker/UFW networking conflicts that break CVAT auto-annotation with Nuclio serverless functions. Covers UFW forward policy, bridge forwarding rules, subnet allow rules, port desync, VRAM issues, and a post-reboot recovery checklist. |

---

## Dotfiles Backup

Config backups stored in [`dotfiles/`](./dotfiles/).

| Config | Source | What it is |
|---|---|---|
| [`dotfiles/niri/`](./dotfiles/niri/) | `~/.config/niri/` | Niri Wayland compositor — main config, noctalia theme override, and modular cfg split across `cfg/` |
| [`dotfiles/noctalia/`](./dotfiles/noctalia/) | `~/.config/noctalia/` | Noctalia panel — settings, color palette, plugin configs, and user templates |
| [`dotfiles/fish/`](./dotfiles/fish/) | `~/.config/fish/` | Fish shell — `config.fish`, `fish_variables`, `fish_greeting.fish`, `fcc.fish` |
| [`dotfiles/starship/`](./dotfiles/starship/) | `~/.config/starship.toml` | Starship prompt config |

To restore, copy the relevant folder back:

```bash
cp -r dotfiles/niri/* ~/.config/niri/

cp -r dotfiles/noctalia/* ~/.config/noctalia/

cp -r dotfiles/fish/* ~/.config/fish/

cp dotfiles/starship/starship.toml ~/.config/starship.toml
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
