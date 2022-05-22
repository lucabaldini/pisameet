#! /bin/bash

for (( x=0; x<=24; x++ ))
do
    ip=$((100 + x))
    echo "rebooting ppm$x"
    ssh pi@192.168.30.$ip "sudo reboot now";
done



