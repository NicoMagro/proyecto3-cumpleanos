# Como compilar y correr

## Compilar

```bash
mpicc src/cumpleanos.c src/serial.c -o serial
mpicc src/cumpleanos.c src/paralelo-estatico.c -o paralelo-estatico
mpicc src/cumpleanos.c src/paralelo-dinamico.c -o paralelo-dinamico
```

## Correr

Los programas reciben dos parametros opcionales: la cantidad de personas
por grupo (K) y la cantidad de grupos a simular. En el dinamico se puede
pasar ademas el tamanio de bloque:

```bash
./serial 23 1000000
mpirun -n 4 ./paralelo-estatico 23 1000000
mpirun -n 4 ./paralelo-dinamico 23 1000000 5000
```

Si la computadora no tiene tantos nucleos, se agrega `--oversubscribe`:

```bash
mpirun --oversubscribe -n 8 ./paralelo-estatico 23 1000000
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
    mpirun --oversubscribe -n 4 ./paralelo-estatico 23 $t | grep "^csv"
done
```

## Experimento 2: curva P(K)

La probabilidad para distintos tamanios de grupo.

```bash
for k in 5 10 15 20 23 25 30 40 50 60 70
do
    mpirun --oversubscribe -n 4 ./paralelo-estatico $k 1000000 | grep "^csv"
done
```

## Experimento 3: speedup (automatizado con `speedup.sh`)

Existe el script `speedup.sh` para correr las mediciones serial, estática y
dinámica de forma automática y guardar la salida en `resultados/speedup.csv`:

```bash
./speedup.sh [k] [grupos] [repeticiones]
# Por defecto corre con K=23, 2.000.000 grupos y 10 repeticiones:
./speedup.sh 23 2000000 10
```

Se puede modificar a gusto dependiendo de la maquina o cluster, cambiando las
variables al inicio del script:
- `PROCESOS`: lista de procesos a probar (ej. `"2 4 6 8"` en laptop o `"2 4 6 8 12 16 24 32 48 64 96"` en cluster).
- `BLOQUES`: tamaños de bloque a evaluar en el dinámico.

Despues, para generar los graficos:

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
