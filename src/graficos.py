# Genera los graficos a partir de resultados/speedup.csv
#
# Uso:  python3 src/graficos.py

import csv
import matplotlib
matplotlib.use("Agg")          # para que funcione tambien por SSH
import matplotlib.pyplot as plt

ARCHIVO = "resultados/speedup.csv"


def mediana(lista):
    """Devuelve el valor del medio de una lista ordenada.

    Es lo que pide la consigna. Sirve para que una corrida lenta suelta
    (porque justo el sistema operativo estaba haciendo otra cosa) no
    arruine el resultado.
    """
    ordenada = sorted(lista)
    mitad = len(ordenada) // 2
    if len(ordenada) % 2 == 1:
        return ordenada[mitad]
    return (ordenada[mitad - 1] + ordenada[mitad]) / 2


def promedio_recortado(lista):
    """Promedio sacando el valor mas chico y el mas grande.

    Es otra forma de sacar los valores raros. La calculamos ademas de la
    mediana para poder comparar: si las dos dan parecido, quiere decir que
    las mediciones fueron estables.
    """
    ordenada = sorted(lista)
    if len(ordenada) > 2:
        ordenada = ordenada[1:-1]
    return sum(ordenada) / len(ordenada)


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
recortados = [promedio_recortado(tiempos[p]) for p in procesos]

# El speedup se mide contra la version serial (1 proceso): Sp = T1 / Tp
tiempo_serial = medianas[0]
speedup = [tiempo_serial / t for t in medianas]
eficiencia = [s / p for s, p in zip(speedup, procesos)]

# Lo mismo pero con el promedio recortado, para comparar los dos metodos
serial_recortado = recortados[0]
speedup_recortado = [serial_recortado / t for t in recortados]

print("Corridas por configuracion:", len(tiempos[procesos[0]]))
print("")
print("procesos | mediana (s) | speedup | eficiencia | prom. recortado | speedup")
for i, p in enumerate(procesos):
    print("%8d | %11.3f | %7.2f | %10.2f | %15.3f | %7.2f"
          % (p, medianas[i], speedup[i], eficiencia[i],
             recortados[i], speedup_recortado[i]))

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
