from Parametros.Parametros_tot import *

"""
# Modificacion v0.8:
Ahora la funcion, que genera la población, solo genera individuos unicos al trabajar con conjuntos y tuplas
"""
################################
"""
# Población v0.2
def inicializar_poblacion(tamano_poblacion, maquinas_por_etapa, num_pedidos):
    poblacion = [
        [[random.choice(maquinas_por_etapa[i]) for i in range(5)] for _ in range(num_pedidos)]
        for _ in range(tamano_poblacion)
    ]
    return poblacion
"""
################################
######################## modificacion v0.8 ########################


def inicializar_poblacion(
    tamano_poblacion=tamano_poblacion,
    maquinas_por_etapa=maquinas_por_etapa,
    num_pedidos=num_pedidos,
):
    poblacion = []
    individuos_existentes = set()

    while len(poblacion) < tamano_poblacion:
        # Genera un nuevo individuo
        individuo = [
            [random.choice(maquinas_por_etapa[i]) for i in range(5)]
            for _ in range(num_pedidos)
        ]

        # Convierte el individuo a una tupla de tuplas para que sea hashable y se pueda añadir al conjunto
        individuo_tuple = tuple(tuple(pedido) for pedido in individuo)

        # Añadir solo si es único
        if individuo_tuple not in individuos_existentes:
            poblacion.append(individuo)
            individuos_existentes.add(individuo_tuple)

    return poblacion
