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
cc src/cumpleanos.c src/serial.c -o serial
mpicc src/cumpleanos.c src/paralelo.c -o paralelo

./serial 23 1000000
mpirun -n 4 ./paralelo 23 1000000
```

Mas detalles y los comandos de los experimentos en [docs/como-correr.md](docs/como-correr.md).

## Archivos

| Carpeta | Que hay adentro |
|---|---|
| `src/cumpleanos.c` | La simulacion y la formula teorica |
| `src/serial.c` | Programa serial, sirve de referencia para el speedup |
| `src/paralelo.c` | Programa con MPI |
| `src/graficos.py` | Genera los graficos a partir de los resultados |
| `tests/` | Tests de las funciones y de la version paralela |
| `docs/` | Informe, bibliografia y como correr todo |
| `resultados/` | Los CSV y los graficos de cada maquina |

## Resultado que ya tenemos

Speedup medido en la notebook de Nicolas (2 millones de grupos, K=23,
mediana de 3 corridas):

| Procesos | Tiempo | Speedup | Eficiencia |
|---|---|---|---|
| 1 | 1.327 s | 1.00 | 1.00 |
| 2 | 0.670 s | 1.98 | 0.99 |
| 4 | 0.330 s | 4.02 | 1.01 |
| 6 | 0.222 s | 5.98 | 1.00 |
| 8 | 0.200 s | 6.63 | 0.83 |

Falta correr lo mismo en las otras dos notebooks y en el servidor.
