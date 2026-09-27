# Informe - Paradoja del Cumpleanios

(Documento en construccion, se completa a medida que avanzamos)

## 1. El problema

Explicar que es la paradoja y por que resulta contraintuitiva.

## 2. La formula teorica

Deducir P(K) por el complemento: primero se calcula la probabilidad de que
NINGUNA de las K personas comparta cumpleanios, y despues se resta de 1.

Supuestos del modelo (y por que no son del todo ciertos en la realidad):

- Los 365 dias son igual de probables.
- No se tienen en cuenta los anios bisiestos.
- Los cumpleanios de las personas son independientes (no hay mellizos).

## 3. Como lo simulamos

Explicar el metodo de Monte Carlo: sortear muchos grupos al azar y contar
la frecuencia con la que aparece una coincidencia.

## 4. Como lo paralelizamos

- Por que este problema se puede paralelizar facil: cada grupo es independiente.
- Como se repartieron los grupos entre los procesos.
- Por que se usa MPI_Reduce para juntar los resultados.
- Por que cada proceso necesita una semilla distinta.

## 5. Resultados

### 5.1 Convergencia

Tabla y grafico del error segun la cantidad de grupos simulados.

### 5.2 Curva P(K)

Comparacion de la curva simulada con la teorica.

### 5.3 Speedup

Tabla de tiempos, speedup y eficiencia. Grafico.

### 5.4 Comparacion entre computadoras

Resultados en las tres notebooks y en el servidor.

## 6. Conclusiones

Responder concretamente:

1. ¿La simulacion coincide con la teoria? ¿Con cuantos grupos?
2. ¿Como baja el error al aumentar la cantidad de simulaciones?
3. ¿Cuanto speedup logramos y hasta cuantos procesos sigue mejorando?
4. ¿Por que a partir de cierta cantidad de procesos deja de mejorar?
5. ¿Que diferencias hubo entre las computadoras?

## 7. Mejoras para el futuro

Ideas: hacer un histograma de en que grupo aparece la primera coincidencia,
probar con anios de otra cantidad de dias, usar la distribucion real de
nacimientos en lugar de suponer que todos los dias son igual de probables.

## 8. Bibliografia

Ver [bibliografia.md](bibliografia.md).
