# Graficos sobre como influye el tamanio del problema en el speedup.
# Lee los CSV de resultados/tamanio/ y genera tres PNG en esa misma carpeta.
#
# Uso:  python3 src/graficos-tamanio.py

import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CARPETA = "resultados/tamanio/"


def mediana(lista):
    o = sorted(lista)
    m = len(o) // 2
    return o[m] if len(o) % 2 == 1 else (o[m - 1] + o[m]) / 2


def leer(archivo):
    with open(CARPETA + archivo) as f:
        return list(csv.DictReader(f))


def agrupar(filas, clave_a, clave_b, valor):
    d = {}
    for f in filas:
        d.setdefault((int(f[clave_a]), int(f[clave_b])), []).append(float(f[valor]))
    return {k: mediana(v) for k, v in d.items()}


# ---------- 1. Speedup segun la cantidad de procesos, una curva por T ----------
d = agrupar(leer("tamanio-problema.csv"), "grupos", "procesos", "tiempo")
ts = sorted({t for t, _ in d})
ps = sorted({p for _, p in d if p > 1})

plt.figure(figsize=(7, 5))
plt.plot([1] + ps, [1] + ps, "--", color="gray", label="ideal")
for t in ts:
    speedup = [d[(t, p)] and d[(t, 1)] / d[(t, p)] for p in ps]
    plt.plot(ps, speedup, "o-", label="T = {:,}".format(t).replace(",", "."))
plt.xlabel("Cantidad de procesos")
plt.ylabel("Speedup")
plt.title("Speedup segun el tamanio del problema (K=23)")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(CARPETA + "speedup-por-tamanio.png", dpi=150)
print("Guardado " + CARPETA + "speedup-por-tamanio.png")

# ---------- 2. Ganancia real, midiendo el comando completo ----------
d = agrupar(leer("tiempo-total.csv"), "grupos", "procesos", "tiempo_total")
ts = sorted({t for t, _ in d})
ganancia = [d[(t, 1)] / d[(t, 8)] for t in ts]

plt.figure(figsize=(7, 5))
plt.semilogx(ts, ganancia, "o-", color="tab:red",
             label="ganancia real con 8 procesos")
plt.axhline(1.0, color="gray", linestyle="--", label="sin ganancia")
for t, g in zip(ts, ganancia):
    plt.annotate("%.2fx" % g, xy=(t, g), xytext=(0, 8),
                 textcoords="offset points", ha="center", fontsize=9)
plt.xlabel("Cantidad de grupos simulados (T)")
plt.ylabel("Tiempo serial / tiempo con 8 procesos")
plt.title("Ganancia midiendo el comando completo\n(incluye el arranque de MPI)")
plt.grid(alpha=0.3, which="both")
plt.legend()
plt.tight_layout()
plt.savefig(CARPETA + "ganancia-real.png", dpi=150)
print("Guardado " + CARPETA + "ganancia-real.png")

# ---------- 3. Efecto del tamanio del grupo K ----------
d = agrupar(leer("efecto-k.csv"), "k", "procesos", "tiempo")
ks = sorted({k for k, _ in d})
speedup = [d[(k, 1)] / d[(k, 8)] for k in ks]

fig, (izq, der) = plt.subplots(1, 2, figsize=(11, 4.5))
izq.plot(ks, [d[(k, 1)] for k in ks], "o-", label="serial")
izq.plot(ks, [d[(k, 8)] for k in ks], "o-", label="8 procesos")
izq.set_xlabel("Personas por grupo (K)")
izq.set_ylabel("Tiempo (s)")
izq.set_title("Tiempo segun K")
izq.grid(alpha=0.3)
izq.legend()

der.plot(ks, speedup, "o-", color="tab:green")
der.set_ylim(0, 9)
der.set_xlabel("Personas por grupo (K)")
der.set_ylabel("Speedup con 8 procesos")
der.set_title("El speedup no depende de K")
der.grid(alpha=0.3)

fig.tight_layout()
fig.savefig(CARPETA + "efecto-k.png", dpi=150)
print("Guardado " + CARPETA + "efecto-k.png")

print("\nGanancia real con 8 procesos:")
for t, g in zip(ts, ganancia):
    print("  T = %-12s %.2fx" % ("{:,}".format(t).replace(",", "."), g))
print("\nSpeedup segun K:")
for k, s in zip(ks, speedup):
    print("  K = %-5d %.2f" % (k, s))
