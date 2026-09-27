/*
   Paradoja del cumpleanios - version SERIAL (un solo proceso)
   Sirve como referencia para calcular el speedup: es el T1 de la formula
   Sp = T1 / Tp.

   Igual que el codigo serial de la catedra, se compila con mpicc y usa
   MPI_Wtime para medir el tiempo, aunque no haga nada en paralelo. Esto es
   para medir igual que la version paralela y poder comparar los tiempos.

   Compilar:  mpicc src/cumpleanos.c src/serial.c -o serial
   Ejecutar:  ./serial 23 1000000
*/
#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include "cumpleanos.h"

int main(int argc, char **argv)
{
    int k = 23;                  /* personas por grupo */
    long cantidad = 1000000;     /* cantidad de grupos a simular */
    long coincidencias;
    double p_simulada, p_teorica;
    double t_inicio, t_fin, tiempo;

    MPI_Init(&argc, &argv);

    /* Los argumentos llegan como texto: atoi y atol los pasan a numero */
    if (argc > 1) k = atoi(argv[1]);
    if (argc > 2) cantidad = atol(argv[2]);

    if (k < 1 || cantidad < 1)
    {
        printf("Uso: %s [personas] [grupos]\n", argv[0]);
        MPI_Finalize();
        return 1;
    }

    /* Medimos solo la simulacion, que es la parte pesada */
    t_inicio = MPI_Wtime();
    coincidencias = simular_grupos(k, cantidad, 12345);
    t_fin = MPI_Wtime();

    tiempo = t_fin - t_inicio;
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

    MPI_Finalize();
    return 0;
}
