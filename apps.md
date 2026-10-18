# Apps & Tools

A categorized list of everything installed and used on this system.

> **System:** CachyOS · Niri (Wayland) · Noctalia shell

> [!NOTE]
> Packages are tagged by source:
> `pacman` = official Arch or CachyOS repos · `AUR` = Arch User Repository · `flatpak` = Flathub
> The goal is to minimize AUR usage where possible. AUR commands use `yay`.

> [!IMPORTANT]
> This is a **curated** list — the apps actually used day to day.
> It deliberately omits the base system, kernels, drivers, codecs and the
> GNOME session, all of which come from the CachyOS installer. Niri is
> installed on top of that GNOME base. The gaming stack is available from
> the **CachyOS Hello** app and is not tracked here.

---

## Daily Use

| App | Package | Source | What it's for |
|---|---|---|---|
| Kitty | `kitty` | pacman | Primary terminal |
| Starship | `starship` | pacman | Shell prompt |
| Brave | `brave-bin` | pacman (cachyos) | Primary browser |
| Zen Browser | `zen-browser-bin` | pacman (cachyos) | Secondary browser |
| Firefox | `firefox` | pacman | Backup browser |
| Google Chrome | `google-chrome` | AUR | Chromium-based browser |
| Telegram | `telegram-desktop` | pacman | Chat |
| KDE Connect | `kdeconnect` | pacman | Phone ↔ desktop |
| AB Download Manager | `ab-download-manager` | pacman (cachyos) | Download manager |

```bash
# Official / CachyOS repos
sudo pacman -S kitty starship brave-bin zen-browser-bin firefox telegram-desktop kdeconnect ab-download-manager

# AUR
yay -S google-chrome
```

---

## Development

| App | Package | Source | What it's for |
|---|---|---|---|
| VS Code | `visual-studio-code-bin` | AUR | Primary editor |
| Antigravity IDE | `antigravity-ide` | AUR | AI coding assistant |
| OpenCode | `opencode` | pacman | Terminal coding agent |
| Android Studio | `android-studio` | AUR | Android dev |
| Flutter | *manual* | — | Cross-platform UI — see note below |
| JupyterLab | `jupyterlab` | pacman | Python notebooks |
| CUDA | `cuda` | pacman | GPU compute (NVIDIA open drivers) |
| GitHub Desktop | `github-desktop` | pacman | Git GUI |
| Git LFS | `git-lfs` | pacman | Large file support for Git |
| Docker | `docker`, `docker-compose` | pacman | Containers |

```bash
# Official / CachyOS repos
sudo pacman -S opencode jupyterlab cuda github-desktop git-lfs docker docker-compose

# AUR
yay -S visual-studio-code-bin antigravity-ide  android-studio
```

> [!NOTE]
> **Flutter is not installed from a package.** The SDK lives at `~/tools/flutter`
> (currently 3.47.2, stable channel) and is put on `PATH` by `dotfiles/fish/config.fish`:
>
> ```fish
> fish_add_path $HOME/tools/flutter/bin
> fish_add_path $HOME/.pub-cache/bin
> ```
>
> To restore: clone `https://github.com/flutter/flutter.git` into `~/tools/flutter`,
> check out the `stable` branch, then run `flutter doctor`.

---

## Terminal & CLI

| Tool | Package | Source | What it's for |
|---|---|---|---|
| Neovim | `neovim` | pacman | Terminal editor — config backed up in `dotfiles/nvim/` |
| lazygit | `lazygit` | pacman | Terminal git UI |
| GitHub CLI | `github-cli` | pacman | The `gh` command |
| zoxide | `zoxide` | pacman | Smarter `cd` — initialised in `config.fish` |
| ripgrep | `ripgrep` | pacman | Fast recursive search (`rg`) |

```bash
sudo pacman -S neovim lazygit github-cli zoxide ripgrep
```

> [!NOTE]
> The Neovim config in `dotfiles/nvim/` is a **LazyVim** setup. Restore with:
> ```bash
> cp -r dotfiles/nvim ~/.config/nvim && nvim   # plugins install on first launch
> ```
> `lazy-lock.json` is included, so plugin versions are pinned to a known-good state.

---

## Speech to Text

| App | Package | Source | What it's for |
|---|---|---|---|
| Handy | `handy-bin` | AUR | Offline speech-to-text, works system-wide |

```bash
yay -S handy-bin
```

---

## Creative & Media

