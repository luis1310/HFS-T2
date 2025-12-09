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
pytest tesis3/tests/ -v
```

## Uso Básico

```python
from src.core.problem import ProblemConfig
from src.core.chromosome import Chromosome
from src.core.validator import validate_chromosome_structure

# Cargar configuración
config = ProblemConfig.from_yaml()

# Crear cromosoma aleatorio
chromosome = Chromosome.random(config)

# Validar
ok, msg = validate_chromosome_structure(chromosome.genes, config)
assert ok, msg
```

## Tests

```bash
# Ejecutar todos los tests
pytest tesis3/tests/ -v

# Con cobertura
pytest tesis3/tests/ --cov=tesis3/src --cov-report=html

# Solo tests específicos
pytest tesis3/tests/test_chromosome.py -v
```

## Desarrollo

- Formato de código: `black src/`
- Linting: `flake8 src/`

## CI (checks mínimos como gates)

Este repositorio incluye un workflow de GitHub Actions (`.github/workflows/ci.yml`) que aplica las siguientes “puertas” de calidad:

- Lint estricto
  - `flake8` en `tesis3/src/algorithms` y `tesis3/src/operators`
  - `black --check` e `isort --check-only` en `tesis3/src`
- Tests con límite de tiempo
  - `pytest` con `--timeout=30`
- Cobertura mínima
  - Gate global ≥ 75% con `pytest-cov` + `coverage.xml` (config en `.coveragerc`)

Habilitar Actions: en GitHub → Settings → Actions → Allow all actions. Con cada push/PR, el pipeline se ejecuta automáticamente.

## config/config.yaml (explicación)

- `problem.num_pedidos` (int): cantidad de pedidos.
- `problem.num_etapas` (int): número de etapas del proceso.
- `problem.num_maquinas` (int): total de máquinas.
- `problem.tiempos_iniciales` (list[float]): tiempos base por máquina.
- `problem.incrementos` (list[float]): factor de incremento por uso (desgaste) por máquina.
- `problem.maquinas_por_etapa` (dict): máquinas válidas por etapa, e.g. `etapa_1: [1,2,3]`.
- `problem.enfriamiento` (dict): parámetros internos que afectan makespan/energía (no es objetivo).
- `problem.energia` (dict): potencias activas/inactivas y parámetros energéticos.

Ejemplo de acceso en código:
```python
config.get_maquinas_etapa(1)  # -> lista de máquinas válidas para etapa 1
```

## Métrica de balance por etapas/máquina

Se usa la desviación estándar de los tiempos de uso por máquina:
```
σ_D = sqrt( (1/M) * sum_i (D_i - \bar{D})^2 )
```
Donde `D_i` es el tiempo total activo de la máquina `i` y `\bar{D}` el promedio. Esta métrica penaliza la concentración de carga en pocas máquinas y favorece la distribución equitativa.

## Pipeline (alto nivel)

```mermaid
flowchart LR
    A[Cargar config.yaml] --> B[Inicializar población válida]
    B --> C[Evaluar fitness multiobjetivo]
    C --> D[Clasificación no dominada + Crowding]
    D --> E[Selección NSGA-II]
    E --> F[Cruce stage-aware]
    F --> G[Mutación stage-aware]
    G --> H{¿Búsqueda local?}
    H -- sí --> I[Búsqueda local (memético)]
    H -- no --> J[Combinar y seleccionar]
    I --> J
    J --> K{¿Generaciones restantes?}
    K -- sí --> C
    K -- no --> L[Frente de Pareto final]
```
