from Algoritmo_evo.algoritmo_evo import *

poblacion = inicializar_poblacion(poblacion_size, num_pedidos)
# Ejecutar el algoritmo
inicio = time.time()
algoritmo_evolutivo(num_generaciones, poblacion, incrementos, tiempos_iniciales)
fin = time.time()
print("########################################################")
print('Tiempo de ejecución: ')
print(fin - inicio)