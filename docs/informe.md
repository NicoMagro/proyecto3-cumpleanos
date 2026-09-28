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

### Distribución del trabajo

Los T grupos se reparten en partes iguales entre los P procesos:

```c
mi_cantidad = cantidad / n_procesos;
if (rango == 0)
    mi_cantidad = mi_cantidad + (cantidad % n_procesos);
```

Cuando la división no es exacta, el proceso 0 se hace cargo de los grupos
sobrantes. Sin esa corrección se perderían hasta P−1 grupos y la suma de las
partes no daría el total pedido.

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

### 5.4 Comparación entre sistemas

_(Pendiente: correr el experimento 3 en las otras dos notebooks y en el
servidor de la facultad)_

## 6. Conclusiones

_(Pendiente hasta completar los experimentos 1, 2 y 4. Lo que ya se puede
afirmar:)_

1. La simulación reproduce el valor teórico con buena precisión: con 2.000.000
   de grupos y K=23 se obtuvo una probabilidad estimada de 0.5070 frente al
   valor exacto 0.5073, con un error del orden de 0.0003.
2. El problema escala muy bien hasta la cantidad de núcleos físicos de alto
   rendimiento disponibles, alcanzando un speedup de 5.68 con 6 procesos
   (eficiencia 0.95).
3. Aumentar la cantidad de procesos más allá de los núcleos rápidos disponibles
   sigue mejorando el tiempo total, pero con eficiencia decreciente.
4. El speedup obtenido es notablemente mejor que el de problemas con
   comunicación intensa, como el producto escalar del TP1, porque aquí la
   comunicación total se limita a un entero por proceso.

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
