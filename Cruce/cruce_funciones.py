from Parametros.Parametros_tot import *
# Modificación de la funcion de cruce, se extrae todo el métdo para que cruce una población completa
"""
# Modificación v0.7
Se añade otro metodo de cruzamiento

# Modificación v0.7.1
Se modifica los metodos de cruzamiento para que solo tomen los padres
"""
# Cruce en 1 punto:
def cruce(padre1, padre2, pc=tasa_cruzamiento):
    hijos = []
    if random.random() < pc:
        punto_cruce = random.randint(1, len(padre1) - 1)
        hijo1 = padre1[:punto_cruce] + padre2[punto_cruce:]
        hijo2 = padre2[:punto_cruce] + padre1[punto_cruce:]
        hijos.append(hijo1)
        hijos.append(hijo2)
    else:
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

