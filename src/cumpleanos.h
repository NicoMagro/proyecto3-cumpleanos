#ifndef CUMPLEANOS_H
#define CUMPLEANOS_H

#define DIAS 365

/*
   Simula "cantidad" grupos de "k" personas y devuelve cuantos de esos
   grupos tuvieron al menos dos personas con el mismo cumpleanios.
*/
long simular_grupos(int k, long cantidad, unsigned int semilla);

/*
   Probabilidad teorica de que en un grupo de k personas haya al menos
   una coincidencia:  P(k) = 1 - (365/365)*(364/365)*...*((365-k+1)/365)
*/
double probabilidad_teorica(int k);

#endif
