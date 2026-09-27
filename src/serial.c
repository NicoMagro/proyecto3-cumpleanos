/*
   Paradoja del cumpleanios - version SERIAL (sin MPI)
   Sirve como referencia para calcular el speedup de la version paralela.

   Compilar:  cc src/cumpleanos.c src/serial.c -o serial
   Ejecutar:  ./serial 23 1000000
*/
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "cumpleanos.h"

int main(int argc, char **argv)
{
    int k = 23;                  /* personas por grupo */
    long cantidad = 1000000;     /* cantidad de grupos a simular */
    long coincidencias;
    double p_simulada, p_teorica, tiempo;
    clock_t inicio, fin;

    if (argc > 1) k = atoi(argv[1]);
    if (argc > 2) cantidad = atol(argv[2]);

    if (k < 1 || cantidad < 1)
    {
        printf("Uso: %s [personas] [grupos]\n", argv[0]);
        return 1;
    }

    inicio = clock();
    coincidencias = simular_grupos(k, cantidad, 12345);
    fin = clock();

    tiempo = (double)(fin - inicio) / CLOCKS_PER_SEC;
    p_simulada = (double)coincidencias / cantidad;
    p_teorica = probabilidad_teorica(k);

    printf("Personas por grupo (K) : %d\n", k);
    printf("Grupos simulados       : %ld\n", cantidad);
    printf("Grupos con coincidencia: %ld\n", coincidencias);
    printf("Probabilidad simulada  : %.4f\n", p_simulada);
    printf("Probabilidad teorica   : %.4f\n", p_teorica);
    printf("Error                  : %.4f\n", p_simulada - p_teorica);
    printf("Tiempo                 : %.3f segundos\n", tiempo);

    /* Linea con formato CSV, para juntar resultados de varias corridas */
    printf("csv,%d,%ld,1,%.6f,%.6f,%.3f\n",
           k, cantidad, p_simulada, p_teorica, tiempo);

    return 0;
}
