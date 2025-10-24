from Parametros.Parametros_tot import *
import numpy as np


def fitness_multiobjetivo(cromosoma, tiempos_iniciales=tiempos_iniciales, incrementos=incrementos):
    """
    Función fitness multiobjetivo que evalúa 4 objetivos:
    1. Makespan (tiempo total de finalización)
    2. Balance de carga entre máquinas (desviación estándar)
    3. Penalización por enfriamientos
    4. Consumo energético total
    
    Returns:
        tuple: (objetivo1, objetivo2, objetivo3, objetivo4)
            - objetivo1: 1/makespan (para maximizar, como antes)
            - objetivo2: 1/(desviacion_std + 1) (maximizar balance)
            - objetivo3: 1/(num_enfriamientos + 1) (minimizar enfriamientos)
            - objetivo4: 1/(energia_total + 1) (minimizar consumo energético)
    """
    
    # Inicializar los tiempos de disponibilidad de cada máquina
    disponibilidad_maquinas = {
        i: 0 for i in range(1, num_maquinas + 1)
    }
    tiempos_actuales = tiempos_iniciales[:]
    
    # Rastrear tiempo total de uso por máquina (para balance de carga)
    tiempo_uso_maquinas = {i: 0 for i in range(1, num_maquinas + 1)}
    
    # Contador de enfriamientos por máquina
    enfriamientos_por_maquina = {i: 0 for i in range(1, num_maquinas + 1)}
    num_enfriamientos = 0
    tiempo_enfriamiento_total = 0
    
    # Variable para almacenar el tiempo total (makespan)
    tiempo_total = 0

    for pedido in cromosoma:
        tiempo_pedido = 0

        for maquina in pedido:
            # Verificar el tiempo disponible de la máquina asignada
            tiempo_inicio = max(disponibilidad_maquinas[maquina], tiempo_pedido)

            # Calcular el tiempo de trabajo de la máquina actual
            tiempo_trabajo = tiempos_actuales[maquina - 1]

            # Verificar si el tiempo de la máquina excede el límite de enfriamiento
            requiere_enfriamiento = False
            if tiempo_trabajo >= tiempos_iniciales[maquina - 1] * limite_enfriamiento:
                requiere_enfriamiento = True
                num_enfriamientos += 1
                enfriamientos_por_maquina[maquina] += 1
                tiempo_enfriamiento_total += tiempo_enfriamiento
                tiempo_trabajo += tiempo_enfriamiento
                tiempo_trabajo *= factor_enfriamiento

            # Actualizar tiempo de trabajo de la máquina
            tiempos_actuales[maquina - 1] *= 1 + incrementos[maquina - 1]

            # Actualizar tiempo de finalización de la máquina
            disponibilidad_maquinas[maquina] = tiempo_inicio + tiempo_trabajo
            
            # Acumular tiempo de uso de esta máquina
            tiempo_uso_maquinas[maquina] += tiempo_trabajo

            # Actualizar el tiempo total del pedido
            tiempo_pedido = tiempo_inicio + tiempo_trabajo

        # El tiempo total será el mayor tiempo entre todos los pedidos
        tiempo_total = max(tiempo_total, tiempo_pedido)

    # ====== CÁLCULO DE LOS 4 OBJETIVOS ======
    
    # Objetivo 1: Makespan (minimizar tiempo total)
    # Invertido para poder maximizar en el algoritmo evolutivo
    objetivo_makespan = 1 / tiempo_total if tiempo_total > 0 else 0
    
    # Objetivo 2: Balance de carga (minimizar desviación estándar)
    # Calcular desviación estándar de tiempos de uso
    tiempos_uso = list(tiempo_uso_maquinas.values())
    desviacion_std = np.std(tiempos_uso)
    # Invertido para maximizar el balance (menor desviación = mejor)
    objetivo_balance = 1 / (desviacion_std + 1)
    
    # Objetivo 3: Minimizar enfriamientos
    # Penalización por número de enfriamientos y tiempo perdido
    penalizacion_enfriamiento = num_enfriamientos + (tiempo_enfriamiento_total / 100)
    # Invertido para maximizar (menos enfriamientos = mejor)
    objetivo_enfriamiento = 1 / (penalizacion_enfriamiento + 1)
    
    # Objetivo 4: Minimizar consumo energético
    # Calcular energía total consumida (en kWh)
    energia_total = 0
    for i in range(1, num_maquinas + 1):
        # Tiempo que la máquina estuvo activa (en horas)
        tiempo_activo_hrs = tiempo_uso_maquinas[i] / 60
        # Tiempo que la máquina estuvo inactiva (en horas)
        tiempo_inactivo_hrs = (tiempo_total - tiempo_uso_maquinas[i]) / 60
        
        # Energía consumida en estado activo
        energia_activa = potencias_activas[i - 1] * tiempo_activo_hrs
        # Energía consumida en estado inactivo
        energia_inactiva = potencias_inactivas[i - 1] * tiempo_inactivo_hrs
        # Energía extra por enfriamientos
        energia_enfriamiento_maquina = enfriamientos_por_maquina[i] * energia_por_enfriamiento
        
        energia_total += energia_activa + energia_inactiva + energia_enfriamiento_maquina
    
    # Invertido para maximizar (menos energía = mejor)
    objetivo_energia = 1 / (energia_total + 1)
    
    return objetivo_makespan, objetivo_balance, objetivo_enfriamiento, objetivo_energia


