# Apps & Tools

A categorized list of everything installed and used on this system.

> **System:** CachyOS · Niri (Wayland) · Noctalia shell

> [!NOTE]
> Packages are tagged by source:
> `pacman` = official Arch or CachyOS repos · `AUR` = Arch User Repository
> The goal is to minimize AUR usage where possible.

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
| Discord | `discord` | pacman | Chat |
| Telegram | `telegram-desktop` | pacman | Chat |
| KDE Connect | `kdeconnect` | pacman | Phone ↔ desktop |
| Planify | `planify` | pacman | Task management |
| AB Download Manager | `ab-download-manager` | pacman (cachyos) | Download manager |

```bash
# Official / CachyOS repos
sudo pacman -S kitty starship brave-bin zen-browser-bin firefox discord telegram-desktop kdeconnect planify ab-download-manager

# AUR
paru -S google-chrome
```

---

## Development

| App | Package | Source | What it's for |
|---|---|---|---|
| VS Code | `visual-studio-code-bin` | AUR | Primary editor |
| Antigravity IDE | `antigravity-ide` | AUR | AI coding assistant |
| OpenCode | `opencode` | pacman | Terminal coding agent |
| Android Studio | `android-studio` | AUR | Android dev |
| Flutter | `flutter-bin` | AUR | Cross-platform UI |
| JupyterLab | `jupyterlab` | pacman | Python notebooks |
| GitHub Desktop | `github-desktop` | pacman | Git GUI |
| Git LFS | `git-lfs` | pacman | Large file support for Git |
| Docker | `docker`, `docker-compose` | pacman | Containers |

```bash
# Official / CachyOS repos
sudo pacman -S opencode jupyterlab github-desktop git-lfs docker docker-compose

# AUR
paru -S visual-studio-code-bin antigravity-ide android-studio flutter-bin
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
# Official / CachyOS repos
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
paru -S input-remapper-bin
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
| Noctalia | `noctalia-git` | AUR | Shell (bar, launcher, etc.) |
| NiriMod | `nirimod-git` | AUR | Visual config for Niri |
| Grim + Slurp | `grim`, `slurp` | pacman | Screenshots |
<!-- | snixembed | `snixembed-git` | AUR | Tray icon support | -->
| Proton VPN | `proton-vpn-gtk-app` | pacman | VPN |
| Cisco Secure Client | `cisco-secure-client` | AUR | Work/school VPN |
| Bazaar | `bazaar` | pacman | Flatpak app store |

```bash
# Official / CachyOS repos
sudo pacman -S niri grim slurp proton-vpn-gtk-app bazaar

# AUR
paru -S noctalia-git nirimod-git cisco-secure-client
```

---

## Networking & VPN

| App | Package | Source | What it's for |
|---|---|---|---|
| Proton VPN | `proton-vpn-gtk-app` | pacman | Personal VPN |
| Cisco Secure Client | `cisco-secure-client` | AUR | Work/school VPN |

```bash
sudo pacman -S proton-vpn-gtk-app
paru -S cisco-secure-client
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
| Capitaine Cursors | `capitaine-cursors` | pacman | Cursor |

```bash
sudo pacman -S capitaine-cursors
paru -S yaru-gtk-theme yaru-icon-theme yaru-gnome-shell-theme
```

---

## AUR Summary

All AUR packages in one place for easy tracking:

| Package | Category | Notes |
|---|---|---|
| `visual-studio-code-bin` | Development | No official repo alternative |
| `antigravity-ide` | Development | Google AI coding IDE |
| `android-studio` | Development | Official Android IDE |
| `flutter-bin` | Development | Flutter SDK |
| `google-chrome` | Daily Use | Chromium browser |
| `cisco-secure-client` | Networking | Work/school VPN |
| `input-remapper-bin` | Utilities | Input remapping |
| `noctalia-git` | Shell Stack | Noctalia shell *(core to setup)* |
| `noctalia-greeter-git` | Shell Stack | Greeter *(core to setup)* |
| `nirimod-git` | Shell Stack | Niri config GUI |
| `yaru-gtk-theme` | Themes | GTK theme |
| `yaru-icon-theme` | Themes | Icon theme |
| `yaru-gnome-shell-theme` | Themes | GNOME Shell theme |

### Install all AUR packages at once

```bash
paru -S visual-studio-code-bin antigravity-ide android-studio flutter-bin google-chrome cisco-secure-client input-remapper-bin noctalia-git noctalia-greeter-git nirimod-git yaru-gtk-theme yaru-icon-theme yaru-gnome-shell-theme
```
