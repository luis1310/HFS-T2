
"""Utilidades para manejo de población"""
from tesis3.src.core.chromosome import Chromosome


def inicializar_poblacion(config, tamano):
    """
    Genera población inicial aleatoria
    
    Args:
        config: ProblemConfig
        tamano: Número de individuos
    
    Returns:
        Lista de Chromosome
    """
    poblacion = []
    individuos_unicos = set()
    
    while len(poblacion) < tamano:
        ind = Chromosome.random(config)
        ind_tuple = tuple(tuple(pedido) for pedido in ind.genes)
        
        if ind_tuple not in individuos_unicos:
            poblacion.append(ind)
            individuos_unicos.add(ind_tuple)
    
    return poblacion
