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
```