def fitness_multiobjetivo_demo(cromosoma, tiempos_iniciales=tiempos_iniciales, incrementos=incrementos):
    """
    Versión DEMO de la función fitness multiobjetivo con impresión de detalles
    """
    
    # Inicializar
    disponibilidad_maquinas = {i: 0 for i in range(1, num_maquinas + 1)}
    tiempos_actuales = tiempos_iniciales[:]
    tiempo_uso_maquinas = {i: 0 for i in range(1, num_maquinas + 1)}
    enfriamientos_por_maquina = {i: 0 for i in range(1, num_maquinas + 1)}
    num_enfriamientos = 0
    tiempo_enfriamiento_total = 0
    tiempo_total = 0

    print("\n" + "="*70)
    print("EVALUACIÓN MULTIOBJETIVO DEL CROMOSOMA (4 OBJETIVOS)")
    print("="*70)

    for pedido_idx, pedido in enumerate(cromosoma):
        tiempo_pedido = 0
        print(f"\nPedido {pedido_idx + 1} pasando por las máquinas:")

        for etapa, maquina in enumerate(pedido):
            tiempo_inicio = max(disponibilidad_maquinas[maquina], tiempo_pedido)
            
            if tiempo_inicio > tiempo_pedido:
                print(f"  Etapa {etapa + 1} | Máquina {maquina} - EN COLA")

            tiempo_trabajo = tiempos_actuales[maquina - 1]
            
            # Verificar enfriamiento
            requiere_enfriamiento = False
            if tiempo_trabajo >= tiempos_iniciales[maquina - 1] * limite_enfriamiento:
                requiere_enfriamiento = True
                num_enfriamientos += 1
                enfriamientos_por_maquina[maquina] += 1
                tiempo_enfriamiento_total += tiempo_enfriamiento
                tiempo_trabajo += tiempo_enfriamiento
                tiempo_trabajo *= factor_enfriamiento

            tiempo_trabajo_real = tiempo_trabajo
            tiempos_actuales[maquina - 1] *= 1 + incrementos[maquina - 1]
            disponibilidad_maquinas[maquina] = tiempo_inicio + tiempo_trabajo_real
            tiempo_uso_maquinas[maquina] += tiempo_trabajo_real
            tiempo_pedido = tiempo_inicio + tiempo_trabajo_real

            estado = " ENFRIAMIENTO" if requiere_enfriamiento else " Normal"
            print(f"  Etapa {etapa + 1} | Máquina {maquina} - {estado} (tiempo: {tiempo_trabajo_real:.2f}s)")

        tiempo_total = max(tiempo_total, tiempo_pedido)

    # Calcular objetivos
    objetivo_makespan = 1 / tiempo_total if tiempo_total > 0 else 0
    
    tiempos_uso = list(tiempo_uso_maquinas.values())
    desviacion_std = np.std(tiempos_uso)
    objetivo_balance = 1 / (desviacion_std + 1)
    
    penalizacion_enfriamiento = num_enfriamientos + (tiempo_enfriamiento_total / 100)
    objetivo_enfriamiento = 1 / (penalizacion_enfriamiento + 1)
    
    # Calcular energía total
    energia_total = 0
    energia_por_maquina = {}
    for i in range(1, num_maquinas + 1):
        tiempo_activo_hrs = tiempo_uso_maquinas[i] / 60
        tiempo_inactivo_hrs = (tiempo_total - tiempo_uso_maquinas[i]) / 60
        
        energia_activa = potencias_activas[i - 1] * tiempo_activo_hrs
        energia_inactiva = potencias_inactivas[i - 1] * tiempo_inactivo_hrs
        energia_enfriamiento_maq = enfriamientos_por_maquina[i] * energia_por_enfriamiento
        
        energia_maquina = energia_activa + energia_inactiva + energia_enfriamiento_maq
        energia_por_maquina[i] = energia_maquina
        energia_total += energia_maquina
    
    objetivo_energia = 1 / (energia_total + 1)

    # Resultados
    print("\n" + "="*70)
    print("RESULTADOS DE LA EVALUACIÓN MULTIOBJETIVO (4 OBJETIVOS)")
    print("="*70)
    print(f"\n OBJETIVO 1 - MAKESPAN:")
    print(f"   Tiempo total: {tiempo_total:.2f}s")
    print(f"   Fitness makespan: {objetivo_makespan:.8f}")
    
    print(f"\n  OBJETIVO 2 - BALANCE DE CARGA:")
    print(f"   Desviación estándar: {desviacion_std:.2f}s")
    print(f"   Tiempo promedio por máquina: {np.mean(tiempos_uso):.2f}s")
    print(f"   Máquina más cargada: {max(tiempos_uso):.2f}s")
    print(f"   Máquina menos cargada: {min(tiempos_uso):.2f}s")
    print(f"   Fitness balance: {objetivo_balance:.8f}")
    
    print(f"\n  OBJETIVO 3 - ENFRIAMIENTOS:")
    print(f"   Número de enfriamientos: {num_enfriamientos}")
    print(f"   Tiempo total perdido por enfriamiento: {tiempo_enfriamiento_total:.2f}s")
    print(f"   Fitness enfriamiento: {objetivo_enfriamiento:.8f}")
    
    print(f"\n OBJETIVO 4 - CONSUMO ENERGÉTICO:")
    print(f"   Energía total consumida: {energia_total:.2f} kWh")
    print(f"   Energía promedio por máquina: {energia_total/11:.2f} kWh")
    print(f"   Máquina con mayor consumo: {max(energia_por_maquina.values()):.2f} kWh (Máq {max(energia_por_maquina, key=energia_por_maquina.get)})")
    print(f"   Máquina con menor consumo: {min(energia_por_maquina.values()):.2f} kWh (Máq {min(energia_por_maquina, key=energia_por_maquina.get)})")
    print(f"   Fitness energía: {objetivo_energia:.8f}")
    
    print("\n" + "="*70)
    print(f"VECTOR DE OBJETIVOS: ({objetivo_makespan:.6f}, {objetivo_balance:.6f}, {objetivo_enfriamiento:.6f}, {objetivo_energia:.6f})")
    print("="*70 + "\n")
    
    return objetivo_makespan, objetivo_balance, objetivo_enfriamiento, objetivo_energia