#!/bin/bash

while true ; do
if ifconfig wlan0 | grep -q "inet addr" ; then
 sleep 30
else
 echo "Reestablishing network..." $(date)
 ifup --force wlan0
 sleep 10
fi
done
