from Parametros.Parametros_tot import *

"""
# Modificacion de la funcion de mutación, las maquinas por etapa son añadidas a los parametros
# Se actualiza la funcion de mutación

# Modificacion v0.8
Modificación de la función de mutación, muta a una maquina de un pedido a otra distinta (de haber una disponible)

# Modificacion v0.9
Añadida funcion de mutacion #2: mutacion de intercambio por etapa
"""


# Mutación aleatoria v0.8
def mutacion_aleatoria(
    poblacion, tasa_mutacion=tasa_mutacion, maquinas_por_etapa=maquinas_por_etapa
):
    for individuo in poblacion:
        if random.random() < tasa_mutacion:
            for pedido in individuo:
                # Seleccionar el punto de mutación
                punto_mutacion = random.randint(0, len(pedido) - 2)
                maquina_actual = pedido[punto_mutacion]

                # Filtrar para evitar que se seleccione la misma máquina
                opciones_mutacion = [
                    m for m in maquinas_por_etapa[punto_mutacion] if m != maquina_actual
                ]

                # Solo mutar si hay una opción diferente disponible
                if opciones_mutacion:
                    nueva_maquina = random.choice(opciones_mutacion)
                    pedido[punto_mutacion] = nueva_maquina

    return poblacion


########################## modificacion v0.9 ##########################


## Mutación de intercambio por etapa
def mutacion_intercambio_por_etapa(
    poblacion, tasa_mutacion=tasa_mutacion, maquinas_por_etapa=maquinas_por_etapa
):
    for individuo in poblacion:
        if random.random() < tasa_mutacion:
            for etapa in range(len(maquinas_por_etapa)):
                # Selecciona aleatoriamente dos pedidos en el individuo para intercambiar en esta etapa
                pedidos_a_intercambiar = random.sample(range(len(individuo)), 2)

                # Realiza el intercambio dentro de la misma etapa
                maquina1 = individuo[pedidos_a_intercambiar[0]][etapa]
                maquina2 = individuo[pedidos_a_intercambiar[1]][etapa]

                # Intercambiar las máquinas de los dos pedidos seleccionados en la misma etapa
                (
                    individuo[pedidos_a_intercambiar[0]][etapa],
                    individuo[pedidos_a_intercambiar[1]][etapa],
                ) = (maquina2, maquina1)

    return poblacion
