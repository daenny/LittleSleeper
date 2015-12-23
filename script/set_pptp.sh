#!/bin/env sh
IP=$(ifconfig wlan0 | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*')
IP_PREF=$(echo $IP | grep -Eo '([0-9]{1,3}\.){3}')
sed 's/localip \(.*\)/localip '"$IP"'/g' /etc/pptpd.conf -i
sed 's/remoteip \(.*\)/remoteip '"$IP_PREF"'234-238/g' /etc/pptpd.conf -i

# upnpc -a $IP 1723 1723 TCP
