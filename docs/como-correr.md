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

## Experimento 1: convergencia y precisión (automatizado con `precision.sh`)

Cuantos más grupos simulamos, más se acerca el resultado al valor teórico (convergencia $\mathcal{O}(1/\sqrt{N})$ de Monte Carlo).

Para correr automáticamente el barrido denso de grupos y registrar la evolución de la precisión:

```bash
./precision.sh [k] [procesos]
# Por defecto corre con K=23 y 8 procesos:
./precision.sh 23 8
```

Al terminar las mediciones, el script ejecuta automáticamente `python3 src/graficos_precision.py` para generar los gráficos `resultados/precision/evolucion_probabilidad.png` y `resultados/precision/evolucion_error.png`.

## Experimento 2: curva P(K) (automatizado con `curva_pk.sh`)

Evalúa la probabilidad de coincidencia para distintos tamaños de grupo $K$ (desde 2 hasta 80 personas) y la compara contra el valor teórico.

```bash
./curva_pk.sh [grupos] [procesos]
# Por defecto corre con 1.000.000 de grupos y 8 procesos:
./curva_pk.sh 1000000 8
```

Al terminar las mediciones, el script ejecuta automáticamente `python3 src/graficos_pk.py` y genera `resultados/curva_pk/curva_pk.png`.

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

Al terminar las mediciones, el script ejecuta automáticamente `python3 src/graficos.py`.
Si hace falta regenerar los gráficos a mano:

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
