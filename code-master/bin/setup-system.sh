#! /bin/bash

declare -A IP_ADDR
IP_ADDR[glados]=192.168.108.11
IP_ADDR[wheatley]=192.168.108.12
IP_ADDR[atlas]=192.168.108.13
IP_ADDR[tamara]=192.168.108.14
IP_ADDR[wilma]=192.168.108.15
IP_ADDR[fiona]=192.168.108.16

function uuid() {
    python  -c 'import uuid; print uuid.uuid1()'
}

if [ $# -ne 1 ] ; then
    echo "usage: $0 /dev/sdX"
    exit 1
fi

if [ $(whoami) != "root" ] ; then
    echo "Skript als root ausführen"
    exit 2
fi

if ! which pv > /dev/null ; then
    echo "Bitte erst 'pv' installieren: apt-get install pv"
    exit 3
fi

# Wohin soll installiert werden?
USB=$1
echo "Stick: $USB"

# Wie soll der Name des Ziels heißen?
read -p "Name des Roboters: " NAME

IP=${IP_ADDR[$NAME]}
echo "IP-Adresse ist dann '$IP'."

if [ "${COPY:-yes}" == "yes" ] ; then
        echo "Beschreibe den Stick $USB..."
#        (zcat system.raw.gz | pv -B 512k | dd bs=4M of=$USB) || ( echo "Fail writing system"  && exit 1)
        (pv -B 512k system.raw | dd bs=4M of=$USB) || (echo "Fail writing system" && exit 1)

        sync

        echo "Lese Partitionstabelle neu ein"
        blockdev --rereadpt $USB
fi

sync

echo "Binde das kopierte Dateisystem ein"
TEMP=$(mktemp -d /tmp/darwinXXXX)
mount ${USB}1 $TEMP

echo "Setze Hostname auf '$NAME'..."
echo $NAME > $TEMP/etc/hostname

echo "Setze Hostname in hosts"
sed s/robot/$NAME/g --in-place $TEMP/etc/hosts

UUID_OLD=$(egrep -o '[a-f0-9]{8}(-[a-f0-9]{4}){3}-[a-f0-9]{12}' $TEMP/boot/grub/grub.cfg | head -n1)
UUID_NEW=$(uuid)
echo "Korrigiere UUID in fstab und grub.cfg"
echo "  von  $UUID_OLD"
echo "  nach $UUID_NEW"

sed s/$UUID_OLD/$UUID_NEW/g --in-place $TEMP/boot/grub/grub.cfg
sed s/$UUID_OLD/$UUID_NEW/g --in-place $TEMP/etc/fstab

echo "Setze die IP Adresse"
IP_OLD=$(egrep -o '1[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' $TEMP/etc/NetworkManager/system-connections/HL_KID_C | head -n1)
sed s/$IP_OLD/$IP/g --in-place $TEMP/etc/NetworkManager/system-connections/HL_KID_C

echo "Ausbinden des Dateisystems..."
# Wieder aufräumen
for i in 1 2 3 4 5 ; do
    sleep 1
    umount $TEMP && rmdir $TEMP && break
done

echo "Ändere die UUID der Partition"
tune2fs -U $UUID_NEW ${USB}1

echo "$NAME ist einsatzbereit!"
