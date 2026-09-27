#include <stdlib.h>
#include "cumpleanos.h"

long simular_grupos(int k, long cantidad, unsigned int semilla)
{
    int cumpleanios[DIAS];   /* cumpleanios[d] = 1 si alguien cumple el dia d */
    long con_coincidencia = 0;
    long g;
    int i, dia, hay_coincidencia;

    srand(semilla);   /* cada proceso usa una semilla distinta */

    for (g = 0; g < cantidad; g++)
    {
        /* Empezamos un grupo nuevo: ningun dia esta ocupado todavia */
        for (i = 0; i < DIAS; i++)
            cumpleanios[i] = 0;

        hay_coincidencia = 0;

        /* Le sorteamos un cumpleanios a cada una de las k personas */
        for (i = 0; i < k; i++)
        {
            dia = rand() % DIAS;

            if (cumpleanios[dia] == 1)
            {
                /* Ese dia ya estaba ocupado: encontramos la coincidencia */
                hay_coincidencia = 1;
                break;
            }
            cumpleanios[dia] = 1;
        }

        if (hay_coincidencia == 1)
            con_coincidencia++;
    }

    return con_coincidencia;
}

double probabilidad_teorica(int k)
{
    /*
       Calcular directamente "que al menos dos coincidan" es complicado,
       porque habria que sumar muchos casos: que coincidan dos, que
       coincidan tres, que haya dos pares distintos, etc.

       Por eso calculamos LO CONTRARIO, que es un solo caso y es facil:
       que las k personas cumplan todas en dias diferentes. Al final
       hacemos 1 - ese valor.
    */
    double sin_coincidencia = 1.0;
    int i;

    /* Con mas de 365 personas no alcanzan los dias para darle uno distinto
       a cada una, asi que la coincidencia es segura.
       Ademas, sin este if el bucle llegaria a i = 365 y empezaria a
       multiplicar por cero y por numeros negativos. */
    if (k > DIAS)
        return 1.0;

    /*
       Vamos metiendo a las personas en la sala de a una y preguntamos que
       probabilidad hay de que la que entra NO choque con las anteriores.

       i es el contador de personas: i = 0 es la primera persona que entra,
       i = 1 la segunda, y asi hasta la persona numero k.

       (DIAS - i) son los DIAS LIBRES que quedan, no personas. Cada persona
       que entro antes ocupo un dia, y le deja uno menos a la siguiente:

           i = 0  ->  entra la 1a persona  ->  365 dias libres  ->  365/365
           i = 1  ->  entra la 2a persona  ->  364 dias libres  ->  364/365
           i = 2  ->  entra la 3a persona  ->  363 dias libres  ->  363/365

       Como las personas son independientes entre si, para que NINGUNA
       choque hay que multiplicar todas esas probabilidades.

       Ojo con el orden de la cuenta: primero se multiplica por
       sin_coincidencia, que es un double. Si se escribiera
       ((DIAS - i) / DIAS) se dividirian dos enteros y C haria division
       entera: 364/365 daria 0 en lugar de 0.9972.
    */
    for (i = 0; i < k; i++)
        sin_coincidencia = sin_coincidencia * (DIAS - i) / DIAS;

    /* Ya tenemos la probabilidad de que no haya ninguna coincidencia.
       La que buscamos es la contraria. Con k = 23 esto da 0.5073. */
    return 1.0 - sin_coincidencia;
}
