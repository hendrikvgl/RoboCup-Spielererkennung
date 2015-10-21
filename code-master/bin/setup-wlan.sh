#! /bin/bash
if [ $# -ne 2 ] ; then
    echo "usage: $0 <robot_ip> <robot_number>"
    exit 1
fi
echo $1
echo $2
echo "Lösche W-Lans"
ssh darwin@$1 sudo rm -f  /etc/NetworkManager/system-connections/\*
ssh darwin@$1 sudo rm -f  /tmp/net/\*
echo "Kopieren der neuen W-Lans"
rsync -Pauz ../infrastruktur/wlan-config/* darwin@$1:/tmp/net/
ssh darwin@$1 "\
    sed 's/99.99.99.99/192.168.107.1$2/g' --in-place /tmp/net/* ; echo 1"
ssh darwin@$1 "sudo cp /tmp/net/* /etc/NetworkManager/system-connections/"
ssh darwin@$1 "sudo chown root:root /etc/NetworkManager/system-connections/*"
ssh darwin@$1 "sudo chmod 600 /etc/NetworkManager/system-connections/*"
echo "nach W-Lans suchen"
ssh darwin@$1 nm-tool
