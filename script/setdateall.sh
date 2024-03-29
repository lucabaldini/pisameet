#! /bin/bash

for (( x=0; x<=24; x++ ))
do
    ip=$((100 + x))
    echo "setting date on ppm$x"
    ssh pi@192.168.30.$ip "sudo date -s '2022-05-21 08:18:30'; exit;";
done



