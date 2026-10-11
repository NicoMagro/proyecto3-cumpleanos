#!/bin/bash
# Mide la curva P(K) variando el tamaño del grupo de personas (K)
# y compara la probabilidad simulada contra la teorica.
# Al finalizar, ejecuta automaticamente src/graficos_pk.py para generar el grafico.
# Uso: ./curva_pk.sh [grupos] [procesos]

GRUPOS=${1:-1000000}
PROCESOS=${2:-8}

# Rango de personas K desde 2 hasta 80 (cubre de 0% a 99.9%)
# Con paso de 2 en 2, asegurando incluir el hito clasico K=23
KS="2 4 6 8 10 12 14 16 18 20 22 23 24 26 28 30 32 34 36 38 40 42 44 46 48 50 52 54 56 58 60 62 64 66 68 70 72 74 76 78 80"
SALIDA=resultados/curva_pk/curva_pk.csv

mkdir -p resultados/curva_pk
mpicc src/cumpleanos.c src/paralelo-estatico.c -o paralelo-estatico || exit 1

echo "k,grupos,procesos,p_simulada,p_teorica,tiempo" > $SALIDA

echo "=== Iniciando mediciones de Curva P(K) (Grupos=$GRUPOS, Procesos=$PROCESOS) ==="

total_k=$(echo $KS | wc -w)
i=0

for k in $KS
do
    i=$((i + 1))
    linea=$(mpirun --oversubscribe -n $PROCESOS ./paralelo-estatico $k $GRUPOS | grep "^csv")
    if [ -n "$linea" ]; then
        # Salida: csv,k,grupos,procesos,bloque,p_simulada,p_teorica,tiempo
        p_sim=$(echo "$linea" | cut -d',' -f6)
        p_teo=$(echo "$linea" | cut -d',' -f7)
        tiempo=$(echo "$linea" | cut -d',' -f8)
        
        echo "$k,$GRUPOS,$PROCESOS,$p_sim,$p_teo,$tiempo" >> $SALIDA
        printf "[%2d/%2d] K=%2d | P_sim: %s | P_teo: %s | Tiempo: %ss\n" $i $total_k $k $p_sim $p_teo $tiempo
    fi
done

echo "=== Mediciones completadas en $SALIDA ==="
echo "Generando graficos..."
python3 src/graficos_pk.py "$SALIDA"
