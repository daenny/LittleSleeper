#!/bin/env sh
while true; do
    # testing...
    LC_ALL=C nmcli -t -f DEVICE,STATE dev | grep -q "^wlan0:connected$"
    if [ $? -eq 0 ]; then
	break
    else
	# not connected, sleeping for a second
	sleep 1
    fi
done



IP=$(ifconfig wlan0 | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*')
IP_PREF=$(echo $IP | grep -Eo '([0-9]{1,3}\.){3}')
sed 's/localip \(.*\)/localip '"$IP"'/g' /etc/pptpd.conf -i
sed 's/remoteip \(.*\)/remoteip '"$IP_PREF"'234-238/g' /etc/pptpd.conf -i

# upnpc -a $IP 1723 1723 TCP
