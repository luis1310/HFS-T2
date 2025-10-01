# Tesis 3: Optimización Multiobjetivo con NSGA-II

Evolución del proyecto de Tesis 2 hacia un enfoque multiobjetivo con operadores avanzados.

## Estructura del Proyecto

```
tesis3/
├── config/          # Archivos de configuración
├── src/             # Código fuente
│   ├── core/        # Clases fundamentales
│   ├── fitness/     # Funciones de evaluación
│   ├── algorithms/  # NSGA-II y variantes
│   ├── operators/   # Cruces y mutaciones
│   └── utils/       # Utilidades
├── experiments/     # Scripts de experimentación
├── tests/           # Tests unitarios
└── docs/            # Documentación

```

## Setup

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r ../requirements.txt

# Ejecutar tests
pytest tests/ -v
```

## Uso Básico

```python
from src.core.problem import ProblemConfig
from src.core.chromosome import Chromosome

# Cargar configuración
config = ProblemConfig.from_yaml()

# Crear cromosoma aleatorio
chromosome = Chromosome.random(config)

# Validar
assert chromosome.is_valid()
```

## Tests

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=src --cov-report=html

# Solo tests específicos
pytest tests/test_chromosome.py -v
```

## Desarrollo

- Formato de código: `black src/`
- Linting: `flake8 src/`
