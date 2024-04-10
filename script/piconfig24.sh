#! /bin/bash


# Nome del file contenente i valori
file="listapi.txt"

# Verifica se il file esiste
if [ ! -f "$file" ]; then
    echo "Il file $file non esiste."
    exit 1
fi

# Inizializza l'array per memorizzare i valori
numero=()
schermo=()

# Leggi i valori dal file e memorizzali nell'array
while IFS=" " read -r pinum screen; do
    numero+=("$pinum")
    schermo+=("$screen")
done < "$file"

# Stampa i valori letti dal file
#echo "Valori letti dal file:"
#echo "Prima Colonna (Numero): ${numero[*]}"
#echo "Seconda Colonna (Schermo): ${schermo[*]}"

for x in "${numero[@]}"
do
    ip=$((100 + x))
    echo " updating ppm$x"
    ssh pi@192.168.30.$ip "rm -Rf pisameet; mkdir pisameet; cd pisameet;  git config --global http.proxy http://gridsquid1.pi.infn.it:3128; git config --global http.sslverify false; git clone https://github.com/lucabaldini/pisameet.git ./; git remote set-url origin https://github.com/lucabaldini/pisameet.git; exit;";
done


