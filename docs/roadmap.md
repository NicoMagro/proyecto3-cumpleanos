# Que falta hacer

## Listo

- [x] Simulacion serial (`src/cumpleanos.c`, `src/serial.c`)
- [x] Version paralela con MPI (`src/paralelo.c`)
- [x] Tests
- [x] Primera medicion de speedup en la notebook de Nicolas

## Falta

- [ ] Repartir quien hace que
- [ ] Buscar bibliografia y escribir la seccion 8 del informe
- [ ] Experimento 1: convergencia (ver docs/como-correr.md)
- [ ] Experimento 2: curva P(K)
- [ ] Experimento 3: speedup en las otras dos notebooks
- [ ] Correr todo en el servidor de la facultad
- [ ] Hacer los graficos
- [ ] Escribir el informe
- [ ] Preparar la defensa oral

## Preguntas que nos pueden hacer en el oral

Conviene que los tres sepamos contestar estas:

1. ¿Por que el resultado es tan contraintuitivo?
2. ¿Por que cada proceso usa una semilla distinta? ¿Que pasaria si todos
   usaran la misma?
3. ¿Por que se usa la mediana y no el promedio de las corridas?
4. ¿Por que el speedup deja de mejorar a partir de cierta cantidad de procesos?
5. ¿Que hace MPI_Reduce y por que conviene en lugar de muchos Send y Recv?
6. ¿Que pasa si la cantidad de grupos no es divisible por la cantidad de procesos?
