# Paradoja del Cumpleanios con MPI

Proyecto 3 - Evaluacion Parcial 1
Metodos Numericos II / Computacion Cientifica - FACET, UNT - 2026

## De que se trata

En un grupo de K personas, ¿que probabilidad hay de que al menos dos cumplan
anios el mismo dia? La respuesta es sorprendente: con solo 23 personas la
probabilidad ya pasa el 50%.

El valor teorico se calcula con:

    P(K) = 1 - (365/365) * (364/365) * ... * ((365-K+1)/365)

En este proyecto llegamos al mismo resultado por simulacion: generamos millones
de grupos con cumpleanios al azar y contamos en cuantos hubo coincidencia.
Como cada grupo es independiente de los demas, el trabajo se puede repartir
entre varios procesos con MPI.

## Integrantes

- Angel Nicolas Magro
- Fran Leccese
- Sergio Zair Lobo

## Como usarlo

```bash
mpicc src/cumpleanos.c src/serial.c -o serial
mpicc src/cumpleanos.c src/paralelo-estatico.c -o paralelo-estatico
mpicc src/cumpleanos.c src/paralelo-dinamico.c -o paralelo-dinamico

./serial 23 1000000
mpirun -n 4 ./paralelo-estatico 23 1000000
mpirun -n 4 ./paralelo-dinamico 23 1000000 5000
```

Mas detalles y los comandos de los experimentos en [docs/como-correr.md](docs/como-correr.md).

## Archivos

| Carpeta | Que hay adentro |
|---|---|
| `src/cumpleanos.c` / `.h` | La simulacion y la formula teorica |
| `src/serial.c` | Programa serial, sirve de referencia (T1) para el speedup |
| `src/paralelo-estatico.c` | Programa MPI con reparto fijo de grupos |
| `src/paralelo-dinamico.c` | Programa MPI maestro-trabajadores con bloques |
| `src/graficos.py` y `graficos_*.py` | Generan los graficos a partir de los resultados |
| `tests/` | Tests de las funciones y de la version paralela |
| `docs/` | Informe, roadmap y como correr todo |
| `resultados/` | Los CSV y los graficos de cada maquina |

## Resultados

Todas las mediciones usan 2.000.000 de grupos y K=23. Se comparan dos
esquemas: **estatico** (reparto fijo) y **dinamico** (maestro-trabajadores).
Entre parentesis, la cantidad de procesos donde se dio el mejor speedup.

| Maquina | Nucleos / Hilos | T. serial (s) | Sp. Estatico (max) | Sp. Dinamico (max) |
|---|---|---|---|---|
| Notebook Nicolas (Apple M2 Pro) | 10 nucleos | 0.419 | 9.12 (16) | 8.93 (11) |
| Sergio (SMT desactivado) | 8 nucleos / 8 hilos | 0.591 | 8.20 (8) | 7.34 (21) |
| Sergio (SMT activado) | 8 nucleos / 16 hilos | 0.592 | 11.61 (16) | 11.17 (24) |
| Cluster CCAD UNC | 128 CPU (cuota 96) | 2.319 | 89.21 (96) | 92.78 (192) |
| Notebook Francisco (ASUS TUF) | 4 nucleos / 8 hilos | 1.812 | 6.07 (8) | 6.03 (17) |

Conclusiones principales:

- El esquema **estatico** escala casi de forma lineal mientras haya nucleos
  reales (eficiencia cercana al 100% hasta saturar).
- Con SMT y sobreasignacion el **dinamico** termina ganando porque oculta la
  latencia de comunicacion (p. ej. 192 procesos en el cluster: 0.025 s vs
  0.036 s del estatico).
- El tamanio de bloque optimo del dinamico ronda los 425-4.255 grupos.

Detalle completo, graficos y mapas de calor en [docs/informe.md](docs/informe.md).
