
"""Tests para configuración del problema"""
import pytest
from tesis3.src.core.problem import ProblemConfig


def test_load_config_from_yaml():
    """Verifica que se cargue correctamente el config.yaml"""
    config = ProblemConfig.from_yaml("tesis3/config/config.yaml")
    
    assert config.num_pedidos == 40
    assert config.num_maquinas == 11
    assert config.num_etapas == 5


def test_get_maquinas_etapa():
    """Verifica obtención de máquinas por etapa"""
    config = ProblemConfig.from_yaml("tesis3/config/config.yaml")
    
    assert config.get_maquinas_etapa(1) == [1, 2, 3]
    assert config.get_maquinas_etapa(2) == [4, 5]
    assert config.get_maquinas_etapa(5) == [11]


def test_all_machines_covered():
    """Verifica que todas las máquinas estén asignadas"""
    config = ProblemConfig.from_yaml("tesis3/config/config.yaml")
    
    all_machines = set()
    for i in range(1, config.num_etapas + 1):
        all_machines.update(config.get_maquinas_etapa(i))
    
    expected_machines = set(range(1, config.num_maquinas + 1))
    assert all_machines == expected_machines
