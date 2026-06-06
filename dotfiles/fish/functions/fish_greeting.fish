function fish_greeting
    set -l accent (set_color -o cyan) 
    set -l label  (set_color 666)
    set -l icon   (set_color 888)
    set -l val    (set_color normal)
    set -l dim    (set_color 444)

    set -l os_info  (awk -F= '/^PRETTY_NAME/{print $2}' /etc/os-release | tr -d '"')
    set -l kernel   (uname -r | cut -d'-' -f1)
    set -l uptime   (uptime -p | sed 's/up //')
    set -l ram      (free -h | awk '/^Mem:/ {printf "%s / %s", $3, $2}' | sed -E 's/Gi?/G/g')
    set -l disk     (df -h / | awk 'NR==2 {print $3 " / " $2 " ("$5" used)"}')
    
    set -l cpu_info (awk -F': ' '/model name/ {gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2; exit}' /proc/cpuinfo | sed 's/(R)//g;s/(TM)//g')
    
    set -l gpu_info (nvidia-smi --query-gpu=name,temperature.gpu --format=csv,noheader 2>/dev/null | awk -F', ' '{print $1 "  |  " $2 "°C"}')
    if test -z "$gpu_info"
        set gpu_info "N/A or Powered Off"
    end

    set -l ip (ip route get 1.1.1.1 2>/dev/null | awk '{print $7; exit}')
    if test -z "$ip"
        set ip "Offline (127.0.0.1)"
    end

    set -l pkgs (command -v pacman >/dev/null; and pacman -Qq 2>/dev/null | wc -l; or echo "0")

    set -l date_str (date "+%a, %d %b %Y")
    set -l time_str (date "+%I:%M %p")

    set -l quotes \
        "Talk is cheap. Show me the code." \
        "It works on my machine." \
        "Have you tried turning it off and on again?" \
        "It's not a bug, it's an undocumented feature." \
        "Documentation? The code IS the documentation." \
        "Eat. Sleep. Rebase. Repeat." \
        "To err is human. To blame git is divine." \
        "In case of fire: git commit, git push, evacuate." \
        "undefined is not a function. Story of my life." \
        "First, solve the problem. Then, write the code." \
        "Make it work, make it right, make it fast." \
        "Simplicity is the soul of efficiency." \
        "A user interface is like a joke. If you have to explain it, it's not that good." \
        "The best error message is the one that never shows up." \
        "Hardware: The parts of a computer system that can be kicked." \
        "Optimism is an occupational hazard of programming." \
        "Before software can be reusable it first has to be usable."

    set -l quote $quotes[(random 1 (count $quotes))]

    echo ""
    echo "  $accent Dhanraj $dim — $val$date_str $dim· $val$time_str"
    echo ""
    printf "  $icon   $label os      $val%s\n" "$os_info"
    printf "  $icon   $label kernel  $val%s\n" "$kernel"
    printf "  $icon   $label cpu     $val%s\n" "$cpu_info"
    printf "  $icon 󰢮  $label gpu     $val%s\n" "$gpu_info"
    printf "  $icon   $label ram     $val%s\n" "$ram"
    printf "  $icon 󰋊  $label disk    $val%s\n" "$disk"
    printf "  $icon 󰏗  $label pkgs    $val%s\n" "$pkgs"
    printf "  $icon 󰖟  $label ip      $val%s\n" "$ip"
    printf "  $icon 󰔛  $label uptime  $val%s\n" "$uptime"
    echo ""
    
    set -l quote_length (string length "$quote")
    set -l divider (string repeat -n $quote_length "─")
    
    echo "  $dim$quote"
    echo "  $dim$divider$val"
    echo ""
end
