from Parametros.Parametros_tot import *
from Aptitud.funcion_fitness import *

#Seleccion 1 v0.1
def seleccion_por_torneo(poblacion, k):
    seleccionados = []
    
    for _ in range(len(poblacion)):
        torneo = random.sample(poblacion, k)
        # Modificado la forma en que se halla el ganador del torneo
        mejor = max(torneo, key=lambda cromosoma: fitness(cromosoma, tiempos_iniciales, incrementos))
        seleccionados.append(mejor)

    return seleccionados
