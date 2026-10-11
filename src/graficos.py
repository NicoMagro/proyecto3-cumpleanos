# Genera graficos a partir de un archivo unificado CSV.
# Uso: python3 src/graficos.py

import csv
import os
import math
import matplotlib
import numpy as np
from matplotlib.colors import LogNorm
from matplotlib.patches import Rectangle
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

ARCHIVO = "resultados/speedup.csv"

def mediana(lista):
    ordenada = sorted(lista)
    mitad = len(ordenada) // 2
    if len(ordenada) % 2 == 1:
        return ordenada[mitad]
    return (ordenada[mitad - 1] + ordenada[mitad]) / 2

tiempos_serial = []
tiempos_estatico = {}
tiempos_dinamico = {}
simuladas_dinamico = {}
grupos = None
teorica = None

# 1. Leer el archivo CSV
with open(ARCHIVO) as f:
    for fila in csv.reader(f):
        if len(fila) < 8 or fila[0] not in ["serial", "estatico", "dinamico"]:
            continue
            
        tipo = fila[0]
        grupos = int(fila[2])
        procesos = int(fila[3])
        bloque = int(fila[4])
        p_sim = float(fila[5])
        teorica = float(fila[6])
        tiempo = float(fila[7])
        
        if tipo == "serial":
            tiempos_serial.append(tiempo)
        elif tipo == "estatico":
            tiempos_estatico.setdefault(procesos, []).append(tiempo)
        elif tipo == "dinamico":
            tiempos_dinamico.setdefault(procesos, {}).setdefault(bloque, []).append(tiempo)
            simuladas_dinamico.setdefault(procesos, {}).setdefault(bloque, []).append(p_sim)

if not tiempos_serial:
    raise SystemExit(f"No hay corridas seriales en {ARCHIVO}")

# 2. Calcular tiempo base (serial)
serial_mediana = mediana(tiempos_serial)
print(f"Tiempo serial (mediana de {len(tiempos_serial)} corridas): {serial_mediana:.3f} s\n")

# 3. Procesar Estatico (mediana por procesador)
procs_estatico = sorted(tiempos_estatico.keys())
sp_estatico = []
ef_estatico = []

print("--- ESTATICO ---")
print("procesos | tiempo (s) | speedup | eficiencia")
for p in procs_estatico:
    t_med = mediana(tiempos_estatico[p])
    speedup = serial_mediana / t_med
    eficiencia = speedup / p
    sp_estatico.append(speedup)
    ef_estatico.append(eficiencia)
    print(f"{p:8d} | {t_med:10.3f} | {speedup:7.2f} | {eficiencia:10.2f}")

# 4. Procesar Dinamico (buscar el MEJOR bloque por procesador)
procs_dinamico = sorted(tiempos_dinamico.keys())
sp_dinamico = []
ef_dinamico = []

print("\n--- DINAMICO (Mejor bloque por proceso) ---")
print("procesos | mejor tamanio bloque | tiempo (s) | speedup | eficiencia")
for p in procs_dinamico:
    mejor_tiempo = float('inf')
    mejor_bloque = -1
    
    for b, tiempos_lista in tiempos_dinamico[p].items():
        t_med = mediana(tiempos_lista)
        if t_med < mejor_tiempo:
            mejor_tiempo = t_med
            mejor_bloque = b
            
    speedup = serial_mediana / mejor_tiempo
    eficiencia = speedup / p
    sp_dinamico.append(speedup)
    ef_dinamico.append(eficiencia)
    print(f"{p:8d} | {mejor_bloque:12d} | {mejor_tiempo:10.3f} | {speedup:7.2f} | {eficiencia:10.2f}")

os.makedirs("resultados", exist_ok=True)

# Anexar el punto base (1 proceso, speedup 1.0, eficiencia 1.0) para los graficos
procs_estatico.insert(0, 1)
sp_estatico.insert(0, 1.0)
ef_estatico.insert(0, 1.0)

procs_dinamico.insert(0, 1)
sp_dinamico.insert(0, 1.0)
ef_dinamico.insert(0, 1.0)

# ---------------------------------------------------------------
# Grafico 1: Speedup Comparativo
# ---------------------------------------------------------------
plt.figure(figsize=(9, 6))
plt.plot(procs_estatico, sp_estatico, "o-", color="tab:blue", label="Estático")
plt.plot(procs_dinamico, sp_dinamico, "s-", color="tab:orange", label="Dinámico (mejor bloque)")
max_proc = max(procs_estatico + procs_dinamico) if procs_estatico else 0
if max_proc > 0:
    plt.plot([1, max_proc], [1, max_proc], "--", color="gray", label="Speedup ideal")
todos_procs_sp = sorted(list(set(procs_estatico + procs_dinamico)))
plt.xticks(todos_procs_sp)
plt.xlabel("Cantidad de procesos")
plt.ylabel("Speedup")
plt.title("Comparación de Speedup: Estático vs Mejor Dinámico")
plt.grid(alpha=0.3)
plt.legend()
plt.savefig("resultados/speedup.png", dpi=150, bbox_inches="tight")
plt.close()
print("\nGuardado resultados/speedup.png")

