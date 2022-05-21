#! /bin/bash

for (( x=1; x<=24; x++ ))
do
    ip=$((100 + x))
    echo "pulling git on ppm$x"
    ssh pi@192.168.30.$ip "cd pisameet; git pull; exit;";
done



