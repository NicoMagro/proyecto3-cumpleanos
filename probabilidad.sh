#!/bin/bash
# Experimentos de probabilidad (no de rendimiento):
#   1. Convergencia: como baja el error al aumentar la cantidad de grupos.
#   2. Curva P(K): la probabilidad para distintos tamanios de grupo.
# Uso: ./probabilidad.sh

mkdir -p resultados/probabilidad

# --- 1. Convergencia -------------------------------------------------------
# Para cada cantidad de grupos repetimos con 10 semillas distintas, de modo
# que cada repeticion sea una muestra independiente del error.
SALIDA=resultados/probabilidad/convergencia.csv
echo "k,grupos,semilla,p_simulada,p_teorica,error" > $SALIDA

for t in 1000 10000 100000 1000000 10000000
do
    for s in 1 2 3 4 5 6 7 8 9 10
    do
        ./serial 23 $t $((1000 * s)) | grep "^csv" | \
          awk -F, -v s=$((1000 * s)) '{printf "%s,%s,%d,%s,%s,%.8f\n", $2, $3, s, $6, $7, $6-$7}' >> $SALIDA
    done
    echo "convergencia: $t grupos listo"
done

# --- 2. Curva P(K) ---------------------------------------------------------
SALIDA=resultados/probabilidad/curva_pk.csv
echo "k,grupos,p_simulada,p_teorica,error" > $SALIDA

for k in $(seq 2 100)
do
    ./serial $k 1000000 | grep "^csv" | \
      awk -F, '{printf "%s,%s,%s,%s,%.8f\n", $2, $3, $6, $7, $6-$7}' >> $SALIDA
done
echo "curva P(K): listo"

echo "Resultados en resultados/probabilidad/"
