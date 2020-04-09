#!/usr/bin/env bash

SOURCE=/root/maintenance.html
LOCATION=/var/www/maintenance.html

if [[ $1 = "on" ]]
then
    cp ${SOURCE} ${LOCATION}
elif [[ $1 = "off" ]]
then
    # TODO: check if location exists to prevent errors
    rm ${LOCATION}
else
    echo -e "Helper script to enable a maintenance page.\n\nMaintenance page should be located in /root/maintenance.html\n"
    echo -e "\tUsage: maintenance [on|off]\n"
    echo -e "\t\ton:\t enables maintenance mode\n"
    echo -e "\t\toff:\t enables maintenance mode\n"
fi
