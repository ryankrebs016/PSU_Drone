echo "starting log service" >> home/debian/bb_log.txt
live=$(cat /home/debian/config.txt)
if [ $live -eq "0" ]
then
	echo "lab mode"
	exit 0
fi

sleep 4.5

sw=$(cat /sys/class/gpio/gpio49/value)

while :
do
	tem=$(cat /sys/class/gpio/gpio49/value)
	if [ $tem -gt $sw ]
	then
		echo "starting pulsing"
		log="starting log "
		ti=$( date +%d%m%y%H%M%S )
		into_log="$log$ti"
		echo $into_log >> /home/debian/bb_log.txt
		tim=$( date +%d%m%y%H%M%S )
		python3 pulser.py 1
		str2str -in serial://ttyS2:115200#ubx -out /home/debian/gps_log/$tim.ubx
	fi
	sw=$tem
	sleep 1
done
