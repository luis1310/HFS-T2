from Parametros.Parametros_tot import *
from Aptitud.funcion_fitness_v0_1 import *
#Seleccion 1 v0.1
def seleccion_por_torneo(poblacion, k=3):
    seleccionados = []

    for _ in range(len(poblacion)):
        torneo = random.sample(poblacion, k)
        mejor = max(torneo, key=fitness)
        seleccionados.append(mejor)

    return seleccionados
