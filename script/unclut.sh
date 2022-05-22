#! /bin/bash

for (( x=0; x<=24; x++ ))
do
    ip=$((100 + x))
    echo "unclut ppm$x"
    ssh pi@192.168.30.$ip "cd pisameet; git pull; cp unclut.desktop ../.config/autostart; sudo reboot now;"
done



