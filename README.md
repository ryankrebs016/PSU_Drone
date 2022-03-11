# PSU_Drone
Code for Beacon's drone at psu

Requirements - RTKLIB, Adafruit_BBIO (not needed?)

-BB_pulser.py holds the scripts for communicating with the pulser with a beaglebone black
  through the pmod rs485 adapter
-start_log.sh continually checks the switch pin for low to high to determine if
  pulsing and logging should start
-end_log.sh continually checks the switch pin for high to low to determine if pulsing and
  logging should stop. calls a kill function to stop str2str
-setup_pins.sh sets the correct output on the gpio pin muxs

start_log.sh, end_log.sh, and setup_pins.sh need to have sudo permissions and need to
  have a service written /etc/systemd/system/ and enabled for startup
 