| App | Package | Source | What it's for |
|---|---|---|---|
| OBS Studio | `obs-studio` | pacman | Screen recording / streaming |
| Kdenlive | `kdenlive` | pacman | Video editing |
| VLC | `vlc` | pacman | Media playback |
| Handbrake | `handbrake` | pacman | Video transcoding |
| Snapshot | `snapshot` | pacman | Camera / screenshot capture |
| gpu-screen-recorder | `gpu-screen-recorder` | pacman | GPU-accelerated recording |

```bash
sudo pacman -S obs-studio kdenlive vlc handbrake snapshot gpu-screen-recorder
```

---

## System & Utilities

| App | Package | Source | What it's for |
|---|---|---|---|
| Btop | `btop` | pacman | Resource monitor (terminal) |
| Mission Center | `mission-center` | pacman | Resource monitor (GUI) |
| Fastfetch | `fastfetch` | pacman | System info |
| Filelight | `filelight` | pacman | Disk usage (GUI) |
| BTRFS Assistant | `btrfs-assistant` | pacman | Snapper / btrfs GUI |
| Solaar | `solaar` | pacman | Logitech device manager |
| Input Remapper | `input-remapper-bin` | AUR | Remap keys/buttons |
| Blueman | `blueman` | pacman | Bluetooth manager |
| LACT | `lact` | pacman | GPU overclocking |
| Meld | `meld` | pacman | Diff / merge tool |
| scrcpy | `scrcpy` | pacman | Android screen mirror |
| Metadata Cleaner | `metadata-cleaner` | pacman | Remove file metadata |
| Yazi | `yazi` | pacman | Terminal file manager |
| Remmina | `remmina` | pacman | Remote desktop client |

```bash
# Official / CachyOS repos
sudo pacman -S btop mission-center fastfetch filelight btrfs-assistant solaar blueman lact meld scrcpy metadata-cleaner yazi remmina

# AUR
yay -S input-remapper-bin
```

---

## Writing & Office

| App | Package | Source | What it's for |
|---|---|---|---|
| OnlyOffice | `onlyoffice-bin` | pacman (cachyos) | Office suite |
| LibreOffice | `libreoffice-fresh` | pacman | Office suite (backup) |
| Setzer | `setzer` | pacman | LaTeX editor |
| TeXLive | `texlive-*` | pacman | LaTeX distribution |

```bash
sudo pacman -S onlyoffice-bin libreoffice-fresh setzer texlive-basic texlive-bibtexextra texlive-binextra texlive-context texlive-fontsextra texlive-fontsrecommended texlive-fontutils texlive-formatsextra texlive-games texlive-humanities texlive-latex texlive-latexextra texlive-latexrecommended texlive-luatex texlive-mathscience texlive-metapost texlive-music texlive-pictures texlive-plaingeneric texlive-pstricks texlive-publishers texlive-xetex
```

---

## Wayland / Shell Stack

| Component | Package | Source | What it's for |
|---|---|---|---|
| Niri | `niri` | pacman | Wayland compositor |
| Noctalia | `noctalia` | pacman | Shell (bar, launcher, etc.) |
| NiriMod | `nirimod-git` | AUR | Visual config for Niri |
| Bazaar | `bazaar` | pacman | Flatpak app store |

```bash
# Official / CachyOS repos
sudo pacman -S niri noctalia bazaar

# AUR
yay -S nirimod-git
```

> [!NOTE]
> Noctalia used to be `noctalia-git` from the AUR — it is now packaged in the
> official `extra` / `cachyos-extra-v3` repos as plain `noctalia`.
> `noctalia-greeter` is **not** installed.
>
> Screenshots use Niri's built-in `screenshot` action, so `grim` and `slurp`
> are no longer needed.

---

## Networking & VPN

| App | Package | Source | What it's for |
|---|---|---|---|
| Proton VPN | `proton-vpn-gtk-app` | pacman | Personal VPN |
| Cisco Secure Client | `cisco-secure-client` | AUR | Work/school VPN |

```bash
sudo pacman -S proton-vpn-gtk-app
yay -S cisco-secure-client
```

---

## Flatpaks

| App | ID | What it's for |
|---|---|---|
| RustDesk | `com.rustdesk.RustDesk` | Remote desktop |
| PDF Arranger | `com.github.jeromerobert.pdfarranger` | Merge / split / rotate PDFs |
| Gear Lever | `it.mijorus.gearlever` | AppImage manager |
| Swifty Notes | `me.spaceinbox.swiftynotes` | Notes |
| Extension Manager | `com.mattjakeman.ExtensionManager` | GNOME extensions (GNOME base session) |

