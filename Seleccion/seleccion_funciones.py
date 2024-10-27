from Parametros.Parametros_tot import *
from Aptitud.funcion_fitness import *
# Se añadio el parametro fitness_values para no calcularlo en la función de selección misma
# Seleccion 1 v0.3
def seleccion_por_torneo(poblacion, fitness_values, k):
    seleccionados = []
    
    for _ in range(len(poblacion)):
        torneo = random.sample(range(len(poblacion)), k)
        # Modificado la forma en que se halla el ganador del torneo
        mejor_idx = max(torneo, key=lambda idx: fitness_values[idx])
        seleccionados.append(poblacion[mejor_idx])

    return seleccionados

##################################### modificación v0.7 ####################################

# Seleccion 2 v0.1
# Selección por Ruleta
def seleccion_por_ruleta(poblacion, fitness_values):
    total_fitness = sum(fitness_values)
    padres = []

    # Normalizar el fitness para obtener probabilidades
    probabilidades = [fitness / total_fitness for fitness in fitness_values]

    # Selección basada en las probabilidades
    for _ in range(len(poblacion)):
        seleccionado = random.choices(poblacion, weights=probabilidades, k=1)[0]
        padres.append(seleccionado)

    return padres

# Seleccion 3 v0.1
# Selección Basada en Ranking
def seleccion_por_ranking(poblacion, fitness_values):
    # Ordenar la población en función del fitness
    indices_ordenados = sorted(range(len(fitness_values)), key=lambda i: fitness_values[i])

    # Asignar probabilidades basadas en el ranking (el mejor tiene el mayor índice)
    ranks = [i + 1 for i in range(len(fitness_values))]
    total_rank = sum(ranks)
    probabilidades = [rank / total_rank for rank in ranks]

    # Invertir el orden para que el mejor tenga mayor probabilidad
    probabilidades = probabilidades[::-1]

    # Seleccionar padres con base en la probabilidad de los rankings
    padres = []
    for _ in range(len(poblacion)):
        seleccionado = random.choices(poblacion, weights=probabilidades, k=1)[0]
        padres.append(seleccionado)

    return padres

