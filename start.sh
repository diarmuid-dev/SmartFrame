#!/bin/sh
mount /dev/sda1 /media/usb/
python3 shutdownBtn.py &
matchbox-window-manager &
python3 images.py  /media/usb/images/ 10
