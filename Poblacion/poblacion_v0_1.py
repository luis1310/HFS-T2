from Parametros.Parametros_tot import *

##Población

def inicializar_poblacion(size, num_pedidos):
    poblacion = []
    for _ in range(size):
        cromosoma = []
        for _ in range(num_pedidos):
            pedido = []
            for etapa, num_maquinas in enumerate(asignaciones_por_etapa):
                maquina_asignada = random.randint(1, num_maquinas)
                pedido.append(maquina_asignada)
            cromosoma.append(pedido)
        poblacion.append(cromosoma)
    return poblacion
