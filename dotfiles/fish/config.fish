if status is-interactive
    set fish_greeting

    if command -v starship &>/dev/null
        starship init fish | source
    end

    if test -f ~/.local/state/quickshell/user/generated/terminal/sequences.txt
        cat ~/.local/state/quickshell/user/generated/terminal/sequences.txt
    end

    alias clear "printf '\033[2J\033[3J\033[1;1H'" # fix: kitty doesn't clear scrollback properly
    alias celar "printf '\033[2J\033[3J\033[1;1H'"
    alias claer "printf '\033[2J\033[3J\033[1;1H'"
    if command -v eza &>/dev/null
        alias ls 'eza --icons'
    end
    alias q 'qs -c ii'
end

function postexec_newline --on-event fish_postexec
    echo ""
end

set -Ux CHROME_EXECUTABLE /usr/bin/google-chrome-stable
set -gx PNPM_HOME "$HOME/.local/share/pnpm"
fish_add_path $PNPM_HOME/bin
fish_add_path $HOME/.local/share/pnpm/bin
fish_add_path $HOME/.npm-global/bin
fish_add_path $HOME/.local/bin

# flutter
fish_add_path $HOME/tools/flutter/bin
fish_add_path $HOME/.pub-cache/bin

zoxide init fish | source

