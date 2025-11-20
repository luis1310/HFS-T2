"""Compara NSGA-II estándar vs memético"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tesis3.src.core.problem import ProblemConfig
from tesis3.src.algorithms.nsga2 import nsga2
from tesis3.src.algorithms.nsga2_memetic import nsga2_memetic
from tesis3.src.operators.crossover import aplicar_cruce
from tesis3.src.operators.mutation import aplicar_mutacion
import time
import numpy as np
import random
import os

config = ProblemConfig.from_yaml("tesis3/config/config.yaml")

def cruce(p1, p2, cfg, prob):
    return aplicar_cruce(p1, p2, cfg, metodo='uniforme', prob_cruce=prob)

def mutacion(pob, cfg, prob):
    return aplicar_mutacion(pob, cfg, metodo='invert', tasa_mut=prob)

print("="*60)
print("COMPARACIÓN: NSGA-II vs NSGA-II Memético")
print("="*60)
print("5 semillas por versión (50 ind, 100 gen)")
print("="*60)

resultados = {'estandar': [], 'memetico': []}

# 5 semillas para cada versión
for semilla in range(5):
    random.seed(semilla)
    np.random.seed(semilla)
    
    print(f"\n{'='*60}")
    print(f"Semilla {semilla+1}/5")
    print(f"{'='*60}")
    
    # NSGA-II estándar
    print("  Ejecutando NSGA-II estándar...")
    inicio = time.time()
    frente_std, fitness_std, _ = nsga2(
        config, cruce, mutacion,
        tamano_poblacion=50,
        num_generaciones=100,
        prob_cruce=0.95,
        prob_mutacion=0.3,
        verbose=False
    )
    tiempo_std = time.time() - inicio
    
    metricas_std = [(1/f[0], 1/f[1]-1, 1/f[2]-1, 1/f[3]-1) for f in fitness_std]
    mejor_mk_std = min(m[0] for m in metricas_std)
    
    resultados['estandar'].append({
        'semilla': semilla,
        'makespan': mejor_mk_std,
        'frente': len(frente_std),
        'tiempo': tiempo_std
    })
    
    print(f"    Makespan: {mejor_mk_std:.2f}s | Frente: {len(frente_std)} | Tiempo: {tiempo_std:.2f}s")
    
    # NSGA-II memético
    print("  Ejecutando NSGA-II memético...")
    inicio = time.time()
    frente_mem, fitness_mem, _ = nsga2_memetic(
        config, cruce, mutacion,
        tamano_poblacion=50,
        num_generaciones=100,
        prob_cruce=0.95,
        prob_mutacion=0.3,
        cada_k_gen=10,
        max_iter_local=5,
        verbose=False
    )
    tiempo_mem = time.time() - inicio
    
    metricas_mem = [(1/f[0], 1/f[1]-1, 1/f[2]-1, 1/f[3]-1) for f in fitness_mem]
    mejor_mk_mem = min(m[0] for m in metricas_mem)
    
    resultados['memetico'].append({
        'semilla': semilla,
        'makespan': mejor_mk_mem,
        'frente': len(frente_mem),
        'tiempo': tiempo_mem
    })
    
    print(f"    Makespan: {mejor_mk_mem:.2f}s | Frente: {len(frente_mem)} | Tiempo: {tiempo_mem:.2f}s")
    
    mejora_semilla = ((mejor_mk_std - mejor_mk_mem) / mejor_mk_std) * 100
    print(f"    Mejora: {mejora_semilla:+.2f}%")

# Análisis final
print("\n" + "="*60)
print("RESULTADOS COMPARATIVOS (5 semillas)")
print("="*60)

mk_std = [r['makespan'] for r in resultados['estandar']]
mk_mem = [r['makespan'] for r in resultados['memetico']]
t_std = [r['tiempo'] for r in resultados['estandar']]
t_mem = [r['tiempo'] for r in resultados['memetico']]

print(f"\nNSGA-II Estándar:")
print(f"   Makespan promedio: {np.mean(mk_std):.2f}s ± {np.std(mk_std):.2f}")
print(f"   Mejor caso:        {np.min(mk_std):.2f}s")
print(f"   Peor caso:         {np.max(mk_std):.2f}s")
print(f"   Tiempo promedio:   {np.mean(t_std):.2f}s")

print(f"\nNSGA-II Memético:")
print(f"   Makespan promedio: {np.mean(mk_mem):.2f}s ± {np.std(mk_mem):.2f}")
print(f"   Mejor caso:        {np.min(mk_mem):.2f}s")
print(f"   Peor caso:         {np.max(mk_mem):.2f}s")
print(f"   Tiempo promedio:   {np.mean(t_mem):.2f}s")

mejora = ((np.mean(mk_std) - np.mean(mk_mem)) / np.mean(mk_std)) * 100
overhead = ((np.mean(t_mem) - np.mean(t_std)) / np.mean(t_std)) * 100

print(f"\nCONCLUSIONES:")
print(f"   Mejora promedio en makespan: {mejora:+.2f}%")
print(f"   Overhead computacional:      {overhead:+.2f}%")

if mejora > 0:
    print(f"\nLa búsqueda local MEJORA los resultados")
else:
    print(f"\nLa búsqueda local NO mejora significativamente")

print("\n" + "="*60)

# Asegurar que el directorio existe
os.makedirs('tesis3/results', exist_ok=True)

# Guardar resultados
import csv
with open('tesis3/results/comparacion_memetica.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['version', 'semilla', 'makespan', 'frente', 'tiempo'])
    writer.writeheader()
    
    for r in resultados['estandar']:
        writer.writerow({'version': 'estandar', **r})
    
    for r in resultados['memetico']:
        writer.writerow({'version': 'memetico', **r})

print("Resultados guardados: tesis3/results/comparacion_memetica.csv")
