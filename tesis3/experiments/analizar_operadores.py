
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tesis3.src.core.problem import ProblemConfig
from tesis3.src.core.chromosome import Chromosome
from tesis3.src.operators.mutation import mutacion_swap_stage_aware
from tesis3.src.fitness.multi_objective import fitness_multiobjetivo

config = ProblemConfig.from_yaml("tesis3/config/config.yaml")

original = Chromosome.random(config)
f_original = fitness_multiobjetivo(original, config)

print("Cromosoma original:")
print(f"Makespan: {1/f_original[0]:.2f}")

print("\n10 mutaciones del mismo individuo:")
for i in range(10):
    mutado = mutacion_swap_stage_aware([original.copy()], config, 1.0)[0]
    f_mutado = fitness_multiobjetivo(mutado, config)
    mk_mutado = 1/f_mutado[0]
    diferencia = mk_mutado - (1/f_original[0])
    print(f"{i+1}: Makespan={mk_mutado:.2f} (diff: {diferencia:+.2f})")
