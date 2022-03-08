echo "starting end log service" >> /home/debian/bb_log.txt
live=$(cat /home/debian/config.txt)
if [ $live -eq "0" ]
then
	echo "lab mode"
	exit 0
fi

sleep 5
pid_str=$(pgrep str2str)
sw=$(cat /sys/class/gpio/gpio49/value)
while :
do
	tem=$(cat /sys/class/gpio/gpio49/value)
	piss=$(pgrep srt2srt)
	if [ $tem -lt $sw ]
	then
		log="ending log "
		ti=$( date +%d%m%y%H%M%S )
		into_log="$log$ti"
		echo $into_log >> /home/debian/bb_log.txt
		echo "killing str and turning off pulser"
		python3 pulser.py 0
		pkill "str2str"
	fi
	sw=$tem
	sleep 1
done

