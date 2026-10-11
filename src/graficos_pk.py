# Genera el grafico de la curva P(K) (teorica vs simulada por Monte Carlo).
# Uso: python3 src/graficos_pk.py [ruta/al/csv]

import csv
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ARCHIVO = sys.argv[1] if len(sys.argv) > 1 else "resultados/curva_pk/curva_pk.csv"

ks = []
p_simuladas = []
p_teoricas = []

with open(ARCHIVO) as f:
    lector = csv.DictReader(f)
    for fila in lector:
        ks.append(int(fila["k"]))
        p_simuladas.append(float(fila["p_simulada"]))
        p_teoricas.append(float(fila["p_teorica"]))

if not ks:
    raise SystemExit(f"No se encontraron datos en {ARCHIVO}")

# Ordenar por K
ordenados = sorted(zip(ks, p_simuladas, p_teoricas))
ks = [x[0] for x in ordenados]
p_simuladas = [x[1] for x in ordenados]
p_teoricas = [x[2] for x in ordenados]

plt.figure(figsize=(9, 5))

# Curva teorica suave de fondo
plt.plot(ks, p_teoricas, color="#d62728", linestyle="--", linewidth=1.8, label="Probabilidad teorica")

# Puntos simulados por Monte Carlo
plt.plot(ks, p_simuladas, "o", color="#1f77b4", markersize=5, label="Simulacion Monte Carlo")

# Lineas de referencia en K=23 (50%)
if 23 in ks:
    idx23 = ks.index(23)
    p23 = p_teoricas[idx23]
    plt.axvline(23, color="gray", linestyle=":", alpha=0.7)
    plt.axhline(0.5, color="gray", linestyle=":", alpha=0.7)
    plt.scatter([23], [p23], color="#ff7f0e", s=60, zorder=5)
    plt.annotate(f"K=23: {p23*100:.1f}%", xy=(23, p23), xytext=(27, 0.42),
                 arrowprops=dict(arrowstyle="->", color="#ff7f0e", lw=1.2),
                 fontsize=9, color="#ff7f0e", fontweight="bold")

plt.xlabel("Personas en el grupo (K)")
plt.ylabel("Probabilidad de coincidencia P(K)")
plt.title("Paradoja del Cumpleaños: Probabilidad P(K) segun tamaño del grupo")
plt.ylim(-0.02, 1.03)
plt.xlim(min(ks) - 1, max(ks) + 1)
plt.grid(alpha=0.3)
plt.legend(loc="lower right")

salida = "resultados/curva_pk/curva_pk.png"
plt.savefig(salida, dpi=150, bbox_inches="tight")
plt.close()
print(f"Grafico guardado en {salida}")
