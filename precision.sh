#!/bin/bash
# Mide la evolucion de la precision y el error de la simulacion
# variando la cantidad de grupos simulados (metodo de Monte Carlo).
# Corre una unica simulacion determinista por cada cantidad de grupos,
# con una grilla densa para obtener una curva perfectamente suave.
# Uso: ./precision.sh [k] [procesos]

K=${1:-23}
PROCESOS=${2:-8}

# Lista densa de cantidades de grupos a simular (64 puntos distribuidos en escala logaritmica)
GRUPOS="
100 150 200 300 400 500 600 700 850 1000
1500 2000 3000 4000 5000 6000 7000 8500 10000
15000 20000 30000 40000 50000 60000 70000 85000 100000
150000 200000 300000 400000 500000 600000 700000 850000 1000000
1500000 2000000 3000000 4000000 5000000 6000000 8000000 10000000
15000000 20000000 30000000 40000000 50000000 60000000 80000000 100000000
150000000 200000000 300000000 400000000 500000000 600000000 800000000
1000000000 1500000000 2000000000 3000000000
"
SALIDA=resultados/precision/precision.csv

mkdir -p resultados/precision
mpicc src/cumpleanos.c src/paralelo-estatico.c -o paralelo-estatico || exit 1
echo "k,grupos,procesos,p_simulada,p_teorica,error,error_abs,tiempo" > $SALIDA

echo "=== Iniciando mediciones de precision (K=$K, Procesos=$PROCESOS) ==="

total_puntos=$(echo $GRUPOS | wc -w)
i=0

for g in $GRUPOS
do
    i=$((i + 1))
    # Ejecutar paralelo-estatico y capturar la linea formateada csv
    linea=$(mpirun --oversubscribe -n $PROCESOS ./paralelo-estatico $K $g | grep "^csv")
    if [ -n "$linea" ]; then
        # El formato de salida de paralelo-estatico es: csv,k,grupos,procesos,bloque,p_simulada,p_teorica,tiempo
        p_sim=$(echo "$linea" | cut -d',' -f6)
        p_teo=$(echo "$linea" | cut -d',' -f7)
        tiempo=$(echo "$linea" | cut -d',' -f8)
        
        # Calcular error y error absoluto con awk
        errores=$(awk -v s="$p_sim" -v t="$p_teo" 'BEGIN { err = s - t; abs_err = (err < 0 ? -err : err); printf "%.8f,%.8f", err, abs_err }')
        
        echo "$K,$g,$PROCESOS,$p_sim,$p_teo,$errores,$tiempo" >> $SALIDA
        printf "[%2d/%2d] Grupos: %8d | P_sim: %s | Err: %s\n" $i $total_puntos $g $p_sim $(echo $errores | cut -d',' -f1)
    fi
done

echo "=== Mediciones completadas en $SALIDA ==="
echo "Generando graficos..."
python3 src/graficos_precision.py "$SALIDA"
