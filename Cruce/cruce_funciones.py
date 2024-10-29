from Parametros.Parametros_tot import *
from Aptitud.funcion_fitness import *
# Modificación de la funcion de cruce, se extrae todo el métdo para que cruce una población completa
"""
# Modificación v0.7
Se añade otro metodo de cruzamiento

# Modificación v0.7.1
Se modifica los metodos de cruzamiento para que solo tomen los padres

# Modificación v0.8
Ahora la funcion de cruce añade el hijo/padre que tenga mejor fitness
"""
##################################### modificación v0.8 ####################################
# Cruce en 1 punto:
def cruce(padre1, padre2, pc=tasa_cruzamiento, fitness=fitness):
    # Calcular el fitness de los padres
    fitness_padre1 = fitness(padre1)
    fitness_padre2 = fitness(padre2)
    hijos = []
    test = []
    if random.random() < pc:
        # Realizar cruce si pasa el umbral de probabilidad pc
        punto_cruce = random.randint(1, len(padre1) - 1)
        hijo1 = padre1[:punto_cruce] + padre2[punto_cruce:]
        hijo2 = padre2[:punto_cruce] + padre1[punto_cruce:]

        # Calcular el fitness de los hijos
        fitness_hijo1 = fitness(hijo1)
        fitness_hijo2 = fitness(hijo2)

        # Comparar fitness de los hijos y padres
        if fitness_hijo1 >= fitness_padre1:
            hijos.append(hijo1)
        else:
            hijos.append(padre1)  # Mantener al padre1 si hijo1 es peor

        if fitness_hijo2 >= fitness_padre2:
            hijos.append(hijo2)
        else:
            hijos.append(padre2)  # Mantener al padre2 si hijo2 es peor
    else:
        # No se realiza cruce, los hijos son iguales a los padres
        hijos.append(padre1)
        hijos.append(padre2)

    return hijos


##################################### modificación v0.7 ####################################

# Cruce en 2 puntos:
def cruce2(padre1, padre2, pc=tasa_cruzamiento):
    hijos = []
    if random.random() < pc:  
        punto_cruce1 = random.randint(1, len(padre1) - 2)
        punto_cruce2 = random.randint(punto_cruce1 + 1, len(padre1))
        hijo1 = padre1[:punto_cruce1] + padre2[punto_cruce1:punto_cruce2] + padre1[punto_cruce2:]
        hijo2 = padre2[:punto_cruce1] + padre1[punto_cruce1:punto_cruce2] + padre2[punto_cruce2:]
        hijos.append(hijo1)
        hijos.append(hijo2)
    else:
        # No se realiza cruce, los hijos son iguales a los padres
        hijos.append(padre1)
        hijos.append(padre2)

    return hijos

