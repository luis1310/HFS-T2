import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # añade raíz de 'tesis3'

from tesis3.src.core.problem import ProblemConfig
from tesis3.src.core.chromosome import Chromosome
from tesis3.src.core.validator import validate_chromosome_structure, validate_population
from tesis3.src.operators.crossover import aplicar_cruce
from tesis3.src.operators.mutation import aplicar_mutacion


def _cargar_config():
    # Usa el config real del proyecto
    return ProblemConfig.from_yaml("tesis3/config/config.yaml")


def _generar_padres_validos(config):
    padre1 = Chromosome.random(config)
    padre2 = Chromosome.random(config)
    assert padre1.is_valid() and padre2.is_valid()
    return padre1, padre2


def test_cruce_mantiene_factibilidad_uniforme():
    config = _cargar_config()
    padre1, padre2 = _generar_padres_validos(config)
    hijo1, hijo2 = aplicar_cruce(padre1, padre2, config, metodo='uniforme', prob_cruce=1.0)

    ok1, msg1 = validate_chromosome_structure(hijo1.genes, config)
    ok2, msg2 = validate_chromosome_structure(hijo2.genes, config)
    assert ok1, f"El hijo1 no es válido: {msg1}"
    assert ok2, f"El hijo2 no es válido: {msg2}"


def test_cruce_mantiene_factibilidad_un_punto():
    config = _cargar_config()
    padre1, padre2 = _generar_padres_validos(config)
    hijo1, hijo2 = aplicar_cruce(padre1, padre2, config, metodo='un_punto', prob_cruce=1.0)

    ok1, msg1 = validate_chromosome_structure(hijo1.genes, config)
    ok2, msg2 = validate_chromosome_structure(hijo2.genes, config)
    assert ok1, f"El hijo1 no es válido: {msg1}"
    assert ok2, f"El hijo2 no es válido: {msg2}"


def test_mutaciones_mantienen_factibilidad_swap_insert_invert():
    config = _cargar_config()
    padre, _ = _generar_padres_validos(config)
    poblacion = [padre]

    # swap
    mutados_swap = aplicar_mutacion(poblacion, config, metodo='swap', tasa_mut=1.0)
    ok, errores = validate_population(mutados_swap, config)
    assert ok, f"Mutación swap generó individuos inválidos: {errores}"

    # insert
    mutados_insert = aplicar_mutacion(poblacion, config, metodo='insert', tasa_mut=1.0)
    ok, errores = validate_population(mutados_insert, config)
    assert ok, f"Mutación insert generó individuos inválidos: {errores}"

    # invert
    mutados_invert = aplicar_mutacion(poblacion, config, metodo='invert', tasa_mut=1.0)
    ok, errores = validate_population(mutados_invert, config)
    assert ok, f"Mutación invert generó individuos inválidos: {errores}"


def test_invariantes_estructura_y_maquinas_validas():
    config = _cargar_config()
    crom = Chromosome.random(config)

    # Estructura base
    assert len(crom.genes) == config.num_pedidos
    for pedido in crom.genes:
        assert len(pedido) == config.num_etapas

    # Máquinas válidas por etapa
    for etapa_idx in range(config.num_etapas):
        validas = set(config.get_maquinas_etapa(etapa_idx + 1))
        for pedido in crom.genes:
            assert pedido[etapa_idx] in validas

