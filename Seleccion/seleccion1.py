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
