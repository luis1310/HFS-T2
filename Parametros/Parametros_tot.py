import random
import time

# Parámetros del problema
tiempos_iniciales = [55, 53, 56, 42, 41, 30, 34, 35, 28, 26, 20]
asignaciones_por_etapa = [3, 2, 3, 2, 1]
incremento_min = 0.02
incremento_max = 0.04
#incrementos = [random.uniform(incremento_min, incremento_max) for _ in range(11)]
# Incrementos para pruebas
incrementos = [0.023506023208672008, 0.037596856948261224, 0.029790852610943303, 0.026482371652136807, 0.0343115347257827, 0.02008422307621436, 0.02354833935682637, 0.03583131181255757, 0.02692514188853341, 0.03854356701956932, 0.026871837367560457]

# Parámetros del enfriamiento (Tiempo de enfriamiento en segundos)
limite_enfriamiento = 1.30
factor_enfriamiento = 0.85
tiempo_enfriamiento = 6
# Parámetros del algoritmo
num_pedidos = 3
poblacion_size = 50
num_generaciones = 500

