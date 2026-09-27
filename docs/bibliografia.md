# Bibliografía

> **Importante:** citar solamente lo que efectivamente leímos. Las obras
> listadas abajo son las referencias estándar del tema, pero antes de dejarlas
> en el informe final hay que consultarlas de verdad, aunque sea el capítulo
> puntual que nos interesa. En una defensa oral es habitual que pregunten de
> dónde sacamos algo.

## Material de la cátedra

- **Teoría HPC 2026.** Métodos Numéricos II / Computación Científica,
  FACET-UNT. De acá salen las definiciones que usamos: speedup Sp = T1/Tp,
  eficiencia, ley de Amdahl, la clasificación de los problemas
  "vergonzosamente paralelos" y los tiempos de ejecución (Tproc, Tcom, Tidle).
- **Trabajo Práctico 1: HPC (2026).** De acá tomamos el uso de `MPI_Reduce`
  en lugar de `MPI_Send`/`MPI_Recv`, la medición con `MPI_Wtime` y el criterio
  de calcular el speedup con la mediana de múltiples ejecuciones.

## Paradoja del cumpleaños

- Grinstead, C. M. y Snell, J. L. *Introduction to Probability*, 2ª edición.
  American Mathematical Society, 1997. Disponible libremente en
  https://math.dartmouth.edu/~prob/prob/prob.pdf
  El problema del cumpleaños se desarrolla en el capítulo de probabilidad
  discreta, con la deducción por el complemento que usamos en la sección 2.
- Ross, S. M. *A First Course in Probability*. Pearson.
  Texto clásico de probabilidad; trata el problema del cumpleaños como
  ejemplo de cálculo por complemento.

## Método de Monte Carlo

- Metropolis, N. y Ulam, S. "The Monte Carlo Method". *Journal of the American
  Statistical Association*, vol. 44, n.º 247, 1949, pp. 335-341.
  Artículo fundacional del método.
- Sobre la velocidad de convergencia 1/√T: cualquier texto de métodos de
  Monte Carlo lo deduce del teorema central del límite. Verificar en el
  material de la cátedra si se vio en clase, y citar esa fuente si es así.

## Computación paralela y MPI

- Amdahl, G. M. "Validity of the single processor approach to achieving large
  scale computing capabilities". *AFIPS Conference Proceedings*, vol. 30,
  1967, pp. 483-485. Es la fuente original de la ley de Amdahl que aparece en
  la teoría de la materia.
- Pacheco, P. *An Introduction to Parallel Programming*. Morgan Kaufmann, 2011.
  Texto introductorio estándar de programación paralela con MPI.
- Gropp, W., Lusk, E. y Skjellum, A. *Using MPI: Portable Parallel Programming
  with the Message-Passing Interface*. MIT Press.
  Referencia detallada sobre las operaciones colectivas como `MPI_Reduce`.
- **Documentación de Open MPI:** https://www.open-mpi.org/doc/
  Consultada para las firmas exactas de `MPI_Reduce`, `MPI_Wtime` y
  `MPI_Barrier`, y para los tipos de datos (`MPI_LONG`, `MPI_DOUBLE`).
- **MPI Forum, el estándar oficial:** https://www.mpi-forum.org/docs/
  Documento de referencia del estándar MPI.

## Para completar

- [ ] Buscar si la cátedra dio material específico sobre Monte Carlo.
- [ ] Si usamos el dato de que los nacimientos no se distribuyen uniformemente
      a lo largo del año (sección 2 del informe), conseguir una fuente real con
      estadísticas y citarla. Si no conseguimos una, sacar esa afirmación o
      dejarla explícitamente como comentario sin respaldo.
