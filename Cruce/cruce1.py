from Parametros.Parametros_tot import *
# Modificación de la funcion de cruce, se extrae todo el métdo para que cruce una población completa
#Cruce v0.1
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
