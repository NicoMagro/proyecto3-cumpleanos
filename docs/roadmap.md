# Que falta hacer

## Listo

- [x] Simulacion serial (`src/cumpleanos.c`, `src/serial.c`)
- [x] Version paralela estatica con MPI (`src/paralelo-estatico.c`)
- [x] Version paralela dinamica con maestro-trabajadores (`src/paralelo-dinamico.c`)
- [x] Tests
- [x] Script de mediciones automaticas (`speedup.sh`, `precision.sh` y `curva_pk.sh`)
- [x] Mediciones de speedup en notebook de Nicolas, desktop de Sergio y cluster
- [x] Generacion de graficos (`src/graficos.py`, `src/graficos_precision.py` y `src/graficos_pk.py`)
- [x] Experimento 1: convergencia y precisión (ver `docs/como-correr.md`)
- [x] Experimento 2: curva P(K) (ver `docs/como-correr.md`)

## Falta

- [ ] Repartir quien hace que
- [ ] Buscar bibliografia y escribir la seccion 8 del informe
- [ ] Escribir el informe final
- [ ] Preparar la defensa oral

## Preguntas que nos pueden hacer en el oral

Conviene que los tres sepamos contestar estas:

1. ¿Por que el resultado es tan contraintuitivo?
2. ¿Por que cada proceso usa una semilla distinta? ¿Que pasaria si todos usaran la misma?
3. ¿Por que se usa la mediana y no el promedio de las corridas?
4. ¿Por que el speedup deja de mejorar a partir de cierta cantidad de procesos?
5. ¿Que hace MPI_Reduce y por que conviene en lugar de muchos Send y Recv?
6. ¿Que pasa si la cantidad de grupos no es divisible por la cantidad de procesos?
7. ¿Por que el paralelo estatico es superior al dinamico en este problema?
8. ¿Por que el dinamico rinde tan poco (~50%) con 2 procesos y por que mejora con mas procesos?
9. ¿Como influye el tamanio de bloque en el dinamico y por que no afecta a la precision?
10. ¿Que impacto tiene activar SMT/Hyper-Threading y por que mejora el tiempo?
11. ¿Por que en el paralelo dinamico sobreasignar procesos (ej. 192 en 96 nucleos) puede rendir mejor que en 96 o que en el estatico?
