
"""Tests para la clase Chromosome"""
import pytest
from tesis3.src.core.chromosome import Chromosome
from tesis3.src.core.problem import ProblemConfig


@pytest.fixture
def config():
    """Fixture para configuración del problema"""
    return ProblemConfig.from_yaml("tesis3/config/config.yaml")


def test_random_chromosome_is_valid(config):
    """Verifica que cromosomas aleatorios sean válidos"""
    chromosome = Chromosome.random(config)
    assert chromosome.is_valid()


def test_chromosome_structure(config):
    """Verifica estructura correcta del cromosoma"""
    chromosome = Chromosome.random(config)
    assert len(chromosome.genes) == config.num_pedidos
    assert all(len(pedido) == config.num_etapas for pedido in chromosome.genes)


def test_chromosome_machines_in_correct_stages(config):
    """Verifica que las máquinas estén en etapas correctas"""
    chromosome = Chromosome.random(config)
    
    for pedido in chromosome.genes:
        for etapa_idx, maquina in enumerate(pedido):
            maquinas_validas = config.get_maquinas_etapa(etapa_idx + 1)
            assert maquina in maquinas_validas


def test_invalid_chromosome_detected(config):
    """Verifica que se detecten cromosomas inválidos"""
    invalid_genes = [[99, 4, 6, 10, 11]] * config.num_pedidos
    chromosome = Chromosome(invalid_genes, config)
    assert not chromosome.is_valid()


def test_chromosome_copy(config):
    """Verifica que la copia sea independiente"""
    original = Chromosome.random(config)
    copia = original.copy()
    
    copia.genes[0][0] = 999
    assert original.genes[0][0] != 999
