"""Validadores de factibilidad"""
from typing import List


def validate_chromosome_structure(genes: List[List[int]], config) -> tuple[bool, str]:
    """
    Valida que un cromosoma tenga la estructura correcta
    
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    # Verificar número de pedidos
    if len(genes) != config.num_pedidos:
        return False, f"Esperado {config.num_pedidos} pedidos, encontrado {len(genes)}"
    
    # Verificar cada pedido
    for i, pedido in enumerate(genes):
        # Verificar número de etapas
        if len(pedido) != config.num_etapas:
            return False, f"Pedido {i}: esperado {config.num_etapas} etapas, encontrado {len(pedido)}"
        
        # Verificar que cada máquina sea válida para su etapa
        for etapa_idx, maquina in enumerate(pedido):
            maquinas_validas = config.get_maquinas_etapa(etapa_idx + 1)
            if maquina not in maquinas_validas:
                return False, f"Pedido {i}, Etapa {etapa_idx+1}: máquina {maquina} no válida. Válidas: {maquinas_validas}"
    
    return True, "Cromosoma válido"


def validate_population(population: List, config) -> tuple[bool, List[str]]:
    """
    Valida una población completa
    
    Returns:
        tuple: (todos_validos, lista_de_errores)
    """
    errores = []
    
    for i, individuo in enumerate(population):
        es_valido, mensaje = validate_chromosome_structure(individuo.genes, config)
        if not es_valido:
            errores.append(f"Individuo {i}: {mensaje}")
    
    return len(errores) == 0, errores
