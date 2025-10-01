#!/bin/bash

# Script para crear estructura completa del proyecto Tesis 3
# Ejecutar desde la carpeta raíz del proyecto (HFS-T2/)

echo "=========================================="
echo "Creando estructura del proyecto Tesis 3"
echo "=========================================="

# Verificar que estemos en la carpeta correcta
if [ ! -d "tesis3" ]; then
    echo "Error: La carpeta tesis3 no existe. Créala primero con: mkdir tesis3"
    exit 1
fi

cd tesis3

# Crear estructura de carpetas
echo "Creando estructura de carpetas..."
mkdir -p config
mkdir -p src/{core,fitness,algorithms,operators,utils}
mkdir -p experiments
mkdir -p tests
mkdir -p docs/{notebooks,latex}

# Crear archivos __init__.py para hacer los módulos importables
echo "Creando archivos __init__.py..."
touch src/__init__.py
touch src/core/__init__.py
touch src/fitness/__init__.py
touch src/algorithms/__init__.py
touch src/operators/__init__.py
touch src/utils/__init__.py

# Crear archivo de configuración YAML
echo "Creando config.yaml..."
cat > config/config.yaml << 'EOF'
# Configuración del problema HFS
problem:
  num_pedidos: 40
  num_maquinas: 11
  num_etapas: 5
  
  tiempos_iniciales: [55, 53, 56, 42, 41, 30, 34, 35, 28, 26, 20]
  
  incrementos: [0.0235, 0.0376, 0.0298, 0.0265, 0.0343, 
                0.0201, 0.0235, 0.0358, 0.0269, 0.0385, 0.0269]
  
  maquinas_por_etapa:
    etapa_1: [1, 2, 3]
    etapa_2: [4, 5]
    etapa_3: [6, 7, 8]
    etapa_4: [9, 10]
    etapa_5: [11]
  
  enfriamiento:
    limite: 1.30
    factor: 0.85
    tiempo: 6
  
  energia:
    potencias_activas: [5.5, 5.3, 5.6, 4.2, 4.1, 3.0, 3.4, 3.5, 2.8, 2.6, 2.0]
    potencias_inactivas: [0.5, 0.5, 0.5, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3, 0.3, 0.2]
    energia_por_enfriamiento: 2.0

# Configuración de algoritmos
algorithm:
  nsga2:
    tamano_poblacion: 100
    num_generaciones: 500
    prob_cruce: 0.95
    prob_mutacion: 0.3
  
  memetic:
    activado: false
    cada_k_generaciones: 10
    max_iteraciones_local: 5

# Configuración de experimentos
experiments:
  num_semillas: 30
  output_dir: "results/tesis3"
  save_plots: true
  save_csv: true
EOF

# Crear requirements.txt
echo "Creando requirements.txt..."
cd ..
cat > requirements.txt << 'EOF'
# Dependencias básicas
numpy>=1.24.0
matplotlib>=3.7.0
pandas>=2.0.0
seaborn>=0.12.0

# Configuración y utilidades
pyyaml>=6.0
tqdm>=4.65.0

# Testing y calidad de código
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.0.0

# Opcional: aceleración
# numba>=0.57.0
EOF

# Crear .gitignore
echo "Creando .gitignore..."
cat > .gitignore << 'EOF'
# Python
venv/
env/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.pytest_cache/

# Resultados y outputs
results/
*.png
*.csv
*.pdf
*.log

# IDEs
.vscode/
.idea/
*.swp
*.swo

# macOS
.DS_Store

# Jupyter
.ipynb_checkpoints/

# Configuración local
config.local.yaml
tesis3/config/config.local.yaml

# Datos grandes
*.zip
*.tar.gz
EOF

# Crear estructura básica de archivos Python
echo "Creando archivos base de Python..."

