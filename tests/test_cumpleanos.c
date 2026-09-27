/*
   Tests de las funciones de src/cumpleanos.c

   Compilar:  cc src/cumpleanos.c tests/test_cumpleanos.c -o test
   Ejecutar:  ./test
*/
#include <stdio.h>
#include <math.h>
#include "../src/cumpleanos.h"

int errores = 0;

/* Compara dos numeros con un margen de tolerancia */
void verificar(const char *nombre, double obtenido, double esperado, double margen)
{
    if (fabs(obtenido - esperado) <= margen)
    {
        printf("OK   %s (obtuvo %.4f, esperaba %.4f)\n", nombre, obtenido, esperado);
    }
    else
    {
        printf("MAL  %s (obtuvo %.4f, esperaba %.4f)\n", nombre, obtenido, esperado);
        errores++;
    }
}

int main(void)
{
    long coincidencias;
    double p;

    printf("--- Probabilidad teorica ---\n");
    verificar("P(1) tiene que ser 0", probabilidad_teorica(1), 0.0, 0.0001);
    verificar("P(23) es el caso famoso", probabilidad_teorica(23), 0.5073, 0.0001);
    verificar("P(57) es casi seguro", probabilidad_teorica(57), 0.9901, 0.0001);
    verificar("P(400) tiene que ser 1", probabilidad_teorica(400), 1.0, 0.0001);

    printf("\n--- Simulacion ---\n");

    /* Con una sola persona nunca puede haber coincidencia */
    coincidencias = simular_grupos(1, 1000, 12345);
    verificar("con K=1 no hay coincidencias", (double)coincidencias, 0.0, 0.0);

    /* Con 366 personas y 365 dias siempre hay coincidencia */
    coincidencias = simular_grupos(366, 1000, 12345);
    verificar("con K=366 siempre hay", (double)coincidencias, 1000.0, 0.0);

    /* La misma semilla tiene que dar siempre el mismo resultado */
    verificar("la misma semilla da lo mismo",
              (double)simular_grupos(23, 5000, 999),
              (double)simular_grupos(23, 5000, 999), 0.0);

    /* Con muchos grupos la simulacion se tiene que parecer a la teoria.
       El margen de 0.005 es el error estadistico esperable con 200000 grupos. */
    coincidencias = simular_grupos(23, 200000, 2026);
    p = (double)coincidencias / 200000;
    verificar("K=23 se acerca a la teoria", p, probabilidad_teorica(23), 0.005);

    coincidencias = simular_grupos(50, 200000, 2026);
    p = (double)coincidencias / 200000;
    verificar("K=50 se acerca a la teoria", p, probabilidad_teorica(50), 0.005);

    printf("\n");
    if (errores == 0)
        printf("Todos los tests pasaron.\n");
    else
        printf("Fallaron %d tests.\n", errores);

    return errores;
}
