"""Genera visualizaciones del frente de Pareto con algoritmo memético"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tesis3.src.core.problem import ProblemConfig
from tesis3.src.algorithms.nsga2_memetic import nsga2_memetic
from tesis3.src.operators.crossover import aplicar_cruce
from tesis3.src.operators.mutation import aplicar_mutacion
from tesis3.src.fitness.multi_objective import fitness_multiobjetivo
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import yaml
import os

print("="*60)
print("VISUALIZACIÓN DEL FRENTE DE PARETO (ALGORITMO MEMÉTICO)")
print("="*60)

# Cargar configuración completa
config = ProblemConfig.from_yaml("tesis3/config/config.yaml")

# Leer parámetros del algoritmo desde YAML
with open("tesis3/config/config.yaml") as f:
    full_config = yaml.safe_load(f)

alg_params = full_config['algorithm']['nsga2']
memetic_params = full_config['algorithm']['memetic']

print(f"\nParámetros del algoritmo (desde config.yaml):")
print(f"   Población: {alg_params['tamano_poblacion']}")
print(f"   Generaciones: {alg_params['num_generaciones']}")
print(f"   Prob. cruce: {alg_params['prob_cruce']}")
print(f"   Prob. mutación: {alg_params['prob_mutacion']}")
print(f"   Memético: {memetic_params['activado']}")
print(f"   Búsqueda local cada: {memetic_params['cada_k_generaciones']} gen")
print(f"   Iteraciones locales: {memetic_params['max_iteraciones_local']}")

def cruce(p1, p2, cfg, prob):
    return aplicar_cruce(p1, p2, cfg, metodo='uniforme', prob_cruce=prob)

def mutacion(pob, cfg, prob):
    return aplicar_mutacion(pob, cfg, metodo='invert', tasa_mut=prob)

print("\nEjecutando NSGA-II Memético (Uniforme + Invert)...")
print(f"   Esto tomará ~{alg_params['num_generaciones'] * 0.05:.0f} segundos\n")

frente_pareto, fitness_pareto, historial = nsga2_memetic(
    config, cruce, mutacion,
    tamano_poblacion=alg_params['tamano_poblacion'],
    num_generaciones=alg_params['num_generaciones'],
    prob_cruce=alg_params['prob_cruce'],
    prob_mutacion=alg_params['prob_mutacion'],
    cada_k_gen=memetic_params['cada_k_generaciones'],
    max_iter_local=memetic_params['max_iteraciones_local'],
    verbose=True
)

print(f"\nFrente de Pareto obtenido: {len(frente_pareto)} soluciones")

# Convertir fitness a métricas reales
metricas = []
for obj_mk, obj_bal, obj_eng in fitness_pareto:
    makespan = 1 / obj_mk
    balance = 1 / obj_bal - 1
    energia = 1 / obj_eng - 1
    metricas.append((makespan, balance, energia))

makespans = [m[0] for m in metricas]
balances = [m[1] for m in metricas]
energias = [m[2] for m in metricas]

print("\nEstadísticas del frente:")
print(f"   Makespan:     {min(makespans):.2f} - {max(makespans):.2f}s")
print(f"   Balance:      {min(balances):.2f} - {max(balances):.2f}")
print(f"   Energía:      {min(energias):.2f} - {max(energias):.2f} kWh")

# Calcular rangos
rango_mk = max(makespans) - min(makespans)
rango_bal = max(balances) - min(balances)
rango_eng = max(energias) - min(energias)

print(f"\nRangos del frente:")
print(f"   Makespan:     {rango_mk:.2f}s")
print(f"   Balance:      {rango_bal:.2f}")
print(f"   Energía:      {rango_eng:.2f} kWh")

# ============================================================
# GRÁFICO 1: 3D (3 dimensiones)
# ============================================================
print("\nGenerando visualizaciones...")

# Asegurar que el directorio existe
os.makedirs('tesis3/results', exist_ok=True)

fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

scatter = ax.scatter(
    makespans, balances, energias,
    c='#2E86AB', s=100, alpha=0.7,
    edgecolors='black', linewidth=0.5
)

ax.set_xlabel('Makespan (s)', fontsize=12, labelpad=10)
ax.set_ylabel('Balance (Desv. Std)', fontsize=12, labelpad=10)
ax.set_zlabel('Energía (kWh)', fontsize=12, labelpad=10)
ax.set_title('Frente de Pareto Memético (3 objetivos)\nMakespan vs Balance vs Energía', 
             fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('tesis3/results/frente_pareto_memetico_3d.png', dpi=300, bbox_inches='tight')
print("   Guardado: frente_pareto_memetico_3d.png")
plt.close()

# ============================================================
# GRÁFICO 2: PROYECCIONES 2D (3 combinaciones)
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Proyecciones 2D del Frente de Pareto Memético', 
             fontsize=16, fontweight='bold')

# Makespan vs Balance
axes[0].scatter(makespans, balances, c='#2E86AB', s=80, alpha=0.7, 
               edgecolors='black', linewidth=0.5)
axes[0].set_xlabel('Makespan (s)', fontsize=11)
axes[0].set_ylabel('Balance (Desv. Std)', fontsize=11)
axes[0].set_title('Makespan vs Balance de Carga', fontweight='bold')
axes[0].grid(True, alpha=0.3)

# Makespan vs Energía
axes[1].scatter(makespans, energias, c='#A23B72', s=80, alpha=0.7, 
               edgecolors='black', linewidth=0.5)
axes[1].set_xlabel('Makespan (s)', fontsize=11)
axes[1].set_ylabel('Energía (kWh)', fontsize=11)
axes[1].set_title('Makespan vs Consumo Energético', fontsize=11, fontweight='bold')
axes[1].grid(True, alpha=0.3)

# Balance vs Energía
axes[2].scatter(balances, energias, c='#F18F01', s=80, alpha=0.7, 
               edgecolors='black', linewidth=0.5)
axes[2].set_xlabel('Balance (Desv. Std)', fontsize=11)
axes[2].set_ylabel('Energía (kWh)', fontsize=11)
axes[2].set_title('Balance vs Consumo Energético', fontweight='bold')
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('tesis3/results/frente_pareto_memetico_2d.png', dpi=300, bbox_inches='tight')
print("   Guardado: frente_pareto_memetico_2d.png")
plt.close()

# ============================================================
# GRÁFICO 3: EVOLUCIÓN DEL FRENTE
# ============================================================
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(historial, linewidth=2, color='#2E86AB')
ax.set_xlabel('Generación', fontsize=12)
ax.set_ylabel('Tamaño del Frente de Pareto', fontsize=12)
ax.set_title('Evolución del Frente de Pareto (Algoritmo Memético)', 
             fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('tesis3/results/evolucion_frente_memetico.png', dpi=300, bbox_inches='tight')
print("   Guardado: evolucion_frente_memetico.png")
plt.close()

# ============================================================
# GUARDAR DATOS DEL FRENTE EN CSV
# ============================================================
import csv

with open('tesis3/results/frente_pareto_memetico.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Makespan', 'Balance', 'Energia'])
    for i, (mk, bal, eng) in enumerate(metricas, 1):
        writer.writerow([i, f"{mk:.2f}", f"{bal:.2f}", f"{eng:.2f}"])

print("   Guardado: frente_pareto_memetico.csv")

# ============================================================
# TOP 10 SOLUCIONES
# ============================================================
print("\n" + "="*60)
print("TOP 10 SOLUCIONES DEL FRENTE DE PARETO MEMÉTICO")
print("="*60)

indices_top10 = sorted(range(len(makespans)), key=lambda i: makespans[i])[:10]

print(f"\n{'#':<4} {'Makespan':<12} {'Balance':<12} {'Energía':<12}")
print("-"*50)
for rank, idx in enumerate(indices_top10, 1):
    mk, bal, eng = metricas[idx]
    print(f"{rank:<4} {mk:<12.2f} {bal:<12.2f} {eng:<12.2f}")

print("\n" + "="*60)
print("VISUALIZACIONES COMPLETADAS")
print("="*60)
print("\nArchivos generados en tesis3/results/:")
print("  1. frente_pareto_memetico_3d.png (3D: Makespan vs Balance vs Energía)")
print("  2. frente_pareto_memetico_2d.png (3 proyecciones 2D)")
print("  3. evolucion_frente_memetico.png (evolución del frente)")
print("  4. frente_pareto_memetico.csv (datos)")
print("="*60)
