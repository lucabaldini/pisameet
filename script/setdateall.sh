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

for ((i=0; i<${#numero[@]}; i++)); do
    x=${numero[i]}
    ip=$((100 + x))
    echo "setting date on ppm$x"
    ssh pi@192.168.30.$ip "sudo date -s '2022-05-21 08:18:30'; exit;";
done



