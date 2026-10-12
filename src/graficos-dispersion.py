# Diagramas de caja de los tiempos: muestran la dispersion de las 10
# repeticiones de cada configuracion, que una tabla de medianas esconde.
# Genera un dispersion.png dentro de la carpeta de cada maquina.
#
# Uso:  python3 src/graficos-dispersion.py

import csv
import os
import glob
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

for archivo in sorted(glob.glob("resultados/*/speedup.csv")):
    carpeta = os.path.dirname(archivo)
    nombre = os.path.basename(carpeta)

    with open(archivo) as f:
        filas = list(csv.DictReader(f))

    # Tiempos del estatico agrupados por cantidad de procesos
    por_p = {}
    for fila in filas:
        if fila["tipo"] == "estatico":
            por_p.setdefault(int(fila["procesos"]), []).append(float(fila["tiempo"]))

    if not por_p:
        continue

    procesos = sorted(por_p)
    datos = [por_p[p] for p in procesos]
    corridas = len(datos[0])

    plt.figure(figsize=(max(7, len(procesos) * 0.5), 5))
    plt.boxplot(datos, labels=[str(p) for p in procesos])
    plt.xlabel("Cantidad de procesos")
    plt.ylabel("Tiempo (s)")
    plt.title("Dispersion de los tiempos - %s (%d corridas por configuracion)"
              % (nombre, corridas))
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(carpeta + "/dispersion.png", dpi=150)
    plt.close()

    # Resumen por consola: cuanto varia cada configuracion
    print("\n%s" % nombre)
    print("  procesos | mediana | minimo | maximo | variacion")
    for p in procesos:
        v = sorted(por_p[p])
        m = v[len(v) // 2]
        print("  %8d | %7.3f | %6.3f | %6.3f | %+.0f%%"
              % (p, m, v[0], v[-1], 100 * (v[-1] - v[0]) / m))
    print("  Guardado %s/dispersion.png" % carpeta)
