from Parametros.Parametros_tot import *
from Aptitud.funcion_fitness import *

"""
# Se añadio el parametro fitness_values para no calcularlo en la función de selección misma
# Modificación v0.7
Se añaden las funciones de seleccion por ranking y por ruleta
# Modificación v0.7.1
Modificación y corrección de las funciones de selección
"""


# Seleccion 1: Seleccion por torneo
def seleccion_por_torneo(poblacion, fitness_values, k=k):
    padres = []
    for _ in range(2):
        torneo = random.sample(range(len(poblacion)), k)
        mejor_idx = max(torneo, key=lambda idx: fitness_values[idx])
        padres.append(poblacion[mejor_idx])
    return padres


# Seleccion 2: Selección por Ruleta
def seleccion_por_ruleta(poblacion, fitness_values):
    total_fitness = sum(fitness_values)
    padres = []

    # Normalizar el fitness para obtener probabilidades
    probabilidades = [fitness / total_fitness for fitness in fitness_values]

    # Selección basada en las probabilidades
    for _ in range(2):
        seleccionado = random.choices(poblacion, weights=probabilidades, k=1)[0]
        padres.append(seleccionado)

    return padres


# Seleccion 3: Selección Basada en Ranking
def seleccion_por_ranking(poblacion, fitness_values):
    # Ordenar la población en función del fitness
    indices_ordenados = sorted(
        range(len(fitness_values)), key=lambda i: fitness_values[i]
    )
    poblacion_ordenada = [poblacion[i] for i in indices_ordenados]
    fitness_ordenado = [fitness_values[i] for i in indices_ordenados]

    # Asignar probabilidades basadas en el ranking (el mejor tiene el mayor índice)
    ranks = [i + 1 for i in range(len(fitness_ordenado))]
    total_rank = sum(ranks)
    probabilidades = [rank / total_rank for rank in ranks]

    # Invertir el orden para que el mejor tenga mayor probabilidad
    probabilidades = probabilidades[::-1]
    poblacion_ordenada = poblacion_ordenada[::-1]  # Alinear con las probabilidades

    # Seleccionar padres con base en la probabilidad de los rankings
    padres = []
    for _ in range(2):
        seleccionado = random.choices(poblacion_ordenada, weights=probabilidades, k=1)[0]
        padres.append(seleccionado)

    return padres
