from Algoritmo_evo.algoritmo_evo import *

poblacion = inicializar_poblacion(poblacion_size, num_pedidos)
# Ejecutar el algoritmo
inicio = time.time()
mejor_individuo, mejor_fitness, mejor_generacion=algoritmo_evolutivo(poblacion, poblacion_size,tiempos_iniciales, incrementos, maquinas_por_etapa, num_generaciones, k, tasa_mutacion)
fin = time.time()
print("\n########################################################\n")
print('Tiempo de ejecución: ')
print(fin - inicio)
print ("Tiempo del cromosoma encontrado:", 1/mejor_fitness)

