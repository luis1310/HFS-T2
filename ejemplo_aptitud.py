from Aptitud.funcion_fitness_v0_1 import *

# Ejemplo de cromosoma para 3 pedidos
cromosoma = [
    [1, 4, 6, 9, 11],
    [2, 5, 7, 10, 11],
    [3, 5, 6, 9, 11]
]

print("Tiempo total:", 1/calcular_tiempo_total(cromosoma))
print("Fitness:", calcular_tiempo_total(cromosoma))