```bash
flatpak install flathub com.rustdesk.RustDesk com.github.jeromerobert.pdfarranger it.mijorus.gearlever me.spaceinbox.swiftynotes com.mattjakeman.ExtensionManager
```

---

## Fonts

| Font | Package | Source |
|---|---|---|
| JetBrains Mono Nerd | `ttf-jetbrains-mono-nerd` | pacman |
| Meslo Nerd | `ttf-meslo-nerd` | pacman |
| Ubuntu Nerd | `ttf-ubuntu-nerd` | pacman |
| Ubuntu Mono Nerd | `ttf-ubuntu-mono-nerd` | pacman |
| 0xProto Nerd | `ttf-0xproto-nerd` | pacman |
| Cantarell | `cantarell-fonts` | pacman |
| Noto (+ CJK + Emoji) | `noto-fonts`, `noto-fonts-cjk`, `noto-fonts-emoji` | pacman |
| Open Sans | `ttf-opensans` | pacman |
| DejaVu | `ttf-dejavu` | pacman |
| Liberation | `ttf-liberation` | pacman |
| Bitstream Vera | `ttf-bitstream-vera` | pacman |
| Ubuntu | manual | `~/.local/share/fonts/ubuntu/` |
| Ubuntu Sans | manual | `~/.local/share/fonts/ubuntu-sans/` |

```bash
sudo pacman -S ttf-jetbrains-mono-nerd ttf-meslo-nerd ttf-ubuntu-nerd ttf-ubuntu-mono-nerd ttf-0xproto-nerd cantarell-fonts noto-fonts noto-fonts-cjk noto-fonts-emoji ttf-opensans ttf-dejavu ttf-liberation ttf-bitstream-vera
```

---

## Cursors & Themes

| Theme | Package | Source | Used for |
|---|---|---|---|
| Yaru (GTK) | `yaru-gtk-theme` | AUR | GTK theme |
| Yaru (Icons) | `yaru-icon-theme` | AUR | Icon theme |
| Yaru (GNOME Shell) | `yaru-gnome-shell-theme` | AUR | Shell theme |
| Yaru (Sounds) | `yaru-sound-theme` | AUR | System sounds |
| Capitaine Cursors | `capitaine-cursors` | pacman | Cursor |
| nwg-look | `nwg-look` | pacman | GTK theme settings for Wayland |

```bash
sudo pacman -S capitaine-cursors nwg-look
yay -S yaru-gtk-theme yaru-icon-theme yaru-gnome-shell-theme yaru-sound-theme
```

---

## AUR Summary

All AUR packages in one place for easy tracking:

| Package | Category | Notes |
|---|---|---|
| `visual-studio-code-bin` | Development | No official repo alternative |
| `antigravity-ide` | Development | Google AI coding IDE |
| `android-studio` | Development | Official Android IDE |
| `google-chrome` | Daily Use | Chromium browser |
| `handy-bin` | Speech to Text | Offline speech-to-text |
| `cisco-secure-client` | Networking | Work/school VPN |
| `input-remapper-bin` | Utilities | Input remapping |
| `nirimod-git` | Shell Stack | Niri config GUI |
| `yaru-gtk-theme` | Themes | GTK theme |
| `yaru-icon-theme` | Themes | Icon theme |
| `yaru-gnome-shell-theme` | Themes | GNOME Shell theme |
| `yaru-sound-theme` | Themes | System sound theme |

### Install all AUR packages at once

```bash
yay -S visual-studio-code-bin antigravity-ide android-studio google-chrome handy-bin cisco-secure-client input-remapper-bin nirimod-git yaru-gtk-theme yaru-icon-theme yaru-gnome-shell-theme yaru-sound-theme
```

---

## Removed since last update

Kept here so a restore doesn't silently reinstall things that were dropped:

| Package | Why it's gone |
|---|---|
| `planify` | Uninstalled — no longer used for tasks |
| `flutter-bin` | Replaced by the manual SDK at `~/tools/flutter` |
| `grim`, `slurp` | Niri's built-in screenshot replaced them |
| `noctalia-git`, `noctalia-greeter-git` | Noctalia is now `noctalia` in the official repos; greeter unused |
| `discord`, `vesktop-bin` | Desktop chat clients no longer used |
| `paru` | Replaced by `yay` as the AUR helper |
