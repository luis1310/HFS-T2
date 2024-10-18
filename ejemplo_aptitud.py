from Aptitud.funcion_fitness import *

# Ejemplo de cromosoma para 3 pedidos
cromosoma = [
    [1, 4, 6, 10, 11],
    [2, 5, 8, 9, 11],
    [3, 5, 6, 10, 11]
]

print("Tiempo total:", 1/fitness(cromosoma, tiempos_iniciales, incrementos))
print("Fitness:", fitness(cromosoma, tiempos_iniciales, incrementos))
