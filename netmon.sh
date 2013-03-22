#!/bin/bash

while true ; do
if ifconfig wlan0 | grep -q "inet" ; then
 sleep 40
else
 echo "Reestablishing network..." $(date)
# ifup --force wlan0
# ifconfig wlan0 up
# Force DHCP renew lease
 dhcpcd -n wlan0
 sleep 10
fi
done
