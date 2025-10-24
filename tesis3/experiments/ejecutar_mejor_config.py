"""Ejecuta la mejor configuración encontrada - EN STANDBY TEMPORAL - se puede eliminar"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tesis3.src.core.problem import ProblemConfig
from tesis3.src.algorithms.nsga2 import nsga2
from tesis3.src.operators.crossover import aplicar_cruce
from tesis3.src.operators.mutation import aplicar_mutacion
import time

config = ProblemConfig.from_yaml("tesis3/config/config.yaml")

def cruce_wrapper(p1, p2, cfg, prob):
    return aplicar_cruce(p1, p2, cfg, metodo='uniforme', prob_cruce=prob)

def mutacion_wrapper(pob, cfg, prob):
    return aplicar_mutacion(pob, cfg, metodo='invert', tasa_mut=prob)

print("Mejor configuración: Uniforme + Invert")
print("Población: 100, Generaciones: 300")

inicio = time.time()
frente, fitness, _ = nsga2(
    config=config,
    metodo_cruce=cruce_wrapper,
    metodo_mutacion=mutacion_wrapper,
    tamano_poblacion=100,
    num_generaciones=300,
    prob_cruce=0.95,
    prob_mutacion=0.3,
    verbose=True
)
tiempo = time.time() - inicio

metricas = [(1/f[0], 1/f[1]-1, 1/f[2]-1, 1/f[3]-1) for f in fitness]
mejor_mk = min(m[0] for m in metricas)

print(f"\nMejor makespan: {mejor_mk:.2f}s")
print(f"Tiempo: {tiempo:.2f}s")
print(f"Tamaño frente: {len(frente)}")
