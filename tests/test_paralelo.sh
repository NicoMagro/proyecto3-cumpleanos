#!/bin/bash
# Verifica que la version paralela de un resultado correcto con distinta
# cantidad de procesos. No pedimos que den el numero exacto de coincidencias
# porque cada proceso usa su propia semilla: pedimos que la probabilidad
# quede cerca de la teorica.

cd "$(dirname "$0")/.."

echo "Compilando..."
mpicc src/cumpleanos.c src/serial.c -o serial || exit 1
mpicc src/cumpleanos.c src/paralelo-estatico.c -o paralelo-estatico || exit 1
mpicc src/cumpleanos.c src/paralelo-dinamico.c -o paralelo-dinamico || exit 1

echo ""
echo "Serial:"
./serial 23 500000 | grep "Probabilidad simulada"

for p in 1 2 4
do
    echo ""
    echo "Paralelo estatico con $p procesos:"
    mpirun --oversubscribe -n $p ./paralelo-estatico 23 500000 | grep "Probabilidad simulada"
done

for p in 2 4
do
    echo ""
    echo "Paralelo dinamico con $p procesos:"
    mpirun --oversubscribe -n $p ./paralelo-dinamico 23 500000 5000 | grep "Probabilidad simulada"
done

echo ""
echo "Todas las corridas tienen que dar alrededor de 0.5073"
