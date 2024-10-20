from Parametros.Parametros_tot import *

# Función fitness v0.2
def fitness_DEMO(cromosoma, tiempos_iniciales, incrementos):
    tiempos_actuales = []
    # Inicializar los tiempos de disponibilidad de cada máquina
    disponibilidad_maquinas = {i: 0 for i in range(1, 12)}  # máquinas 1 a 11
    tiempos_actuales = tiempos_iniciales[:]
    
    # Variable para almacenar el tiempo total
    tiempo_total = 0

    for pedido_idx, pedido in enumerate(cromosoma):
        tiempo_pedido = 0
        # Imprimir el paso de un pedido a traves de las maquinas:
        print(f"\nPedido {pedido_idx + 1} pasando por las máquinas:")

        for etapa, maquina in enumerate(pedido):
            # Verificar el tiempo disponible de la máquina asignada
            # Tiempo que esta máquina terminará de procesar este pedido
            tiempo_inicio = max(disponibilidad_maquinas[maquina], tiempo_pedido)
            # Imprimir Estado "En cola" de un pedido en una maquina
            if tiempo_inicio > tiempo_pedido:
                print(f"Pedido {pedido_idx + 1} en espera en la etapa {etapa + 1} (cola) en máquina {maquina}")
            
            # Calcular el tiempo de trabajo de la máquina actual
            tiempo_trabajo = tiempos_actuales[maquina - 1]

            # Modificado el orden de ejecución, primero se verificará el tiempo de la maquina para que no exceda el límite de enfriamiento
            # posteriormente se actualizan los tiempos de trabajo de las maquinas

            # Verificar si el tiempo de la máquina excede el límite de enfriamiento
            if tiempo_trabajo >= tiempos_iniciales[maquina - 1] * limite_enfriamiento:
                tiempo_trabajo += tiempo_enfriamiento   # Añadir el tiempo de enfriamiento
                tiempo_trabajo *= factor_enfriamiento   # Reducir el tiempo posterior al enfriamiento
            
            # Actualizar tiempo de trabajo de la máquina, los incrementos estarán precalculados en la sección de parametros
            tiempo_trabajo_real = tiempo_trabajo
            tiempos_actuales[maquina - 1] *= (1 + incrementos[maquina - 1])

            # Actualizar tiempo de finalización de la máquina, para verificar su disponibilidad
            disponibilidad_maquinas[maquina] = tiempo_inicio + tiempo_trabajo_real

            # Actualizar el tiempo total del pedido (se suma el tiempo en esta etapa)
            tiempo_pedido = tiempo_inicio + tiempo_trabajo_real

            # Imprimir estado delpedido al pasar de una maquina a otra:
            print(f"Pedido {pedido_idx + 1} pasa por máquina {maquina} en etapa {etapa + 1} (tiempo: {tiempo_trabajo:.2f} s)")

        # El tiempo total será el mayor tiempo entre todos los pedidos
        tiempo_total = max(tiempo_total, tiempo_pedido)

    return 1/tiempo_total
