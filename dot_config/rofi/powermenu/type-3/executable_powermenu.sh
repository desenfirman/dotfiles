#!/usr/bin/env bash

## Author : Aditya Shakya (adi1090x)
## Github : @adi1090x
#
## Rofi   : Power Menu
#
## Available Styles
#
## style-1   style-2   style-3   style-4   style-5

# Current Theme
dir="$HOME/.config/rofi/powermenu/type-3"
theme='style-1'

# CMDs
uptime="`uptime -p | sed -e 's/up //g'`"
host=`hostname`

# Options
shutdown=''
reboot=''
lock=''
suspend=''
logout=''
yes=''
no=''

# Rofi CMD
rofi_cmd() {
    /home/mis-stf08-dese/.local/bin/rofi -dmenu \
        -kb-cancel Escape \
        -p "Uptime: $uptime" \
        -mesg "Uptime: $uptime" \
        -theme "${dir}/${theme}.rasi"
}

# Confirmation CMD
confirm_cmd() {
    /home/mis-stf08-dese/.local/bin/rofi -dmenu \
        -kb-cancel Escape \
        -p 'Confirmation' \
        -mesg 'Are you Sure?' \
        -theme "${dir}/shared/confirm.rasi"
}

# Ask for confirmation
confirm_exit() {
	echo -e "$yes\n$no" | confirm_cmd
}

# Pass variables to rofi dmenu
run_rofi() {
	echo -e "$lock\n$suspend\n$logout\n$reboot\n$shutdown" | rofi_cmd
}

# Execute Command
run_cmd() {
    selected="$(confirm_exit)"
    [[ "$selected" == "$yes" ]] || exit 0

    case "$1" in
        --shutdown) systemctl poweroff ;;
        --reboot) systemctl reboot ;;
        --suspend) systemctl suspend ;;
        --logout) loginctl terminate-session "$XDG_SESSION_ID" ;;
    esac
}

# Actions
chosen="$(run_rofi)"
case ${chosen} in
    $shutdown)
		run_cmd --shutdown
        ;;
    $reboot)
		run_cmd --reboot
        ;;
    $lock)
        loginctl lock-session "$XDG_SESSION_ID"
        ;;
    $suspend)
		run_cmd --suspend
        ;;
    $logout)
		run_cmd --logout
        ;;
esac
