#!/bin/bash

delay=0.5

masterExec="python ah_master.py"
yeelightExec="python yeelights.py yeelight.cfg"
comfeeExec="python comfee.py comfee.cfg"
shellyExec="python shelly.py shelly.cfg"
datetimeExec="python datetime_publisher.py 127.0.0.1 1883"


function stopall() {
	###
	### Kills all previous instances in the system
	###
	echo -n " - Killing all previous instances created by Automated Home . . . "
	sleep $delay
	
	kill -SIGINT $(pgrep -f "$masterExec") &> /dev/null
	kill -SIGINT $(pgrep -f "$yeelightExec") &> /dev/null
	kill -SIGINT $(pgrep -f "$comfeeExec")  &> /dev/null
	kill -SIGINT $(pgrep -f "$shellyExec")  &> /dev/null
	kill -SIGINT $(pgrep -f "$datetimeExec")  &> /dev/null

	echo "$Green [ OK ] $Normal"
	echo ""
	
	return 0
}

function startall() {
	
	###
	### Launching the Automated Home Master
	###
	echo -n " - Launching the Automated Home Master . . . "
	sleep $delay
	$masterExec & &>> /dev/null
	echo "$Green [ OK ] $Normal"

	###
	### Launching the Yeelight
	###
	echo -n " - Launching the Yeelight Manager . . . "
	sleep $delay
	$yeelightExec & &>> /dev/null
	echo "$Green [ OK ] $Normal"

	###
	### Launching the Comfee 
	###
	echo -n " - Launching the Comfee Manager . . . "
	sleep $delay
	$comfeeExec & &>> /dev/null
	echo "$Green [ OK ] $Normal"

	###
	### Launching the Shelly
	###
	echo -n " - Launching the Shelly Manager . . . "
	sleep $delay
	$shellyExec & &>> /dev/null
	echo "$Green [ OK ] $Normal"

	###
	### Launching the Datetime Service
	###
	echo -n " - Launching the Datetime Service . . . "
	sleep $delay
	$datetimeExec & &>> /dev/null
	echo "$Green [ OK ] $Normal"
	
    echo ""
	return 0
}

function version() {
	printf "\nAutomated Home Service Version 0.1.1\n"
	printf "\nCreated on October, 27 2024 by ftcid\n"
	printf "and distributed under GPL License\n\n"
	
	
	return 0
}

function cleanlogs() {
	###
	### Delete all logs created
	###
	echo -n " - Cleaning all logs . . . "
	rm -rf *.log &> /dev/null
	echo "$Green [ OK ] $Normal"
	echo ""
	
	return 0
}


#
# Here it is the different sections to launch the programs for the Automated Home . . . 
#
Green=$'\e[1;32m'
Normal=$'\e[00m'

#\[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w \$\[\033[00m\]

if [ "$1" == "start" ]; then
	version
	printf "Stopping existing instances of Automated Home Service and its modules:\n"
	stopall
	printf "Starting Automated Home Service and its modules:\n"
	startall
	shift
elif [ "$1" == "stop" ]; then
	version
	printf "Stopping Automated Home Service and its modules:\n"
	stopall
	shift
elif [ "$1" == "version" ]; then
	version
	shift
elif [ "$1" == "cleanlogs" ]; then
	version
	printf "Cleaning all logs created by Automated Home Service and its modules:\n"
	cleanlogs
	shift
else
	printf "Usage: ./automatedhome.sh [ start | stop | cleanlogs | version ]\n\n"
fi
