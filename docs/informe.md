# Paradoja del Cumpleaños: simulación paralela con MPI

**Proyecto 3 — Evaluación Parcial 1**
Métodos Numéricos II / Computación Científica — FACET, UNT — 2026

Integrantes: Ángel Nicolás Magro, Fran Leccese, Sergio Zair Lobo

---

## 1. El problema

La paradoja del cumpleaños plantea la siguiente pregunta: en un grupo de K
personas elegidas al azar, ¿qué probabilidad hay de que al menos dos de ellas
cumplan años el mismo día?

Se la llama paradoja porque el resultado contradice la intuición. Frente a 365
días posibles, uno esperaría necesitar un grupo muy numeroso para que aparezca
una coincidencia. Sin embargo, con solo 23 personas la probabilidad ya supera
el 50%, y con 57 personas pasa el 99%.

La intuición falla porque uno tiende a pensar en cuántas personas comparten
cumpleaños _con uno mismo_, que son 22 comparaciones. Pero la pregunta es si
existe alguna coincidencia entre _cualquier_ par del grupo, y en un grupo de 23
personas hay 23 × 22 / 2 = 253 pares posibles. Es esa cantidad de pares, y no
la cantidad de personas, la que hace crecer la probabilidad tan rápido.

## 2. La solución analítica

Calcular directamente la probabilidad de que haya al menos una coincidencia es
engorroso, porque habría que sumar muchos casos distintos: que coincidan
exactamente dos personas, que coincidan tres, que haya dos pares separados, y
así sucesivamente.

Resulta mucho más simple calcular el **complemento**: la probabilidad de que
_ninguna_ persona comparta cumpleaños, es decir, que las K personas cumplan
todas en días diferentes. Ese es un solo caso.

Pensemos que las personas entran a una sala de a una por vez:

- La primera entra a una sala vacía: tiene los 365 días disponibles, y la
  probabilidad de no chocar con nadie es 365/365 = 1.
- La segunda debe evitar el día que ya ocupó la primera: le quedan 364 días
  libres, con probabilidad 364/365.
- La tercera debe evitar dos días: 363/365.
- Y así hasta la persona K, que debe evitar K−1 días.

Como los cumpleaños son independientes entre sí, la probabilidad de que
_todas_ eviten a las anteriores es el producto de todas esas fracciones:

    P(ninguna coincidencia) = (365/365) × (364/365) × ... × ((365 − K + 1)/365)

Y la probabilidad que buscamos es la contraria:

    P(K) = 1 − (365/365) × (364/365) × ... × ((365 − K + 1)/365)

Evaluando la fórmula se obtienen los valores conocidos:

| K   | P(K)   |
| --- | ------ |
| 10  | 0.1169 |
| 20  | 0.4114 |
| 23  | 0.5073 |
| 30  | 0.7063 |
| 50  | 0.9704 |
| 57  | 0.9901 |

En el código, esta fórmula está implementada en la función
`probabilidad_teorica` de `src/cumpleanos.c`.

### Supuestos del modelo

El cálculo anterior vale bajo tres supuestos que conviene explicitar, porque
en la realidad no se cumplen del todo:

1. **Los 365 días son igualmente probables.** En la práctica los nacimientos
   no se distribuyen de manera uniforme a lo largo del año: hay meses con más
   nacimientos que otros. Esta desviación hace que la probabilidad real de
   coincidencia sea levemente _mayor_ que la calculada.
2. **No se consideran los años bisiestos.** Se ignora el 29 de febrero.
3. **Los cumpleaños son independientes entre sí.** No se contemplan mellizos
   ni grupos formados por familiares.

Estos supuestos son los del enunciado clásico del problema, y son los que
hacen posible comparar la simulación contra una fórmula exacta.

## 3. Metodología de simulación

Para verificar la fórmula de manera empírica utilizamos el **método de Monte
Carlo**, que consiste en resolver un problema determinista mediante muestreo
aleatorio masivo: en lugar de deducir la probabilidad, la observamos generando
muchísimos casos al azar y midiendo con qué frecuencia ocurre el evento.

El algoritmo para cada grupo simulado es:

