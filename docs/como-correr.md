# Como compilar y correr

No hace falta Makefile: son dos comandos.

## Compilar

```bash
cc src/cumpleanos.c src/serial.c -o serial
mpicc src/cumpleanos.c src/paralelo.c -o paralelo
```

## Correr

Los dos programas reciben dos parametros opcionales: la cantidad de personas
por grupo (K) y la cantidad de grupos a simular.

```bash
./serial 23 1000000
mpirun -n 4 ./paralelo 23 1000000
```

Si la computadora no tiene tantos nucleos, se agrega `--oversubscribe`:

```bash
mpirun --oversubscribe -n 8 ./paralelo 23 1000000
```

## Correr los tests

```bash
cc src/cumpleanos.c tests/test_cumpleanos.c -o test -lm
./test

./tests/test_paralelo.sh
```

## Experimento 1: convergencia

Cuantos mas grupos simulamos, mas se acerca el resultado a la teoria.

```bash
for t in 1000 10000 100000 1000000 10000000
do
    mpirun --oversubscribe -n 4 ./paralelo 23 $t | grep "^csv"
done
```

## Experimento 2: curva P(K)

La probabilidad para distintos tamanios de grupo.

```bash
for k in 5 10 15 20 23 25 30 40 50 60 70
do
    mpirun --oversubscribe -n 4 ./paralelo $k 1000000 | grep "^csv"
done
```

## Experimento 3: speedup

La consigna pide correr varias veces y quedarse con la mediana, asi que
repetimos cada configuracion 5 veces.

```bash
# Guardamos el encabezado una sola vez
echo "tipo,k,grupos,procesos,p_simulada,p_teorica,tiempo" > resultados/speedup.csv

for repeticion in 1 2 3 4 5
do
    ./serial 23 5000000 | grep "^csv" >> resultados/speedup.csv

    for p in 2 4 6 8
    do
        mpirun --oversubscribe -n $p ./paralelo 23 5000000 | grep "^csv" >> resultados/speedup.csv
    done
done
```

Despues:

```bash
python3 src/graficos.py
```

## Datos de la computadora

Antes de guardar resultados, anotar en `resultados/` con que maquina se corrio:

```bash
# En Mac
sysctl -n machdep.cpu.brand_string; sysctl -n hw.physicalcpu

# En Linux
lscpu | grep "Model name"; nproc
```
