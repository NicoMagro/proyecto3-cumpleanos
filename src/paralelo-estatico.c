/*
   Paradoja del cumpleanios - version PARALELA ESTATICA con MPI

   Los grupos a simular se reparten de forma fija y equitativa entre los procesos.
   Cada proceso cuenta sus coincidencias y al final se suman todas con MPI_Reduce.

   Compilar:  mpicc src/cumpleanos.c src/paralelo-estatico.c -o paralelo-estatico
   Ejecutar:  mpirun -n 4 ./paralelo-estatico 23 1000000
*/
#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include "cumpleanos.h"

int main(int argc, char **argv)
{
    int rango, n_procesos;
    int k = 23;
    long cantidad = 1000000;
    long mi_cantidad, mis_coincidencias, total_coincidencias;
    double inicio, mi_tiempo, tiempo, p_simulada, p_teorica;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rango);
    MPI_Comm_size(MPI_COMM_WORLD, &n_procesos);

    if (argc > 1) k = atoi(argv[1]);
    if (argc > 2) cantidad = atol(argv[2]);

    if (k < 1 || cantidad < 1)
    {
        if (rango == 0)
            printf("Uso: mpirun -n P %s [personas] [grupos]\n", argv[0]);
        MPI_Finalize();
        return 1;
    }

    /* Repartimos los grupos entre los procesos */
    mi_cantidad = cantidad / n_procesos;

    
    /* Si la division no es exacta, el proceso que tenga rango menor a la 
       cantidad de grupos que sobran, aumenta su cantidad en 1*/
    if (rango < cantidad % n_procesos)
        mi_cantidad++;

    /* Todos arrancan a medir al mismo tiempo */
    MPI_Barrier(MPI_COMM_WORLD);
    inicio = MPI_Wtime();

    /* Cada proceso usa una semilla distinta. Si todos usaran la misma,
       simularian exactamente los mismos grupos y el resultado seria
       como haber hecho una sola parte repetida varias veces. */
    mis_coincidencias = simular_grupos(k, mi_cantidad, 12345 + rango);

    mi_tiempo = MPI_Wtime() - inicio;

    printf("Proceso %d: simule %ld grupos y encontre %ld coincidencias\n",
           rango, mi_cantidad, mis_coincidencias);

    /* Sumamos las coincidencias de todos los procesos en el proceso 0 */
    MPI_Reduce(&mis_coincidencias, &total_coincidencias, 1, MPI_LONG,
               MPI_SUM, 0, MPI_COMM_WORLD);

    /* El tiempo de la corrida es el del proceso que mas tardo, porque
       el trabajo no termina hasta que termina el ultimo */
    MPI_Reduce(&mi_tiempo, &tiempo, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

    if (rango == 0)
    {
        p_simulada = (double)total_coincidencias / cantidad;
        p_teorica = probabilidad_teorica(k);

        printf("\n");
        printf("Procesos               : %d\n", n_procesos);
        printf("Personas por grupo (K) : %d\n", k);
        printf("Grupos simulados       : %ld\n", cantidad);
        printf("Grupos con coincidencia: %ld\n", total_coincidencias);
        printf("Probabilidad simulada  : %.4f\n", p_simulada);
        printf("Probabilidad teorica   : %.4f\n", p_teorica);
        printf("Error                  : %.4f\n", p_simulada - p_teorica);
        printf("Tiempo                 : %.3f segundos\n", tiempo);

        printf("csv,%d,%ld,%d,0,%.6f,%.6f,%.3f\n",
            k, cantidad, n_procesos, p_simulada, p_teorica, tiempo);
    }

    MPI_Finalize();
    return 0;
}
