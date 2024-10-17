from Parametros.Parametros_tot import *

def fitness(cromosoma):
    tiempos_actuales = maquinas_tiempos_iniciales[:]
    tiempos_fin_maquinas = [0] * len(maquinas_tiempos_iniciales)

    for pedido in cromosoma:
        tiempo_inicial_pedido = 0

        for etapa, maquina in enumerate(pedido):
            # Tiempo que esta máquina terminará de procesar este pedido
            tiempo_inicio = max(tiempos_fin_maquinas[maquina - 1], tiempo_inicial_pedido)
            tiempo_trabajo = tiempos_actuales[maquina - 1]

            # Actualizar tiempo de trabajo de la máquina
            incremento = random.uniform(incremento_min, incremento_max)
            tiempos_actuales[maquina - 1] *= (1 + incremento)

            # Si la máquina supera el límite del 130%, se enfría
            if tiempos_actuales[maquina - 1] >= maquinas_tiempos_iniciales[maquina - 1] * limite_enfriamiento:
                tiempos_actuales[maquina - 1] *= factor_enfriamiento
                tiempo_trabajo += tiempo_enfriamiento

            # Actualizar tiempo de finalización de la máquina
            tiempos_fin_maquinas[maquina - 1] = tiempo_inicio + tiempo_trabajo

            # El pedido ahora pasará a la siguiente etapa, así que actualizamos el tiempo de inicio
            tiempo_inicial_pedido = tiempos_fin_maquinas[maquina - 1]
            tiempo_max= max(tiempos_fin_maquinas)

    return 1/tiempo_max
