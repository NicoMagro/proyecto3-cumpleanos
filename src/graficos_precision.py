# Genera graficos de evolucion de la precision y convergencia de Monte Carlo.
# Uso: python3 src/graficos_precision.py [ruta/al/csv]

import csv
import sys
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ARCHIVO = sys.argv[1] if len(sys.argv) > 1 else "resultados/precision/precision.csv"

datos_por_grupos = {}
teorica = None

with open(ARCHIVO) as f:
    lector = csv.DictReader(f)
    for fila in lector:
        g = int(fila["grupos"])
        p_sim = float(fila["p_simulada"])
        p_teo = float(fila["p_teorica"])
        err_abs = float(fila["error_abs"])
        tiempo = float(fila["tiempo"])
        
        teorica = p_teo
        datos_por_grupos.setdefault(g, {
            "p_sim": [],
            "error_abs": [],
            "tiempo": []
        })
        datos_por_grupos[g]["p_sim"].append(p_sim)
        datos_por_grupos[g]["error_abs"].append(err_abs)
        datos_por_grupos[g]["tiempo"].append(tiempo)

grupos_ordenados = sorted(datos_por_grupos.keys())
if not grupos_ordenados:
    raise SystemExit(f"No se encontraron datos en {ARCHIVO}")

p_simuladas = [np.mean(datos_por_grupos[g]["p_sim"]) for g in grupos_ordenados]
err_absolutos = [np.mean(datos_por_grupos[g]["error_abs"]) for g in grupos_ordenados]

print(f"=== Datos procesados de {ARCHIVO} (P teorica = {teorica:.6f}) ===")
print("Grupos       | P simulada     | Error absoluto | Tiempo (s)")
for g, p, e, t in zip(grupos_ordenados, p_simuladas, err_absolutos, [np.mean(datos_por_grupos[g]["tiempo"]) for g in grupos_ordenados]):
    print(f"{g:12d} | {p:14.6f} | {e:14.6f} | {t:8.4f}")

# Seleccionar etiquetas claras en el eje X para no saturar si hay muchos puntos
def formatear_n(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:g}M"
    if n >= 1_000:
        return f"{n/1_000:g}k"
    return str(n)

# Si hay muchos puntos (ej. > 20), rotulamos los hitos principales (ej. 1, 2, 5 por decada)
if len(grupos_ordenados) > 20:
    hitos_principales = {100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000,
                         100000, 200000, 500000, 1000000, 2000000, 5000000, 10000000}
    ticks_x = [g for g in grupos_ordenados if g in hitos_principales]
    # Asegurar incluir primer y ultimo punto
    if grupos_ordenados[0] not in ticks_x:
        ticks_x.insert(0, grupos_ordenados[0])
    if grupos_ordenados[-1] not in ticks_x:
        ticks_x.append(grupos_ordenados[-1])
    ticks_x = sorted(list(set(ticks_x)))
else:
    ticks_x = grupos_ordenados

etiquetas_x = [formatear_n(g) for g in ticks_x]

# -------------------------------------------------------------------------
# Grafico 1: Convergencia de la probabilidad simulada hacia el valor teorico
# -------------------------------------------------------------------------
plt.figure(figsize=(10, 5))
plt.axhline(teorica, color="#d62728", linestyle="--", linewidth=1.5, label=f"P teorica ({teorica:.4f})")

plt.plot(grupos_ordenados, p_simuladas, "o-", color="#1f77b4", markersize=4, linewidth=1.5, label="P simulada")
plt.xscale("log")
plt.xticks(ticks_x, etiquetas_x, rotation=45, fontsize=8)
plt.minorticks_off()
plt.xlabel("Cantidad de grupos simulados")
plt.ylabel("Probabilidad estimada")
plt.title("Evolucion de la probabilidad estimada segun grupos simulados")
plt.grid(alpha=0.3)
plt.legend()
salida_prob = "resultados/precision/evolucion_probabilidad.png"
plt.savefig(salida_prob, dpi=150, bbox_inches="tight")
plt.close()
print(f"\nGuardado {salida_prob}")

# -------------------------------------------------------------------------
# Grafico 2: Error absoluto vs cantidad de grupos y cota teorica 1 / sqrt(N)
# -------------------------------------------------------------------------
plt.figure(figsize=(10, 5))

plt.plot(grupos_ordenados, err_absolutos, "o-", color="#2ca02c", markersize=4, linewidth=1.5, label="Error absoluto |P_sim - P_teo|")

# Cota teorica de Monte Carlo ~ C / sqrt(N) ajustada con los primeros puntos
c_ajuste = err_absolutos[0] * math.sqrt(grupos_ordenados[0])
curva_teorica = [c_ajuste / math.sqrt(g) for g in grupos_ordenados]
plt.plot(grupos_ordenados, curva_teorica, "--", color="#d62728", linewidth=1.5, label=r"Tendencia Monte Carlo $\propto 1/\sqrt{N}$")

plt.xscale("log")
plt.yscale("log")
plt.xticks(ticks_x, etiquetas_x, rotation=45, fontsize=8)
plt.minorticks_off()
plt.xlabel("Cantidad de grupos simulados")
plt.ylabel("Error absoluto (escala log)")
plt.title("Convergencia del error absoluto segun cantidad de grupos")
plt.grid(alpha=0.3)
plt.legend()
salida_error = "resultados/precision/evolucion_error.png"
plt.savefig(salida_error, dpi=150, bbox_inches="tight")
plt.close()
print(f"Guardado {salida_error}")
