# Configuration Backup

This directory snapshots selected active configuration from `~/.config/`.

Refresh the backup from the corresponding live paths. Generated Noctalia theme
files are omitted; Noctalia regenerates them after setup.
Alacritty, Foot, GTK and Btop backups are excluded. This also excludes their
non-theme settings and GTK bookmarks; it does not modify the live files.

## Included

- Fish, Starship, Niri, Noctalia, Neovim, Kitty, autostart and WirePlumber.
- Noctalia's live settings and state in `noctalia-state/`.
- `dconf.ini`, an earlier export of the dconf database.

The Noctalia panel's live settings are in
`noctalia-state/settings.toml`, not only in `noctalia/noctalia-config.toml`.

## Deliberately excluded

Exclude passwords, private keys, browser profiles, paired-device identities,
cookies, session data, clipboard/notification history, caches, backups, and
downloaded models. In particular, `~/.config/opencode/service.json`, KDE
Connect's key material, Noctalia calendar credentials, and browser
configuration trees must not be copied.

## Restore

Merge a directory into its source path; do not delete the destination first.

```bash
cp -a dotfiles/niri/. ~/.config/niri/
cp -a dotfiles/nvim/. ~/.config/nvim/
cp -a dotfiles/noctalia/. ~/.config/noctalia/
cp -a dotfiles/noctalia-state/. ~/.local/state/noctalia/
dconf load / < dotfiles/dconf.ini
```

For another directory, use the same form, for example:

```bash
cp -a dotfiles/kitty/. ~/.config/kitty/
```
