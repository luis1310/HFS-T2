from Algoritmo_evo.algoritmo_evo import *

poblacion = inicializar_poblacion(tamano_poblacion, maquinas_por_etapa, num_pedidos)
# Ejecutar el algoritmo
inicio = time.time()
mejor_individuo, mejor_fitness, mejor_generacion=algoritmo_evolutivo(
    poblacion, tamano_poblacion,tiempos_iniciales, incrementos, maquinas_por_etapa, num_generaciones, k, tasa_mutacion, prop_elitismo
    )
fin = time.time()
print("\n########################################################\n")
print('Tiempo de ejecución: ')
print(fin - inicio)
print (f"Tiempo del cromosoma encontrado :  {1/mejor_fitness:.16f}")

