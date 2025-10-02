

"""Análisis riguroso con 30 semillas de la mejor configuración"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tesis3.src.core.problem import ProblemConfig
from tesis3.src.algorithms.nsga2 import nsga2
from tesis3.src.operators.crossover import aplicar_cruce
from tesis3.src.operators.mutation import aplicar_mutacion
import random
import numpy as np

config = ProblemConfig.from_yaml("tesis3/config/config.yaml")

resultados = []

print("Ejecutando 30 réplicas de Uniforme + Invert...")

for semilla in range(30):
    random.seed(semilla)
    
    def cruce(p1, p2, cfg, prob):
        return aplicar_cruce(p1, p2, cfg, metodo='uniforme', prob_cruce=prob)
    
    def mutacion(pob, cfg, prob):
        return aplicar_mutacion(pob, cfg, metodo='invert', tasa_mut=prob)
    
    frente, fitness, _ = nsga2(
        config=config,
        metodo_cruce=cruce,
        metodo_mutacion=mutacion,
        tamano_poblacion=100,
        num_generaciones=300,
        prob_cruce=0.95,
        prob_mutacion=0.3,
        verbose=False
    )
    
    metricas = [(1/f[0], 1/f[1]-1, 1/f[2]-1, 1/f[3]-1) for f in fitness]
    mejor_mk = min(m[0] for m in metricas)
    
    resultados.append({
        'semilla': semilla,
        'makespan': mejor_mk,
        'frente': len(frente)
    })
    
    if (semilla + 1) % 5 == 0:
        print(f"  Completadas {semilla + 1}/30 réplicas")

makespans = [r['makespan'] for r in resultados]

print("\n" + "="*60)
print("RESULTADOS FINALES (30 semillas)")
print("="*60)
print(f"Makespan promedio: {np.mean(makespans):.2f}s")
print(f"Desviación estándar: {np.std(makespans):.2f}s")
print(f"Mejor caso: {np.min(makespans):.2f}s")
print(f"Peor caso: {np.max(makespans):.2f}s")
print(f"Mediana: {np.median(makespans):.2f}s")

print("\nComparación con Tesis 2:")
tesis2_makespan = 1556.04
mejora = ((tesis2_makespan - np.mean(makespans)) / tesis2_makespan) * 100
print(f"Tesis 2: {tesis2_makespan:.2f}s")
print(f"Tesis 3: {np.mean(makespans):.2f}s")
print(f"Mejora: {mejora:.1f}%")