# src/core/problem.py
cat > tesis3/src/core/problem.py << 'EOF'
"""Configuración del problema HFS"""
import yaml
from dataclasses import dataclass, field
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
        config_path = Path(__file__).parent.parent.parent / path
        with open(config_path) as f:
            config = yaml.safe_load(f)
        return cls(**config['problem'])
    
    def get_maquinas_etapa(self, etapa: int) -> List[int]:
        """Obtiene máquinas disponibles para una etapa (1-indexed)"""
        return self.maquinas_por_etapa[f'etapa_{etapa}']
EOF

# src/core/chromosome.py
cat > tesis3/src/core/chromosome.py << 'EOF'
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
EOF

# src/core/validator.py
cat > tesis3/src/core/validator.py << 'EOF'
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
EOF

# tests/test_chromosome.py
cat > tesis3/tests/test_chromosome.py << 'EOF'
"""Tests para la clase Chromosome"""
import pytest
from src.core.chromosome import Chromosome
from src.core.problem import ProblemConfig


@pytest.fixture
def config():
    """Fixture para configuración del problema"""
    return ProblemConfig.from_yaml("config/config.yaml")


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
    # Cromosoma con máquina inválida
    invalid_genes = [[99, 4, 6, 10, 11]] * config.num_pedidos
    chromosome = Chromosome(invalid_genes, config)
    assert not chromosome.is_valid()


def test_chromosome_copy(config):
    """Verifica que la copia sea independiente"""
    original = Chromosome.random(config)
    copia = original.copy()
    
    # Modificar copia
    copia.genes[0][0] = 999
    
    # Original no debe cambiar
    assert original.genes[0][0] != 999
EOF

# tests/test_problem.py
cat > tesis3/tests/test_problem.py << 'EOF'
"""Tests para configuración del problema"""
import pytest
from src.core.problem import ProblemConfig


def test_load_config_from_yaml():
    """Verifica que se cargue correctamente el config.yaml"""
    config = ProblemConfig.from_yaml("config/config.yaml")
    
    assert config.num_pedidos == 40
    assert config.num_maquinas == 11
    assert config.num_etapas == 5


def test_get_maquinas_etapa():
    """Verifica obtención de máquinas por etapa"""
    config = ProblemConfig.from_yaml("config/config.yaml")
    
    assert config.get_maquinas_etapa(1) == [1, 2, 3]
    assert config.get_maquinas_etapa(2) == [4, 5]
    assert config.get_maquinas_etapa(5) == [11]


def test_all_machines_covered():
    """Verifica que todas las máquinas estén asignadas"""
    config = ProblemConfig.from_yaml("config/config.yaml")
    
    all_machines = set()
    for i in range(1, config.num_etapas + 1):
        all_machines.update(config.get_maquinas_etapa(i))
    
    expected_machines = set(range(1, config.num_maquinas + 1))
    assert all_machines == expected_machines
EOF

# README.md
cat > tesis3/README.md << 'EOF'
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
EOF

# Volver a la raíz y crear GitHub Actions
cd ..
mkdir -p .github/workflows

cat > .github/workflows/tests.yml << 'EOF'
name: Tests Tesis 3

on:
  push:
    branches: [ tesis3-dev, main ]
    paths:
      - 'tesis3/**'
      - 'requirements.txt'
  pull_request:
    branches: [ tesis3-dev, main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd tesis3
        pytest tests/ -v --cov=src --cov-report=term
    
    - name: Check code format
      run: |
        black --check tesis3/src/
EOF

echo ""
echo "=========================================="
echo "✅ Estructura creada exitosamente"
echo "=========================================="
echo ""
echo "Próximos pasos:"
echo "1. cd .. (volver a raíz del proyecto)"
echo "2. python3 -m venv venv"
echo "3. source venv/bin/activate"
echo "4. pip install -r requirements.txt"
echo "5. cd tesis3 && pytest tests/ -v"
echo ""
echo "Archivos creados:"
echo "- tesis3/config/config.yaml"
echo "- tesis3/src/core/{problem.py, chromosome.py, validator.py}"
echo "- tesis3/tests/{test_chromosome.py, test_problem.py}"
echo "- requirements.txt"
echo "- .gitignore"
echo "- .github/workflows/tests.yml"
echo ""