1. Marcar los 365 días como libres.
2. Para cada una de las K personas, sortear un día al azar entre 0 y 364.
3. Si ese día ya estaba ocupado, el grupo tiene una coincidencia y se pasa al
   siguiente grupo sin sortear las personas restantes.
4. Si no, marcar el día como ocupado y continuar con la siguiente persona.

Repitiendo esto para T grupos, la probabilidad estimada es simplemente:

    P estimada = (grupos con coincidencia) / T

La detección de la coincidencia se hace con un arreglo de 365 posiciones y no
comparando todas las personas contra todas. Esto hace que el costo por grupo
sea proporcional a K y no a K².

### Números pseudoaleatorios

Los números que genera `rand()` no son realmente aleatorios sino
**pseudoaleatorios**: la función aplica una fórmula matemática al número
anterior, de modo que a partir de una semilla toda la secuencia queda
determinada. Esto, lejos de ser un defecto, es deseable en un experimento
numérico, porque permite que cualquiera reproduzca exactamente los mismos
resultados.

Sobre el manejo de las semillas se tomaron dos decisiones:

**Una semilla distinta por proceso.** En la versión paralela cada proceso usa
`12345 + rango`. Si todos usaran la misma, todos sortearían exactamente los
mismos grupos y el resultado equivaldría al de un solo proceso repetido varias
veces, desperdiciando por completo el paralelismo.

**La misma semilla en todas las repeticiones.** Para medir tiempos, las diez
ejecuciones de cada configuración simulan exactamente los mismos grupos. De
esta manera la única variable que cambia entre repeticiones es la cantidad de
procesos, que es precisamente lo que se quiere medir. Si cada repetición
sorteara grupos distintos, la cantidad de trabajo variaría levemente (cuando
un grupo presenta una coincidencia temprana, el algoritmo corta y sortea menos
números) y no se podría atribuir la diferencia de tiempos únicamente al
paralelismo. Como contrapartida, las repeticiones brindan diez mediciones de
tiempo pero una sola muestra estadística de la probabilidad, por lo que el
experimento de convergencia requiere variar la semilla explícitamente.

**Limitación conocida de este esquema.** Las semillas asignadas a los procesos
son consecutivas (12345, 12346, 12347, ...). Dos semillas contiguas producen
secuencias que no son estadísticamente independientes entre sí, porque
provienen de la misma fórmula evaluada desde puntos de partida muy próximos.
En un método de Monte Carlo esto puede hacer que las muestras aporten menos
información de la que su cantidad sugiere, y que la precisión real sea inferior
a la esperada para T simulaciones. En las mediciones realizadas el efecto no se
manifiesta: con 2.000.000 de grupos la estimación difiere del valor teórico en
3 diezmilésimas. Se deja constancia de todos modos porque se trata de una
observación empírica y no de una verificación formal de independencia. La
solución habitual consiste en separar las semillas entre sí, por ejemplo
`12345 + rango * 7919`, o bien emplear un generador diseñado específicamente
para ejecución paralela.

## 4. Implementación paralela

### Qué se puede paralelizar

Cada grupo simulado es completamente independiente de los demás: para saber si
el grupo número 500.000 tiene una coincidencia no hace falta conocer ningún
resultado anterior. Esta independencia total convierte al problema en uno de
los llamados **vergonzosamente paralelos**, donde la parte serial es casi nula
y, según la ley de Amdahl, el speedup alcanzable es prácticamente lineal.

### Distribución del trabajo: versión estática (`src/paralelo-estatico.c`)

Los T grupos se reparten en partes iguales entre los P procesos:

```c
mi_cantidad = cantidad / n_procesos;
if (rango < cantidad % n_procesos)
    mi_cantidad++;
```

Cuando la división no es exacta, los primeros procesos se hacen cargo de los grupos
sobrantes. Sin esa corrección se perderían hasta P−1 grupos y la suma de las
partes no daría el total pedido. Cada proceso simula sus grupos con la semilla
`12345 + rango` sin comunicarse con los demás.

### Distribución del trabajo: versión dinámica (`src/paralelo-dinamico.c`)

Implementa un esquema **maestro-trabajadores**:
- El **proceso 0 (maestro)** no simula: reparte bloques de grupos a pedido.
- Los **procesos 1 a P−1 (trabajadores)** piden un bloque, lo simulan y vuelven
  a pedir otro hasta que no queda trabajo.

