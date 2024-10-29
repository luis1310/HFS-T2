from Parametros.Parametros_tot import *
"""
# Modificacion de la funcion de mutación, las maquinas por etapa son añadidas a los parametros
# Se actualiza la funcion de mutación

# Modificacion v0.8
Modificación de la función de mutación, muta a una maquina de un pedido a otra distinta (de haber una disponible)
"""
# Mutación1 v0.6
def mutacion1(poblacion, maquinas_por_etapa=maquinas_por_etapa, tasa_mutacion=tasa_mutacion):
    for individuo in poblacion:
        if random.random() < tasa_mutacion:
            for pedido in individuo:
                # Seleccionar el punto de mutación
                punto_mutacion = random.randint(0, len(pedido) - 2)
                maquina_actual = pedido[punto_mutacion]

                # Filtrar para evitar que se seleccione la misma máquina
                opciones_mutacion = [m for m in maquinas_por_etapa[punto_mutacion] if m != maquina_actual]

                # Solo mutar si hay una opción diferente disponible
                if opciones_mutacion:
                    nueva_maquina = random.choice(opciones_mutacion)
                    pedido[punto_mutacion] = nueva_maquina

    return poblacion