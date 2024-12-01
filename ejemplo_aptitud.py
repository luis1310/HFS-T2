from Aptitud.funcion_fitness import *
from Aptitud.funcion_fitness_DEMO import *

# Ejemplo de cromosoma para 3 pedidos
cromosoma = [[1, 4, 6, 10, 11], [2, 5, 8, 9, 11], [3, 5, 6, 10, 11]]

cromosoma2 = [[2, 4, 7, 10, 11], [2, 5, 7, 10, 11], [2, 4, 7, 9, 11]]

# Ejemplo para 4 pedidos
cromosoma3 = [[1, 4, 6, 10, 11], [2, 5, 8, 9, 11], [3, 5, 6, 10, 11], [2, 4, 7, 9, 11]]

print(cromosoma)
fit = fitness_DEMO(cromosoma, tiempos_iniciales, incrementos)
print("\n############################################################\n")
print("Tiempo de trabajo (Makespam):", 1 / fit)
print("Fitness:", fit)

print(
    "\n############################## OTRO CROMOSOMA ##############################\n"
)


print(cromosoma2)
fit2 = fitness_DEMO(cromosoma2, tiempos_iniciales, incrementos)
print("\n############################################################\n")
print("Tiempo de trabajo (Makespam):", 1 / fit2)
print("Fitness:", fit2)


print(
    "\n############################## OTRO CROMOSOMA ##############################\n"
)


print(cromosoma3)
fit3 = fitness_DEMO(cromosoma3, tiempos_iniciales, incrementos)
print("\n############################################################\n")
print("Tiempo de trabajo (Makespam):", 1 / fit3)
print("Fitness:", fit3)
