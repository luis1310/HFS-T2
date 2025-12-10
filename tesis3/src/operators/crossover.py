
"""Operadores de cruce stage-aware"""
import random
from tesis3.src.core.chromosome import Chromosome


def cruce_uniforme_por_etapa(padre1, padre2, config, prob_cruce=0.95):
    """
    Cruce uniforme: cada etapa se hereda aleatoriamente
    
    Args:
        padre1, padre2: Instancias de Chromosome
        config: ProblemConfig
        prob_cruce: Probabilidad de realizar cruce
    
    Returns:
        tuple: (hijo1, hijo2) como Chromosome
    """
    if random.random() > prob_cruce:
        return padre1.copy(), padre2.copy()
    
    genes_hijo1 = []
    genes_hijo2 = []
    
    for i in range(config.num_pedidos):
        pedido_hijo1 = []
        pedido_hijo2 = []
        
        for etapa in range(config.num_etapas):
            if random.random() < 0.5:
                pedido_hijo1.append(padre1.genes[i][etapa])
                pedido_hijo2.append(padre2.genes[i][etapa])
            else:
                pedido_hijo1.append(padre2.genes[i][etapa])
                pedido_hijo2.append(padre1.genes[i][etapa])
        
        genes_hijo1.append(pedido_hijo1)
        genes_hijo2.append(pedido_hijo2)
    
    hijo1 = Chromosome(genes_hijo1, config)
    hijo2 = Chromosome(genes_hijo2, config)
    
    return hijo1, hijo2


def cruce_un_punto(padre1, padre2, config, prob_cruce=0.95):
    """
    Cruce de un punto entre pedidos
    """
    if random.random() > prob_cruce:
        return padre1.copy(), padre2.copy()
    
    punto = random.randint(1, config.num_pedidos - 1)
    
    genes_hijo1 = padre1.genes[:punto] + padre2.genes[punto:]
    genes_hijo2 = padre2.genes[:punto] + padre1.genes[punto:]
    
    hijo1 = Chromosome(genes_hijo1, config)
    hijo2 = Chromosome(genes_hijo2, config)
    
    return hijo1, hijo2


# Wrapper
def aplicar_cruce(padre1, padre2, config, metodo='uniforme', prob_cruce=0.95):
    """
    Aplica el método de cruce especificado
    
    Args:
        padre1, padre2: Chromosome
        config: ProblemConfig
        metodo: 'uniforme' o 'un_punto'
        prob_cruce: Probabilidad de cruce
    
    Returns:
        tuple: (hijo1, hijo2)
    """
    if metodo == 'uniforme':
        return cruce_uniforme_por_etapa(padre1, padre2, config, prob_cruce)
    elif metodo == 'un_punto':
        return cruce_un_punto(padre1, padre2, config, prob_cruce)
    else:
        raise ValueError(f"Método de cruce desconocido: {metodo}")
