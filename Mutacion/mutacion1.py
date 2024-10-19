from Parametros.Parametros_tot import *
## Modificaci´n de la funcion de mutación, las maquinas por etapa son añadidas a los parametros
# Se actualiza la funcion de mutación
##Mutación1 v0.3
def mutacion(poblacion, maquinas_por_etapa, tasa_mutacion):
    for individuo in poblacion:
        if random.random() < tasa_mutacion:
            punto_mutacion = random.randint(0, len(individuo[0]) - 1)
            nueva_maquina = random.choice(maquinas_por_etapa[punto_mutacion])
            for pedido in individuo:
                pedido[punto_mutacion] = nueva_maquina
    return poblacion
