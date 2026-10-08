/*
   Paradoja del cumpleanios - version PARALELA DINAMICA con MPI (maestro-trabajadores)

   El proceso 0 (maestro) no simula: solo reparte bloques de grupos a pedido.
   Cada trabajador pide un bloque, lo simula y vuelve a pedir otro hasta que
   el maestro le responde que ya no queda trabajo. Asi los procesos mas rapidos
   hacen mas bloques y nadie queda esperando a los demas.

   Cada trabajador acumula sus coincidencias localmente y las envia una sola
   vez al final con MPI_Reduce, por lo que durante la ejecucion solo viajan
   mensajes muy pequenios (pedido de trabajo y asignacion de bloque).

   Compilar:  mpicc src/cumpleanos.c src/paralelo-dinamico.c -o paralelo-dinamico
   Ejecutar:  mpirun -n 4 ./paralelo-dinamico 23 1000000 5000
              (personas, grupos y tamanio de bloque; los tres son opcionales)
*/
#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include "cumpleanos.h"

#define TAG_PEDIDO  1   /* trabajador -> maestro: "dame trabajo"        */
#define TAG_TRABAJO 2   /* maestro -> trabajador: bloque a simular       */

int main(int argc, char **argv)
{
    int rango, n_procesos;
    int k = 23;
    long cantidad = 1000000;
    long bloque = 0;                /* 0 = elegir automaticamente */
    long mis_coincidencias = 0, total_coincidencias;
    long mis_grupos = 0, mis_bloques = 0;
    double inicio, mi_tiempo, tiempo, p_simulada, p_teorica;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rango);
    MPI_Comm_size(MPI_COMM_WORLD, &n_procesos);

    if (argc > 1) k = atoi(argv[1]);
    if (argc > 2) cantidad = atol(argv[2]);
    if (argc > 3) bloque = atol(argv[3]);

    if (k < 1 || cantidad < 1 || bloque < 0)
    {
        if (rango == 0)
            printf("Uso: mpirun -n P %s [personas] [grupos] [tamanio_bloque]\n", argv[0]);
        MPI_Finalize();
        return 1;
    }

    int n_trabajadores = (n_procesos > 1) ? n_procesos - 1 : 1;

    /* Tamanio de bloque automatico: unos 20 bloques por trabajador.
       Pocos bloques desbalancean la carga; demasiados llenan la red de mensajes. */
    if (bloque == 0)
    {
        bloque = cantidad / ((long)n_trabajadores * 20);
        if (bloque < 1) bloque = 1;
    }
    if (bloque > cantidad) bloque = cantidad;

    /* Todos arrancan a medir al mismo tiempo */
    MPI_Barrier(MPI_COMM_WORLD);
    inicio = MPI_Wtime();

    if (n_procesos == 1)
    {
        /* Sin trabajadores: el unico proceso hace todo en forma secuencial */
        mis_coincidencias = simular_grupos(k, cantidad, 12345);
        mis_grupos = cantidad;
        mis_bloques = 1;
    }
    else if (rango == 0)
    {
        /* ---------------- MAESTRO ---------------- */
        long siguiente = 0;          /* proximo grupo sin asignar */
        long id_bloque = 0;          /* numero de bloque (sirve de semilla) */
        int terminados = 0;          /* trabajadores que ya terminaron */
        int pedido;
        long mensaje[2];             /* {id del bloque, cantidad de grupos} */
        MPI_Status estado;

        while (terminados < n_trabajadores)
        {
            /* Espera el pedido de cualquier trabajador */
            MPI_Recv(&pedido, 1, MPI_INT, MPI_ANY_SOURCE, TAG_PEDIDO,
                     MPI_COMM_WORLD, &estado);

            if (siguiente < cantidad)
            {
                long resto = cantidad - siguiente;
                mensaje[0] = id_bloque++;
                mensaje[1] = (resto < bloque) ? resto : bloque; /* ultimo bloque puede ser menor */
                siguiente += mensaje[1];
            }
            else
            {
                mensaje[0] = -1;
                mensaje[1] = 0;      /* 0 grupos = no hay mas trabajo */
                terminados++;
            }

            MPI_Send(mensaje, 2, MPI_LONG, estado.MPI_SOURCE, TAG_TRABAJO,
                     MPI_COMM_WORLD);
        }
    }
    else
    {
        /* ---------------- TRABAJADORES ---------------- */
        int pedido = 0;
        long mensaje[2];

        while (1)
        {
            MPI_Send(&pedido, 1, MPI_INT, 0, TAG_PEDIDO, MPI_COMM_WORLD);
            MPI_Recv(mensaje, 2, MPI_LONG, 0, TAG_TRABAJO, MPI_COMM_WORLD,
                     MPI_STATUS_IGNORE);

            if (mensaje[1] == 0)
                break;

            /* La semilla depende del numero de bloque, no del proceso:
               cada bloque es distinto y el resultado total no cambia
               aunque los bloques se repartan de otra manera. */
            mis_coincidencias += simular_grupos(k, mensaje[1], 12345 + mensaje[0]);
            mis_grupos += mensaje[1];
            mis_bloques++;
        }
    }

    mi_tiempo = MPI_Wtime() - inicio;

    if (rango != 0 || n_procesos == 1)
        printf("Proceso %d: simule %ld grupos en %ld bloques y encontre %ld coincidencias\n",
               rango, mis_grupos, mis_bloques, mis_coincidencias);

    /* Sumamos las coincidencias de todos los procesos en el proceso 0
       (el maestro aporta 0) */
    MPI_Reduce(&mis_coincidencias, &total_coincidencias, 1, MPI_LONG,
               MPI_SUM, 0, MPI_COMM_WORLD);

    /* El tiempo de la corrida es el del proceso que mas tardo */
    MPI_Reduce(&mi_tiempo, &tiempo, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

    if (rango == 0)
    {
        p_simulada = (double)total_coincidencias / cantidad;
        p_teorica = probabilidad_teorica(k);

        printf("\n");
        printf("Procesos               : %d (1 maestro + %d trabajadores)\n",
               n_procesos, (n_procesos > 1) ? n_procesos - 1 : 0);
        printf("Personas por grupo (K) : %d\n", k);
        printf("Grupos simulados       : %ld\n", cantidad);
        printf("Tamanio de bloque      : %ld\n", bloque);
        printf("Grupos con coincidencia: %ld\n", total_coincidencias);
        printf("Probabilidad simulada  : %.4f\n", p_simulada);
        printf("Probabilidad teorica   : %.4f\n", p_teorica);
        printf("Error                  : %.4f\n", p_simulada - p_teorica);
        printf("Tiempo                 : %.3f segundos\n", tiempo);

        printf("csv,%d,%ld,%d,%ld,%.6f,%.6f,%.3f\n",
               k, cantidad, n_procesos, bloque, p_simulada, p_teorica, tiempo);
    }

    MPI_Finalize();
    return 0;
}