# ---------------------------------------------------------------
# Grafico 2: Eficiencia Comparativa
# ---------------------------------------------------------------
plt.figure(figsize=(9, 6))
plt.plot(procs_estatico, ef_estatico, "o-", color="tab:blue", label="Estático")
plt.plot(procs_dinamico, ef_dinamico, "s-", color="tab:orange", label="Dinámico (mejor bloque)")
plt.axhline(1.0, color="gray", linestyle="--", label="Eficiencia ideal")
plt.xticks(todos_procs_sp)
plt.ylim(0, 1.2)
plt.xlabel("Cantidad de procesos")
plt.ylabel("Eficiencia")
plt.title("Comparación de Eficiencia: Estático vs Mejor Dinámico")
plt.grid(alpha=0.3)
plt.legend()
plt.savefig("resultados/eficiencia.png", dpi=150, bbox_inches="tight")
plt.close()
print("Guardado resultados/eficiencia.png")

# ---------------------------------------------------------------
# Datos para graficos de Bloques (Tiempo y Precision)
# ---------------------------------------------------------------
# Removemos el "1" insertado artificialmente para no interferir con las tablas de bloques
procs_dinamico.pop(0)

datos_bloques = {}
for p in sorted(tiempos_dinamico):
    filas = []
    for b, lista in tiempos_dinamico[p].items():
        filas.append((math.ceil(grupos / b), b, mediana(lista)))
    filas.sort()
    datos_bloques[p] = filas

print("\n--- DETALLES POR BLOQUE (DINAMICO) ---")
print(f"Grupos simulados: {grupos}")
for p in sorted(datos_bloques):
    trabajadores = max(p - 1, 1)
    mejor = min(datos_bloques[p], key=lambda f: f[2])
    print(f"\nProcesos: {p} ({trabajadores} trabajadores)")
    print("bloques tot. | bloques/trab. | tam. bloque | tiempo (s)")
    for n, b, t in datos_bloques[p]:
        print(f"{n:12d} | {n/trabajadores:13.1f} | {b:11d} | {t:10.3f}")
    print(f"  -> mejor: {mejor[0]} bloques (tam. {mejor[1]}) con {mejor[2]:.3f} s")

# ---------------------------------------------------------------
# Grafico 3: Tiempo total vs bloques totales (escala log)
# ---------------------------------------------------------------
procs_ordenados = sorted(datos_bloques)
todos_bloques = sorted({f[0] for filas in datos_bloques.values() for f in filas})

matriz = np.full((len(procs_ordenados), len(todos_bloques)), np.nan)
for i, p in enumerate(procs_ordenados):
    for n, b, t in datos_bloques[p]:
        matriz[i, todos_bloques.index(n)] = t

norm = LogNorm(vmin=np.nanmin(matriz), vmax=np.nanmax(matriz))

fig, ax = plt.subplots(figsize=(11, 0.45 * len(procs_ordenados) + 2.5))
im = ax.imshow(matriz, aspect="auto", cmap="viridis_r", norm=norm)

ax.set_xticks(range(len(todos_bloques)))
ax.set_xticklabels([str(n) for n in todos_bloques])
ax.set_yticks(range(len(procs_ordenados)))
ax.set_yticklabels([str(p) for p in procs_ordenados])
ax.set_xlabel("Cantidad total de bloques")
ax.set_ylabel("Cantidad de procesos")
ax.set_title("Tiempo total (s) segun procesos y cantidad de bloques")

# Numero dentro de cada celda (texto oscuro sobre colores claros y viceversa)
for i in range(matriz.shape[0]):
    for j in range(matriz.shape[1]):
        v = matriz[i, j]
        if np.isnan(v):
            continue
        color = "black" if norm(v) < 0.55 else "white"
        ax.text(j, i, f"{v:.3g}", ha="center", va="center",
                fontsize=8, color=color)

# Recuadro rojo en el mejor tiempo de cada fila
for i in range(matriz.shape[0]):
    minimo = np.nanmin(matriz[i])
    for j in range(matriz.shape[1]):
        if not np.isnan(matriz[i, j]) and np.isclose(matriz[i, j], minimo,
                                                      rtol=0, atol=1e-9):
            ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False,
                                   edgecolor="red", linewidth=2))

fig.colorbar(im, ax=ax, label="Tiempo total (s, escala log)")
fig.savefig("resultados/bloques.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("\nGuardado resultados/bloques.png")

# ---------------------------------------------------------------
# Grafico 4: Precision de simulacion
# ---------------------------------------------------------------
error = {}
for p in sorted(simuladas_dinamico):
    filas = []
    for b, lista in simuladas_dinamico[p].items():
        promedio = sum(lista) / len(lista)
        filas.append((math.ceil(grupos / b), b, promedio - teorica))
    filas.sort()
    error[p] = filas

print(f"\nProbabilidad teorica: {teorica:.6f}")

plt.figure(figsize=(9, 5))
plt.axhline(0, color="black", linewidth=1, label="valor teorico")

marcadores = ["o", "s", "^", "D", "v", "x"]
for i, p in enumerate(sorted(error)):
    x = [f[0] for f in error[p]]
    y = [f[2] for f in error[p]]
    plt.plot(x, y, marcadores[i % len(marcadores)] + "-", alpha=0.7,
             label=f"{p} procesos")

plt.xscale("log")
todos_bloques_err = sorted({f[0] for filas in error.values() for f in filas})
plt.xticks(todos_bloques_err, [str(n) for n in todos_bloques_err], rotation=45)
plt.minorticks_off()
plt.xlabel("Cantidad total de bloques (escala log)")
plt.ylabel("Error = p simulada - p teorica")
plt.title("Precision de la simulacion segun bloques y procesos")
plt.grid(alpha=0.3)
plt.legend(fontsize=6, ncol=2)
plt.savefig("resultados/bloques_precision.png", dpi=150, bbox_inches="tight")
plt.close()
print("Guardado resultados/bloques_precision.png")