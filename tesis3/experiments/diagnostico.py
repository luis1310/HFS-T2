"""Diagnóstico de la población inicial - EN STANDBY TEMPORAL - se puede eliminar"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tesis3.src.core.problem import ProblemConfig
from tesis3.src.utils.population import inicializar_poblacion
from tesis3.src.fitness.multi_objective import fitness_multiobjetivo

config = ProblemConfig.from_yaml("tesis3/config/config.yaml")
poblacion = inicializar_poblacion(config, 10)

fitness_vals = [fitness_multiobjetivo(ind, config) for ind in poblacion]

print("Fitness de 10 individuos aleatorios:")
for i, f in enumerate(fitness_vals):
    mk = 1/f[0]
    bal = 1/f[1] - 1
    enf = 1/f[2] - 1
    eng = 1/f[3] - 1
    print(f"{i}: Makespan={mk:.2f}, Balance={bal:.2f}, Enfr={enf:.2f}, Energía={eng:.2f}")

print(f"\nMakespans únicos: {len(set(round(1/f[0], 2) for f in fitness_vals))}")
print(f"Todos los fitness únicos: {len(set(fitness_vals)) == len(fitness_vals)}")
