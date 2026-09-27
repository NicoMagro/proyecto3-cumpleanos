#!/bin/bash
# Verifica que la version paralela de un resultado correcto con distinta
# cantidad de procesos. No pedimos que den el numero exacto de coincidencias
# porque cada proceso usa su propia semilla: pedimos que la probabilidad
# quede cerca de la teorica.

cd "$(dirname "$0")/.."

echo "Compilando..."
cc src/cumpleanos.c src/serial.c -o serial || exit 1
mpicc src/cumpleanos.c src/paralelo.c -o paralelo || exit 1

echo ""
echo "Serial:"
./serial 23 500000 | grep "Probabilidad simulada"

for p in 1 2 4
do
    echo ""
    echo "Paralelo con $p procesos:"
    mpirun --oversubscribe -n $p ./paralelo 23 500000 | grep "Probabilidad simulada"
done

echo ""
echo "Todas las corridas tienen que dar alrededor de 0.5073"
