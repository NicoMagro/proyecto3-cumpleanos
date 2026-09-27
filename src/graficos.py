# Genera los graficos a partir de resultados/speedup.csv
#
# Uso:  python3 src/graficos.py

import csv
import matplotlib
matplotlib.use("Agg")          # para que funcione tambien por SSH
import matplotlib.pyplot as plt

ARCHIVO = "resultados/speedup.csv"


def mediana(lista):
    """Devuelve el valor del medio de una lista ordenada."""
    ordenada = sorted(lista)
    mitad = len(ordenada) // 2
    if len(ordenada) % 2 == 1:
        return ordenada[mitad]
    return (ordenada[mitad - 1] + ordenada[mitad]) / 2


# Juntamos los tiempos de cada cantidad de procesos
tiempos = {}
with open(ARCHIVO) as f:
    for fila in csv.reader(f):
        if len(fila) < 7 or fila[0] != "csv":
            continue           # saltamos el encabezado
        procesos = int(fila[3])
        tiempo = float(fila[6])
        tiempos.setdefault(procesos, []).append(tiempo)

procesos = sorted(tiempos.keys())
medianas = [mediana(tiempos[p]) for p in procesos]

# El speedup se mide contra la version serial (1 proceso)
tiempo_serial = medianas[0]
speedup = [tiempo_serial / t for t in medianas]
eficiencia = [s / p for s, p in zip(speedup, procesos)]

print("procesos | tiempo (s) | speedup | eficiencia")
for p, t, s, e in zip(procesos, medianas, speedup, eficiencia):
    print("%8d | %10.3f | %7.2f | %10.2f" % (p, t, s, e))

# Grafico de speedup
plt.figure()
plt.plot(procesos, speedup, "o-", label="speedup medido")
plt.plot(procesos, procesos, "--", color="gray", label="speedup ideal")
plt.xlabel("Cantidad de procesos")
plt.ylabel("Speedup")
plt.title("Speedup de la simulacion")
plt.grid(alpha=0.3)
plt.legend()
plt.savefig("resultados/speedup.png", dpi=150)
print("\nGuardado resultados/speedup.png")

# Grafico de eficiencia
plt.figure()
plt.plot(procesos, eficiencia, "o-")
plt.axhline(1.0, color="gray", linestyle="--")
plt.ylim(0, 1.2)
plt.xlabel("Cantidad de procesos")
plt.ylabel("Eficiencia")
plt.title("Eficiencia paralela")
plt.grid(alpha=0.3)
plt.savefig("resultados/eficiencia.png", dpi=150)
print("Guardado resultados/eficiencia.png")
