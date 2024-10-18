import random
import time

# Parámetros del problema
tiempos_iniciales = [55, 53, 56, 42, 41, 30, 34, 35, 28, 26, 20]
asignaciones_por_etapa = [3, 2, 3, 2, 1]
incremento_min = 0.03
incremento_max = 0.03
incrementos = [random.uniform(incremento_min, incremento_max) for _ in range(11)]
# Parámetros del enfriamiento (Tiempo de enfriamiento en segundos)
limite_enfriamiento = 1.30
factor_enfriamiento = 0.85
tiempo_enfriamiento = 6
# Parámetros del algoritmo
num_pedidos = 40
poblacion_size = 50
num_generaciones = 100