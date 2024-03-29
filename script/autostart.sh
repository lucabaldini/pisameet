#! /bin/bash

for (( x=1; x<=20; x++ ))
do
    ip=$((100 + x))
    echo "rebootin ppm$x"
    ssh pi@192.168.30.$ip "cd pisameet; git pull; rm ../.config/autostart/pisameet*; cp pisameet_slideshow.desktop ../.config/autostart/; sudo reboot now;";
done



