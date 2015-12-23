#!/bin/env bash
STATE=1;

while [ $STATE == 1 ]; do
    #do a ping and check that its not a default message or change to grep for something else
    STATE=$(ping -q -w 1 -c 1 `ip r | grep default | cut -d ' ' -f 3` > /dev/null && echo 0 || echo 1)

    #sleep for 2 seconds and try again
    sleep 2
done

IP=$(ifconfig wlan0 | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*')
IP_PREF=$(echo $IP | grep -Eo '([0-9]{1,3}\.){3}')

GWIP=$(/sbin/ip route | awk '/default/ { print $3 }')

sed 's/localip \(.*\)/localip '"$IP"'/g' /etc/pptpd.conf -i
sed 's/remoteip \(.*\)/remoteip '"$IP_PREF"'234-238/g' /etc/pptpd.conf -i

sed 's/ms-dns 1\(.*\)/ms-dns '"$GWIP"'/g' /etc/ppp/pptpd-options -i
# upnpc -a $IP 1723 1723 TCP
