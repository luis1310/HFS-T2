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

# Modificación v0.9
Ahora la funcion de cruce toma los dos mejores individuos entre los padres y los hijos producto del cruzamiento
"""


# Cruce en 1 punto:
##################################### modificación v0.9 ####################################
def cruce_1_punto(padre1, padre2, pc=tasa_cruzamiento, fitness=fitness):
    hijos = []
    # Realizar el cruce si pasa el umbral de probabilidad pc
    if random.random() < pc:
        punto_cruce = random.randint(1, len(padre1) - 1)
        hijo1 = padre1[:punto_cruce] + padre2[punto_cruce:]
        hijo2 = padre2[:punto_cruce] + padre1[punto_cruce:]

        # Calcular fitness para todos los individuos (padres e hijos)
        individuos = [
            (padre1, fitness(padre1)),
            (padre2, fitness(padre2)),
            (hijo1, fitness(hijo1)),
            (hijo2, fitness(hijo2)),
        ]

        # Ordenar por fitness y seleccionar los dos mejores
        individuos.sort(key=lambda x: x[1], reverse=True)
        # Solo devolver los mejores individuos
        hijos.append(individuos[0][0])
        hijos.append(individuos[1][0])

    else:
        # No se realiza cruce, los hijos son iguales a los padres
        hijos.append(padre1)
        hijos.append(padre2)
    return hijos


##################################### modificación v0.7 ####################################


##################################### modificación v0.9.1 ####################################
# Cruce en 2 puntos v0.1
def cruce_2_puntos(padre1, padre2, pc=tasa_cruzamiento, fitness=fitness):
    hijos = []
    if random.random() < pc:
        # Realizar el cruce si pasa el umbral de probabilidad pc
        punto_cruce1 = random.randint(1, len(padre1) - 2)
        punto_cruce2 = random.randint(punto_cruce1 + 1, len(padre1))
        hijo1 = (
            padre1[:punto_cruce1]
            + padre2[punto_cruce1:punto_cruce2]
            + padre1[punto_cruce2:]
        )
        hijo2 = (
            padre2[:punto_cruce1]
            + padre1[punto_cruce1:punto_cruce2]
            + padre2[punto_cruce2:]
        )

        # Calcular fitness para todos los individuos (padres e hijos)
        individuos = [
            (padre1, fitness(padre1)),
            (padre2, fitness(padre2)),
            (hijo1, fitness(hijo1)),
            (hijo2, fitness(hijo2)),
        ]

        # Ordenar por fitness y seleccionar los dos mejores
        individuos.sort(key=lambda x: x[1], reverse=True)

        # Solo devolver los mejores individuos
        hijos.append(hijo1)
        hijos.append(hijo2)

    else:
        # No se realiza cruce, los hijos son iguales a los padres
        hijos.append(padre1)
        hijos.append(padre2)

    return hijos


##################################### modificación v0.9.1 ####################################
