#!/usr/bin/env bash
apt install python3-hid
#apt install python3-hidapi
install -o0 -g0 -m0644 udev/60-rfideas-permissions.rules /etc/udev/rules.d/
udevadm control --reload-rules

