# CachyOS Issues & Fixes

This repository is a collection of CachyOS issues I encountered along with the applied fixes, kept in one place for easy reference.

## Issues & Solutions

<details>
<summary><strong>1. Run Cachy-Update in a specific terminal emulator (e.g., Kitty)</strong></summary>

**The Issue:**
`gio` (used to launch the `arch-update` terminal application via the `arch-update.desktop` file when the systray applet is clicked) currently has a default limited list of known terminal emulators. If none of these "known" terminal emulators are installed on the system, clicking the systray applet does nothing because `gio` cannot find a match from the list. Alternatively, if multiple terminal emulators are installed, it may be necessary to specify which one to use.

**The Solution:**
A preferred terminal (like Kitty) can be configured using `xdg-terminal-exec`.

**Step 1: Install `xdg-terminal-exec` from the AUR**
Using an AUR helper (e.g., `paru` or `yay`):
```bash
paru -S xdg-terminal-exec
# or
yay -S xdg-terminal-exec
```

**Step 2: Create the config file and add the terminal's desktop entry**
For Kitty:
```bash
echo "kitty.desktop" > ~/.config/xdg-terminals.list
```
*Note: Kitty's `.desktop` file is named `kitty.desktop`. Its presence on the system can be verified with:*
```bash
find /usr/share/applications ~/.local/share/applications -name "kitty.desktop" 2>/dev/null
```

**Step 3: Completion**
The next time the systray applet is clicked, `gio` will use `xdg-terminal-exec` to resolve the terminal, which will in turn read `~/.config/xdg-terminals.list` and launch Kitty.

**Extra Notes:**
- The file supports multiple entries (one per line), listed in order of preference - so if Kitty isn't found for some reason, it falls back to the next one on the list.
- To switch terminals later, edit `~/.config/xdg-terminals.list` and replace `kitty.desktop` with another entry (e.g., `Alacritty.desktop`, `foot.desktop`, etc.).

**Reference:** [CachyOS cachy-update documentation](https://github.com/CachyOS/cachy-update#run-cachy-update-in-a-specific-terminal-emulator)

</details>

