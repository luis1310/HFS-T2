
"""Operadores de mutación stage-aware"""
import random


def mutacion_swap_stage_aware(poblacion, config, tasa_mut=0.3):
    """
    Intercambia máquinas entre 2 pedidos en la misma etapa
    """
    mutados = []
    for individuo in poblacion:
        if random.random() < tasa_mut:
            ind_copy = individuo.copy()
            etapa = random.randint(0, config.num_etapas - 1)
            
            if len(ind_copy.genes) >= 2:
                ped1, ped2 = random.sample(range(len(ind_copy.genes)), 2)
                ind_copy.genes[ped1][etapa], ind_copy.genes[ped2][etapa] = \
                    ind_copy.genes[ped2][etapa], ind_copy.genes[ped1][etapa]
            
            mutados.append(ind_copy)
        else:
            mutados.append(individuo)
    
    return mutados


def mutacion_insert_stage_aware(poblacion, config, tasa_mut=0.3):
    """
    Cambia la máquina de un pedido en una etapa específica
    """
    mutados = []
    for individuo in poblacion:
        if random.random() < tasa_mut:
            ind_copy = individuo.copy()
            pedido_idx = random.randint(0, len(ind_copy.genes) - 1)
            etapa = random.randint(0, config.num_etapas - 1)
            
            maquina_actual = ind_copy.genes[pedido_idx][etapa]
            opciones = [m for m in config.get_maquinas_etapa(etapa + 1) 
                       if m != maquina_actual]
            
            if opciones:
                ind_copy.genes[pedido_idx][etapa] = random.choice(opciones)
            
            mutados.append(ind_copy)
        else:
            mutados.append(individuo)
    
    return mutados


def mutacion_invert_stage_aware(poblacion, config, tasa_mut=0.3):
    """
    Invierte asignaciones de máquinas en un rango de etapas
    """
    mutados = []
    for individuo in poblacion:
        if random.random() < tasa_mut:
            ind_copy = individuo.copy()
            pedido_idx = random.randint(0, len(ind_copy.genes) - 1)
            
            if config.num_etapas >= 2:
                etapa1, etapa2 = sorted(random.sample(range(config.num_etapas), 2))
                ind_copy.genes[pedido_idx][etapa1:etapa2+1] = \
                    ind_copy.genes[pedido_idx][etapa1:etapa2+1][::-1]
            
            mutados.append(ind_copy)
        else:
            mutados.append(individuo)
    
    return mutados


# Wrapper para compatibilidad
def aplicar_mutacion(poblacion, config, metodo='swap', tasa_mut=0.3):
    """
    Aplica el método de mutación especificado
    
    Args:
        poblacion: Lista de Chromosome
        config: ProblemConfig
        metodo: 'swap', 'insert', o 'invert'
        tasa_mut: Probabilidad de mutación
    
    Returns:
        Lista de Chromosome mutados
    """
    if metodo == 'swap':
        return mutacion_swap_stage_aware(poblacion, config, tasa_mut)
    elif metodo == 'insert':
        return mutacion_insert_stage_aware(poblacion, config, tasa_mut)
    elif metodo == 'invert':
        return mutacion_invert_stage_aware(poblacion, config, tasa_mut)
    else:
        raise ValueError(f"Método de mutación desconocido: {metodo}")