Para que la simulación sea determinista y reproducible, la semilla no depende
del proceso sino del bloque: cada bloque usa `12345 + id_bloque`.

El tamaño de bloque es configurable por línea de comandos. Si no se indica, el
código asigna automáticamente unos 20 bloques por trabajador.

### Recolección de resultados

Cada proceso cuenta sus propias coincidencias y al final se suman todas con
una única operación colectiva:

```c
MPI_Reduce(&mis_coincidencias, &total_coincidencias, 1, MPI_LONG,
           MPI_SUM, 0, MPI_COMM_WORLD);
```

Se eligió `MPI_Reduce` en lugar de un esquema con `MPI_Send` y `MPI_Recv`
porque resuelve la suma en una sola llamada, el código queda más claro y la
implementación de MPI puede organizar internamente la comunicación en forma de
árbol, que escala mejor que hacer que todos los procesos le envíen al proceso 0.

Toda la comunicación del programa se reduce a un entero por proceso, lo que
explica el buen speedup obtenido.

### Medición del tiempo

El tiempo se mide con `MPI_Wtime`, precedido de un `MPI_Barrier` para que
todos los procesos comiencen a cronometrar en el mismo instante.

Para obtener el tiempo de la corrida se toma el **máximo** entre los tiempos
de todos los procesos, no el promedio:

```c
MPI_Reduce(&mi_tiempo, &tiempo, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);
```

El criterio es que el trabajo no está terminado hasta que termina el último
proceso: si siete procesos tardan 0.2 s y uno tarda 0.5 s, la corrida duró
0.5 s. Promediar escondería justamente los problemas de balance de carga.

La versión serial también se compila con `mpicc` y mide con `MPI_Wtime`,
siguiendo el criterio del código de la cátedra, para que ambos tiempos sean
comparables entre sí.

## 5. Resultados

### 5.1 Convergencia

_(Pendiente: correr el experimento 1 de docs/como-correr.md)_

Se espera que el error disminuya proporcionalmente a 1/√T, que es la velocidad
de convergencia característica del método de Monte Carlo.

### 5.2 Curva P(K)

_(Pendiente: correr el experimento 2 de docs/como-correr.md)_

### 5.3 Speedup y eficiencia

Mediciones realizadas en la notebook de Nicolás (ver
`resultados/maquina-nicolas.txt`), simulando 2.000.000 de grupos con K=23.
Cada configuración se ejecutó **10 veces** y se reporta la **mediana**, tal
como pide la consigna. Se incluye además el promedio recortado (descartando el
valor mínimo y el máximo) como verificación independiente.

| Procesos | Mediana (s) | Speedup | Eficiencia | Prom. recortado (s) | Speedup |
| -------- | ----------- | ------- | ---------- | ------------------- | ------- |
| 1        | 1.325       | 1.00    | 1.00       | 1.334               | 1.00    |
| 2        | 0.661       | 2.00    | 1.00       | 0.664               | 2.01    |
| 4        | 0.328       | 4.05    | 1.01       | 0.332               | 4.02    |
| 6        | 0.233       | 5.68    | 0.95       | 0.234               | 5.69    |
| 8        | 0.205       | 6.47    | 0.81       | 0.208               | 6.40    |

Fórmulas utilizadas: **Sp = T1 / Tp** y **Ep = Sp / p**.

Gráficos: `resultados/speedup.png` y `resultados/eficiencia.png`.

Observaciones:

- Hasta 4 procesos el speedup es prácticamente **lineal**, con eficiencia
  cercana al 100%. Es el comportamiento esperable en un problema
  vergonzosamente paralelo, donde la comunicación es despreciable frente al
  cómputo.
- Con 6 procesos la eficiencia todavía se mantiene alta (0.95).
- Con 8 procesos la eficiencia cae a 0.81. La causa es el hardware: el
  procesador de esta notebook tiene 6 núcleos de alto rendimiento y 4 de
  eficiencia energética. Al pasar de 6 procesos, el sistema operativo empieza
  a asignar procesos a los núcleos lentos, y como el tiempo de la corrida es
  el del proceso más demorado, esos núcleos frenan al conjunto.
