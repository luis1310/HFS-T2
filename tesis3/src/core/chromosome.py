"""Representación del cromosoma"""
import random
from typing import List
from copy import deepcopy


class Chromosome:
    """Representa una solución al problema HFS"""
    
    def __init__(self, genes: List[List[int]], config):
        self.genes = genes
        self.config = config
        self._fitness = None
        self._objectives = None
    
    @classmethod
    def random(cls, config):
        """Genera cromosoma aleatorio válido"""
        genes = []
        for _ in range(config.num_pedidos):
            pedido = [
                random.choice(config.get_maquinas_etapa(i+1))
                for i in range(config.num_etapas)
            ]
            genes.append(pedido)
        return cls(genes, config)
    
    def is_valid(self) -> bool:
        """Verifica si el cromosoma es factible"""
        if len(self.genes) != self.config.num_pedidos:
            return False
        
        for pedido in self.genes:
            if len(pedido) != self.config.num_etapas:
                return False
            
            for etapa_idx, maquina in enumerate(pedido):
                maquinas_validas = self.config.get_maquinas_etapa(etapa_idx + 1)
                if maquina not in maquinas_validas:
                    return False
        
        return True
    
    def copy(self):
        """Crea una copia profunda del cromosoma"""
        return Chromosome(deepcopy(self.genes), self.config)
    
    def __repr__(self):
        return f"Chromosome({len(self.genes)} pedidos, valid={self.is_valid()})"
