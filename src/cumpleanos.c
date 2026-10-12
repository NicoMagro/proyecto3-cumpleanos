#include <stdlib.h>
#include "cumpleanos.h"

long simular_grupos(int k, long cantidad, unsigned int semilla)
{
    int cumpleanios[DIAS]; // cumpleanios[d] = 1 si alguien cumple el dia d
    long con_coincidencia = 0;
    long g;
    int i, dia, hay_coincidencia;

    srand(semilla); // cada proceso usa una semilla distinta

    for (g = 0; g < cantidad; g++)
    {
        // Empezamos un grupo nuevo: ningun dia esta ocupado todavia
        for (i = 0; i < DIAS; i++)
            cumpleanios[i] = 0;

        hay_coincidencia = 0;

        // Le sorteamos un cumpleanios a cada una de las k personas
        for (i = 0; i < k; i++)
        {
            dia = rand() % DIAS;

            if (cumpleanios[dia] == 1)
            {
                // Ese dia ya estaba ocupado: encontramos la coincidencia
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
    // Se calcula el complemento (ninguna coincidencia) y se hace 1 - eso,
    // evitando sumar todos los casos posibles de coincidencia.
    double sin_coincidencia = 1.0;
    int i;

    // Con mas de 365 personas la coincidencia es segura (y el bucle
    // multiplicaria por cero o por numeros negativos).
    if (k > DIAS)
        return 1.0;

    // Producto de (DIAS - i)/DIAS: al entrar la persona i quedan (DIAS - i)
    // dias libres, y para que NINGUNA choque hay que multiplicar todas.
    for (i = 0; i < k; i++)
        sin_coincidencia = sin_coincidencia * (DIAS - i) / DIAS;

    // Complemento: con k = 23 esto da 0.5073.
    return 1.0 - sin_coincidencia;
}
