#!/bin/sh -e
echo "booted at $( date +%d%m%y%H%M%S )" >> /home/debian/bb_log.txt
config-pin P9_21 uart
config-pin P9_22 uart
config-pin P9_23 gpio
config-pin P9_15 gpio

echo out > /sys/class/gpio/gpio48/direction
echo in > /sys/class/gpio/gpio49/direction
echo 1 > /sys/class/gpio/gpio48/value

exit 0
