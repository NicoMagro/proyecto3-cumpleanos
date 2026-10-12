# Graficos de la parte de probabilidad (no de rendimiento):
#   - convergencia.png : como baja el error al aumentar la cantidad de grupos
#   - curva_pk.png     : probabilidad simulada contra la teorica
#
# Uso:  python3 src/graficos-probabilidad.py

import csv
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CARPETA = "resultados/probabilidad/"


def leer(archivo):
    with open(CARPETA + archivo) as f:
        return list(csv.DictReader(f))


def mediana(lista):
    o = sorted(lista)
    m = len(o) // 2
    return o[m] if len(o) % 2 == 1 else (o[m - 1] + o[m]) / 2


# ---------------- Convergencia ----------------
filas = leer("convergencia.csv")

por_t = {}
for f in filas:
    por_t.setdefault(int(f["grupos"]), []).append(abs(float(f["error"])))

ts = sorted(por_t)
errores = [mediana(por_t[t]) for t in ts]

print("grupos      | error mediano | error * raiz(T)")
for t, e in zip(ts, errores):
    print("%11d | %13.6f | %.3f" % (t, e, e * math.sqrt(t)))

plt.figure(figsize=(7, 5))
plt.loglog(ts, errores, "o-", label="error observado (mediana de 10 semillas)")

# Recta de referencia proporcional a 1/raiz(T), apoyada en el primer punto
referencia = [errores[0] * math.sqrt(ts[0] / t) for t in ts]
plt.loglog(ts, referencia, "--", color="gray", label="referencia  1/raiz(T)")

# Nube de puntos: todas las semillas, para que se vea la dispersion
for t in ts:
    plt.loglog([t] * len(por_t[t]), por_t[t], ".", color="tab:blue", alpha=0.3)

plt.xlabel("Cantidad de grupos simulados (T)")
plt.ylabel("Error absoluto |P simulada - P teorica|")
plt.title("Convergencia del metodo de Monte Carlo (K=23)")
plt.grid(True, which="both", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(CARPETA + "convergencia.png", dpi=150)
print("\nGuardado " + CARPETA + "convergencia.png")

# ---------------- Curva P(K) ----------------
filas = sorted(leer("curva_pk.csv"), key=lambda f: int(f["k"]))
ks = [int(f["k"]) for f in filas]
sim = [float(f["p_simulada"]) for f in filas]
teo = [float(f["p_teorica"]) for f in filas]

plt.figure(figsize=(7, 5))
plt.plot(ks, teo, "-", linewidth=2, label="teorica")
plt.plot(ks, sim, ".", markersize=6, label="simulada (1.000.000 de grupos)")
plt.axhline(0.5, color="gray", linestyle=":", linewidth=1)
plt.axvline(23, color="gray", linestyle=":", linewidth=1)
plt.annotate("K=23: la probabilidad pasa el 50%",
             xy=(23, 0.507), xytext=(33, 0.33),
             arrowprops=dict(arrowstyle="->", color="gray"))
plt.xlabel("Personas en el grupo (K)")
plt.ylabel("P(al menos dos comparten cumpleanios)")
plt.title("Paradoja del cumpleanios: simulacion contra teoria")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(CARPETA + "curva_pk.png", dpi=150)
print("Guardado " + CARPETA + "curva_pk.png")

mayor = max(abs(float(f["error"])) for f in filas)
print("\nMayor diferencia entre simulacion y teoria en toda la curva: %.5f" % mayor)
