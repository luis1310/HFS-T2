from Aptitud.funcion_fitness import *
from Aptitud.funcion_fitness_DEMO import *

# Ejemplo de cromosoma para 3 pedidos
cromosoma = [
    [1, 4, 6, 10, 11],
    [2, 5, 8, 9, 11],
    [3, 5, 6, 10, 11],
    [2, 4, 7, 9, 11]
]
#fit = fitness(cromosoma, tiempos_iniciales, incrementos)
fit = fitness_DEMO(cromosoma, tiempos_iniciales, incrementos)
print("\n############################################################\n")
print("Tiempo de trabajo (Makespam):", 1/fit)
print("Fitness:", fit)