- La coincidencia entre la mediana y el promedio recortado (diferencias
  menores al 1%) indica que las mediciones fueron estables y que no hubo
  corridas anómalas que distorsionen las conclusiones.

### 5.4 Comparación: Estático vs Dinámico

Para comparar ambas estrategias se midieron en el desktop de Sergio (Ryzen 7 9800X3D, 8 núcleos) y en un cluster (AMD EPYC, hasta 96 procesos). Para el dinámico se tomó el mejor tamaño de bloque encontrado:

**Desktop de Sergio (8 núcleos, tiempo serial = 0.601 s):**

| Procesos | T. Estático (s) | Speedup Est. | Efic. Est. | T. Dinámico (s) | Speedup Din. | Efic. Din. | Mejor Bloque |
| -------- | --------------- | ------------ | ---------- | --------------- | ------------ | ---------- | ------------ |
| 2        | 0.288           | 2.08         | 1.04       | 0.571           | 1.05         | 0.53       | 200.000      |
| 4        | 0.147           | 4.09         | 1.02       | 0.192           | 3.13         | 0.78       | 4.255        |
| 6        | 0.098           | 6.14         | 1.02       | 0.115           | 5.23         | 0.87       | 425          |
| 8        | 0.076           | 7.91         | 0.99       | 0.084           | 7.16         | 0.90       | 425          |

**Cluster (AMD EPYC, tiempo serial = 2.319 s):**

| Procesos | T. Estático (s) | Speedup Est. | Efic. Est. | T. Dinámico (s) | Speedup Din. | Efic. Din. | Mejor Bloque |
| -------- | --------------- | ------------ | ---------- | --------------- | ------------ | ---------- | ------------ |
| 2        | 1.156           | 2.01         | 1.00       | 2.309           | 1.00         | 0.50       | 200.000      |
| 4        | 0.580           | 4.00         | 1.00       | 0.774           | 2.99         | 0.75       | 4.255        |
| 6        | 0.388           | 5.98         | 1.00       | 0.465           | 4.99         | 0.83       | 4.255        |
| 8        | 0.291           | 7.96         | 0.99       | 0.333           | 6.97         | 0.87       | 425          |
| 12       | 0.194           | 11.96        | 1.00       | 0.213           | 10.89        | 0.91       | 425          |
| 16       | 0.146           | 15.89        | 0.99       | 0.156           | 14.87        | 0.93       | 425          |
| 24       | 0.099           | 23.55        | 0.98       | 0.102           | 22.74        | 0.95       | 425          |
| 32       | 0.074           | 31.34        | 0.98       | 0.076           | 30.52        | 0.95       | 425          |
| 48       | 0.050           | 46.39        | 0.97       | 0.050           | 46.39        | 0.97       | 425          |
| 64       | 0.037           | 62.69        | 0.98       | 0.038           | 61.04        | 0.95       | 425          |
| 96       | 0.026           | 89.21        | 0.93       | 0.026           | 87.53        | 0.91       | 425          |

Observaciones:

- **El estático es superior al dinámico en casi todos los casos:** El problema es naturalmente homogéneo: cada grupo simula 23 personas y toma casi el mismo tiempo, por lo que no hay desbalance de carga que el dinámico pueda corregir. El estático reparte todo de entrada sin comunicación intermedia.
- **El costo del maestro dedicado:** En el dinámico, el proceso 0 no computa, solo coordina. Con 2 procesos solo 1 trabaja, por eso la eficiencia da ~50%. Con 4 procesos trabajan 3 (máximo teórico 75%).
- **Por qué el dinámico mejora, empata en 48 procesos y decae luego (64 y 96 procesos):**
  Al aumentar la cantidad de procesos, el dinámico mejora porque perder 1 proceso como maestro pesa cada vez menos (pasa de perder el 50% con 2 procesos a solo el 2.1% con 48). Justo en 48 procesos se alcanza un equilibrio óptimo: el costo del maestro es mínimo, los 4.706 bloques de tamaño 425 se dividen casi de forma exacta entre los 47 trabajadores (~100 bloques por trabajador), y el maestro aún no se satura despachando pedidos, empatando al estático en 0.050 s.
  Sin embargo, con 64 y 96 procesos el dinámico vuelve a quedar levemente por detrás del estático por dos razones:
  1. *Contención en el maestro:* La corrida entera dura menos de 40 milisegundos. Tener 63 o 95 trabajadores bombardeando a un único proceso central con pedidos concurrentes satura la cola de mensajes del maestro, obligando a los trabajadores a esperar turno para recibir su bloque.
  2. *Latencia de interconexión:* En clusters de alto rendimiento como el del CCAD, al solicitar 96 núcleos la asignación abarca múltiples sockets o dominios de memoria (e interconexión de red si cruza nodos). Mientras que en el estático los procesos no se comunican y trabajan 100% en memoria local, en el dinámico los miles de mensajes de asignación deben cruzar los enlaces del cluster hacia el nodo del maestro, sumando latencia.
