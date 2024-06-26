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
echo "copying file to ppm$x"

    scp scp.sh pi@192.168.30.$ip:
done



