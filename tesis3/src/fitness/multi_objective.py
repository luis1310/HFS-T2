
"""Función de fitness multiobjetivo (4 objetivos)"""
import numpy as np


def fitness_multiobjetivo(chromosome, config):
    """
    Evalúa 4 objetivos: makespan, balance, enfriamientos, energía
    
    Args:
        chromosome: Instancia de Chromosome
        config: Instancia de ProblemConfig
    
    Returns:
        tuple: (obj_makespan, obj_balance, obj_enfriamiento, obj_energia)
    """
    genes = chromosome.genes
    tiempos_iniciales = config.tiempos_iniciales
    incrementos = config.incrementos
    limite_enfriamiento = config.enfriamiento['limite']
    factor_enfriamiento = config.enfriamiento['factor']
    tiempo_enfriamiento = config.enfriamiento['tiempo']
    
    # Inicializar
    disponibilidad_maquinas = {i: 0 for i in range(1, config.num_maquinas + 1)}
    tiempos_actuales = tiempos_iniciales[:]
    tiempo_uso_maquinas = {i: 0 for i in range(1, config.num_maquinas + 1)}
    enfriamientos_por_maquina = {i: 0 for i in range(1, config.num_maquinas + 1)}
    
    num_enfriamientos = 0
    tiempo_enfriamiento_total = 0
    tiempo_total = 0
    
    # Procesar cada pedido
    for pedido in genes:
        tiempo_pedido = 0
        
        for maquina in pedido:
            tiempo_inicio = max(disponibilidad_maquinas[maquina], tiempo_pedido)
            tiempo_trabajo = tiempos_actuales[maquina - 1]
            
            # Verificar enfriamiento
            if tiempo_trabajo >= tiempos_iniciales[maquina - 1] * limite_enfriamiento:
                num_enfriamientos += 1
                enfriamientos_por_maquina[maquina] += 1
                tiempo_enfriamiento_total += tiempo_enfriamiento
                tiempo_trabajo += tiempo_enfriamiento
                tiempo_trabajo *= factor_enfriamiento
            
            # Actualizar tiempos
            tiempos_actuales[maquina - 1] *= 1 + incrementos[maquina - 1]
            disponibilidad_maquinas[maquina] = tiempo_inicio + tiempo_trabajo
            tiempo_uso_maquinas[maquina] += tiempo_trabajo
            tiempo_pedido = tiempo_inicio + tiempo_trabajo
        
        tiempo_total = max(tiempo_total, tiempo_pedido)
    
    # Calcular objetivos
    objetivo_makespan = 1 / tiempo_total if tiempo_total > 0 else 0
    
    tiempos_uso = list(tiempo_uso_maquinas.values())
    desviacion_std = np.std(tiempos_uso)
    objetivo_balance = 1 / (desviacion_std + 1)
    
    penalizacion_enfriamiento = num_enfriamientos + (tiempo_enfriamiento_total / 100)
    objetivo_enfriamiento = 1 / (penalizacion_enfriamiento + 1)
    
    # Calcular energía
    potencias_activas = config.energia['potencias_activas']
    potencias_inactivas = config.energia['potencias_inactivas']
    energia_por_enfriamiento = config.energia['energia_por_enfriamiento']
    
    energia_total = 0
    for i in range(1, config.num_maquinas + 1):
        tiempo_activo_hrs = tiempo_uso_maquinas[i] / 60
        tiempo_inactivo_hrs = (tiempo_total - tiempo_uso_maquinas[i]) / 60
        
        energia_activa = potencias_activas[i - 1] * tiempo_activo_hrs
        energia_inactiva = potencias_inactivas[i - 1] * tiempo_inactivo_hrs
        energia_enfriamiento_maq = enfriamientos_por_maquina[i] * energia_por_enfriamiento
        
        energia_total += energia_activa + energia_inactiva + energia_enfriamiento_maq
    
    objetivo_energia = 1 / (energia_total + 1)
    
    return objetivo_makespan, objetivo_balance, objetivo_enfriamiento, objetivo_energia
