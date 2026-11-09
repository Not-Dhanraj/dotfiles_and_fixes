function restart_sound_controllers --description "Restart the USB and HDMI audio controllers that get stuck after sleep"
    restart_one_controller xhci_hcd 0000:06:00.4       # USB ports (whatever DAC is plugged in) + bluetooth
    restart_one_controller snd_hda_intel 0000:01:00.1  # audio out the HDMI/DisplayPort sockets
end

function restart_one_controller --description "Switch a single piece of hardware off, then back on"
    set -l driver $argv[1]
    set -l address $argv[2]

    echo $address | sudo tee /sys/bus/pci/drivers/$driver/unbind >/dev/null
    sleep 3
    echo $address | sudo tee /sys/bus/pci/drivers/$driver/bind >/dev/null
end
