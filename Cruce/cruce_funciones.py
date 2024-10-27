from Parametros.Parametros_tot import *
# Modificación de la funcion de cruce, se extrae todo el métdo para que cruce una población completa
# Cruce v0.2
def cruce(poblacion):
    nueva_poblacion = []
    for i in range(0, len(poblacion), 2):
        padre1, padre2 = poblacion[i], poblacion[i+1] if i + 1 < len(poblacion) else poblacion[0]
        punto_cruce = random.randint(1, len(padre1) - 1)
        hijo1 = padre1[:punto_cruce] + padre2[punto_cruce:]
        hijo2 = padre2[:punto_cruce] + padre1[punto_cruce:]
        nueva_poblacion.append(hijo1)
        nueva_poblacion.append(hijo2)
    return nueva_poblacion


##################################### modificación v0.7 ####################################

# Cruce en 2 puntos v0.1
def cruce2(poblacion):
    nueva_poblacion = []
    for i in range(0, len(poblacion), 2):
        padre1 = poblacion[i]
        padre2 = poblacion[i + 1] if i + 1 < len(poblacion) else poblacion[0]
        punto_cruce1 = random.randint(1, len(padre1) - 2)
        punto_cruce2 = random.randint(punto_cruce1 + 1, len(padre1))
        hijo1 = padre1[:punto_cruce1] + padre2[punto_cruce1:punto_cruce2] + padre1[punto_cruce2:]
        hijo2 = padre2[:punto_cruce1] + padre1[punto_cruce1:punto_cruce2] + padre2[punto_cruce2:]
        nueva_poblacion.append(hijo1)
        nueva_poblacion.append(hijo2)
    return nueva_poblacion

