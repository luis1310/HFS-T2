from Parametros.Parametros_tot import *

#Cruce v0.1
def cruce(padre1, padre2):
    punto_cruce = random.randint(1, len(padre1) - 2)

    hijo1 = padre1[:punto_cruce] + padre2[punto_cruce:]
    hijo2 = padre2[:punto_cruce] + padre1[punto_cruce:]

    return hijo1, hijo2