- **Efecto del tamaño de bloque:** Si el bloque es muy chico (ej. 1 o 4 grupos), se generan millones de mensajes y el maestro se satura por la comunicación. Si el bloque es muy grande (ej. 1.000.000), los trabajadores terminan rápido y quedan ociosos esperando al último. El rango óptimo está en el medio, entre 400 y 4.255 grupos por bloque (ver `bloques.png`).
- **La precisión no depende del tamaño de bloque:** En `bloques_precision.png` se observa que el error frente al valor teórico es prácticamente idéntico con cualquier bloque. Esto se debe a que la cantidad total de grupos simulados es la misma (2.000.000) y cada bloque tiene su propia semilla (`12345 + id_bloque`), por lo que terminan siendo exactamente los mismos cálculos divididos de otra forma.

## 6. Conclusiones

1. La simulación reproduce el valor teórico con buena precisión: con 2.000.000 de grupos y K=23 se obtuvo una probabilidad estimada de 0.5070 frente al valor exacto 0.5073, con un error del orden de 0.0003, independiente del tamaño de bloque o esquema utilizado.
2. El problema escala de forma casi lineal en la versión estática hasta la cantidad de núcleos físicos disponibles, alcanzando un speedup de 7.91 con 8 procesos en el Ryzen de Sergio (eficiencia 0.99) y 62.69 con 64 procesos en el cluster AMD EPYC (eficiencia 0.98).
3. A gran escala (64 y 96 procesos en el cluster) el tiempo total sigue reduciéndose hasta 0.026 s, pero con una leve caída en la eficiencia (0.93 en estático y 0.91 en dinámico) debido a la latencia de comunicación entre sockets/nodos y la contención en el paso de mensajes.
4. El speedup obtenido en el reparto estático es notablemente mejor que el de problemas con comunicación intensa, como el producto escalar del TP1, porque aquí la comunicación se reduce a un único entero por proceso al final de la corrida.
5. El paralelismo estático es superior al dinámico en este problema: al ser una carga naturalmente homogénea, el dinámico no aporta ventajas y penaliza con la pérdida de un proceso maestro más la sobrecarga de mensajes continuos.
6. En el dinámico, la eficiencia arranca baja (~50% con 2 procesos al haber un solo trabajador), pero crece con la cantidad de procesos a medida que el costo del maestro se diluye entre más trabajadores.
7. El tamaño de bloque en el dinámico presenta un compromiso claro: bloques muy chicos saturan al maestro de mensajes y bloques muy grandes desbalancean la carga al final.

## 7. Mejoras recomendadas para el futuro

- **Histograma de la primera coincidencia:** registrar en qué tamaño de grupo
  aparece la primera coincidencia y graficar su distribución, usando
  `MPI_Gather` para reunir los datos de todos los procesos.
- **Distribución real de nacimientos:** reemplazar el supuesto de días
  equiprobables por datos reales, y cuantificar cuánto aumenta la probabilidad
  de coincidencia respecto del modelo uniforme.
- **Problema generalizado:** permitir años de D días, lo que conecta el
  problema con las colisiones de funciones de hash en criptografía (el llamado
  _birthday attack_).
- **Semilla configurable por línea de comandos**, necesaria para el
  experimento de convergencia con repeticiones independientes.
- **Separar las semillas de los procesos** (por ejemplo `12345 + rango * 7919`)
  y verificar la independencia de las secuencias comparando la estimación que
  produce cada semilla por separado.
- **Balance de carga dinámico** para máquinas con núcleos de distinta
  velocidad, en lugar del reparto estático actual.
