#!/bin/bash
# Mide el rendimiento de las versiones serial, paralelo-estatico y paralelo-dinamico
# variando la cantidad de procesos y el tamaño de bloque.
# Uso: ./speedup.sh [k] [grupos] [repeticiones]

K=${1:-23}
GRUPOS=${2:-2000000}
REPETICIONES=${3:-10}

# Configuracion de la prueba
PROCESOS="2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24"
BLOQUES="1 4 42 425 4255 42553 200000 1000000"
SALIDA=resultados/speedup.csv

mkdir -p resultados
#echo "tipo,k,grupos,procesos,bloque,p_simulada,p_teorica,tiempo" > $SALIDA

for repeticion in $(seq 1 $REPETICIONES)
do
    echo "Repeticion $repeticion de $REPETICIONES"

    # Corrida del serial
    mpirun -n 1 ./serial $K $GRUPOS | grep "^csv" | sed 's/^csv/serial/' >> $SALIDA

    for p in $PROCESOS
    do
        # Corrida del estatico
        mpirun --oversubscribe -n $p ./paralelo-estatico $K $GRUPOS | grep "^csv" | sed 's/^csv/estatico/' >> $SALIDA
        
        # Corridas del dinamico iterando por cada tamano de bloque
        for b in $BLOQUES
        do
            mpirun --oversubscribe -n $p ./paralelo-dinamico $K $GRUPOS $b | grep "^csv" | sed 's/^csv/dinamico/' >> $SALIDA
        done
    done
done

echo "Listo: $SALIDA"