"""Configuración del problema HFS"""
import yaml
import os
from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path


@dataclass
class ProblemConfig:
    """Configuración del problema de scheduling"""
    num_pedidos: int
    num_maquinas: int
    num_etapas: int
    tiempos_iniciales: List[float]
    incrementos: List[float]
    maquinas_por_etapa: Dict[str, List[int]]
    enfriamiento: Dict[str, float]
    energia: Dict[str, any]
    
    @classmethod
    def from_yaml(cls, path: str = "config/config.yaml"):
        """Carga configuración desde archivo YAML"""
        # Si la ruta es relativa, buscar desde la raíz del proyecto
        if not os.path.isabs(path):
            # Encontrar la raíz del proyecto (donde está HFS-T2/)
            current_dir = Path(__file__).resolve().parent
            # Subir hasta encontrar tesis3/
            while current_dir.name != "tesis3" and current_dir.parent != current_dir:
                current_dir = current_dir.parent
            
            # Si ya incluye "tesis3/" en la ruta, usar directamente desde raíz del proyecto
            if path.startswith("tesis3/"):
                config_path = current_dir.parent / path
            else:
                # Si no, asumir que es relativo a tesis3/
                config_path = current_dir / path
        else:
            config_path = Path(path)
        
        with open(config_path) as f:
            config = yaml.safe_load(f)
        return cls(**config['problem'])
    
    def get_maquinas_etapa(self, etapa: int) -> List[int]:
        """Obtiene máquinas disponibles para una etapa (1-indexed)"""
        return self.maquinas_por_etapa[f'etapa_{etapa}']