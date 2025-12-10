"""Función de fitness multiobjetivo (3 objetivos)"""
import numpy as np


def fitness_multiobjetivo(chromosome, config):
    """
    Evalúa 3 objetivos: makespan, balance, energía
    El enfriamiento afecta el makespan pero no es un objetivo separado
    
    Args:
        chromosome: Instancia de Chromosome
        config: Instancia de ProblemConfig
    
    Returns:
        tuple: (obj_makespan, obj_balance, obj_energia)
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
    
    tiempo_total = 0
    
    # Procesar cada pedido
    for pedido in genes:
        tiempo_pedido = 0
        
        for maquina in pedido:
            tiempo_inicio = max(disponibilidad_maquinas[maquina], tiempo_pedido)
            tiempo_trabajo = tiempos_actuales[maquina - 1]
            
            # Verificar enfriamiento (afecta el makespan pero no es objetivo)
            if tiempo_trabajo >= tiempos_iniciales[maquina - 1] * limite_enfriamiento:
                tiempo_trabajo += tiempo_enfriamiento  # Añadir tiempo de enfriamiento
                tiempo_trabajo *= factor_enfriamiento   # Reducir eficiencia
            
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
    objetivo_balance = 1 / (desviacion_std + 1) ## Verificar el balance de carga por iqr
    
    # Calcular energía (sin enfriamiento como objetivo separado)
    potencias_activas = config.energia['potencias_activas']
    potencias_inactivas = config.energia['potencias_inactivas']
    
    energia_total = 0
    for i in range(1, config.num_maquinas + 1):
        tiempo_activo_hrs = tiempo_uso_maquinas[i] / 60
        tiempo_inactivo_hrs = (tiempo_total - tiempo_uso_maquinas[i]) / 60
        
        energia_activa = potencias_activas[i - 1] * tiempo_activo_hrs
        energia_inactiva = potencias_inactivas[i - 1] * tiempo_inactivo_hrs
        
        energia_total += energia_activa + energia_inactiva
    
    objetivo_energia = 1 / (energia_total + 1)
    
    return objetivo_makespan, objetivo_balance, objetivo_energia