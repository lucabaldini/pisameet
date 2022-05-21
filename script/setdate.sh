#! /bin/bash

for x in $@
do
    ip=$((9 + x))
    echo "pulling git on ppm$x"
    ssh pi@192.168.2.$ip "sudo date -s '2022-05-21 08:13:30'; exit;";
done



