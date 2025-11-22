"""Genera visualizaciones del frente de Pareto usando la mejor versión (estándar o memético)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tesis3.src.core.problem import ProblemConfig
from tesis3.src.algorithms.nsga2 import nsga2
from tesis3.src.algorithms.nsga2_memetic import nsga2_memetic
from tesis3.src.operators.crossover import aplicar_cruce
from tesis3.src.operators.mutation import aplicar_mutacion
from tesis3.src.fitness.multi_objective import fitness_multiobjetivo
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import yaml
import os
import glob

print("="*60)
print("VISUALIZACIÓN DEL FRENTE DE PARETO")
print("="*60)

# 🔍 DETERMINAR QUÉ VERSIÓN USAR (basado en resultados de Fase 4)
print("\n🔍 Determinando qué versión usar (estándar o memético)...")
print("   Buscando resultados de la Fase 4 (comparacion_memetica_resumen_*.yaml)...")

archivos_resumen = glob.glob('tesis3/results/comparacion_memetica_resumen_*.yaml')
usar_memetico = True  # Por defecto usar memético
version_seleccionada = "memético"

if archivos_resumen:
    # Ordenar por fecha (más reciente primero)
    archivos_resumen.sort(reverse=True)
    archivo_mas_reciente = archivos_resumen[0]
    
    try:
        with open(archivo_mas_reciente, 'r') as f:
            resumen = yaml.safe_load(f)
        
        if 'comparacion' in resumen and 'version_recomendada' in resumen['comparacion']:
            version_recomendada = resumen['comparacion']['version_recomendada']
            razon = resumen['comparacion'].get('razon', 'No especificada')
            
            if version_recomendada == 'memetico':
                usar_memetico = True
                version_seleccionada = "memético"
                print(f"   ✅ Versión recomendada: MEMÉTICO")
                print(f"   → Razón: {razon}")
            else:
                usar_memetico = False
                version_seleccionada = "estándar"
                print(f"   ✅ Versión recomendada: ESTÁNDAR")
                print(f"   → Razón: {razon}")
        elif 'comparacion' in resumen and 'mejora_score_pct' in resumen['comparacion']:
            # Fallback: inferir de mejora_score_pct (para compatibilidad con archivos antiguos)
            mejora_score = resumen['comparacion']['mejora_score_pct']
            
            if mejora_score > 0:
                usar_memetico = True
                version_seleccionada = "memético"
                print(f"   ✅ Memético es MEJOR (mejora: {mejora_score:+.2f}%)")
                print(f"   → Usando algoritmo MEMÉTICO para visualizaciones")
            else:
                usar_memetico = False
                version_seleccionada = "estándar"
                print(f"   ⚠️  Memético NO mejora (mejora: {mejora_score:+.2f}%)")
                print(f"   → Usando algoritmo ESTÁNDAR para visualizaciones")
        else:
            print(f"   ⚠️  No se encontró información de versión recomendada en el resumen")
            print(f"   → Usando algoritmo MEMÉTICO por defecto")
    except Exception as e:
        print(f"   ⚠️  Error al leer resumen: {e}")
        print(f"   → Usando algoritmo MEMÉTICO por defecto")
else:
    print(f"   ⚠️  No se encontraron archivos de resumen de la Fase 4")
    print(f"   → Usando algoritmo MEMÉTICO por defecto")
    print(f"   → Ejecuta primero la Fase 4 para determinar la mejor versión")

# Cargar configuración completa
config = ProblemConfig.from_yaml("tesis3/config/config.yaml")

# Leer parámetros del algoritmo desde YAML
with open("tesis3/config/config.yaml") as f:
    full_config = yaml.safe_load(f)

alg_params = full_config['algorithm']['nsga2']
memetic_params = full_config['algorithm']['memetic']
operators_params = full_config['algorithm']['operators']

print(f"\nParámetros del algoritmo (desde config.yaml):")
print(f"   Población: {alg_params['tamano_poblacion']}")
print(f"   Generaciones: {alg_params['num_generaciones']}")
print(f"   Prob. cruce: {alg_params['prob_cruce']}")
print(f"   Prob. mutación: {alg_params['prob_mutacion']}")
print(f"   Operador cruce: {operators_params['cruce']}")
print(f"   Operador mutación: {operators_params['mutacion']}")
print(f"   Memético: {memetic_params['activado']}")
print(f"   Búsqueda local cada: {memetic_params['cada_k_generaciones']} gen")
print(f"   Iteraciones locales: {memetic_params['max_iteraciones_local']}")

# Cargar tipos de operadores desde config.yaml
tipo_cruce = operators_params['cruce']
tipo_mutacion = operators_params['mutacion']

def cruce(p1, p2, cfg, prob):
    return aplicar_cruce(p1, p2, cfg, metodo=tipo_cruce, prob_cruce=prob)

def mutacion(pob, cfg, prob):
    return aplicar_mutacion(pob, cfg, metodo=tipo_mutacion, tasa_mut=prob)

print(f"\nEjecutando NSGA-II {version_seleccionada.capitalize()} ({tipo_cruce.capitalize()} + {tipo_mutacion.capitalize()})...")
print(f"   Esto tomará ~{alg_params['num_generaciones'] * 0.05:.0f} segundos\n")

if usar_memetico:
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
else:
    # Usar versión estándar (sin búsqueda local)
    frente_pareto, fitness_pareto, historial = nsga2(
        config, cruce, mutacion,
        tamano_poblacion=alg_params['tamano_poblacion'],
        num_generaciones=alg_params['num_generaciones'],
        prob_cruce=alg_params['prob_cruce'],
        prob_mutacion=alg_params['prob_mutacion'],
        verbose=True
    )
    # Para estándar, historial puede ser None, crear uno básico
    if historial is None:
        historial = [len(frente_pareto)] * alg_params['num_generaciones']

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
ax.set_title(f'Frente de Pareto {version_seleccionada.capitalize()} (3 objetivos)\nMakespan vs Balance vs Energía', 
             fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
nombre_archivo_3d = f'tesis3/results/frente_pareto_{version_seleccionada.lower()}_3d.png'
plt.savefig(nombre_archivo_3d, dpi=300, bbox_inches='tight')
print(f"   Guardado: frente_pareto_{version_seleccionada.lower()}_3d.png")
plt.close()

# ============================================================
# GRÁFICO 2: PROYECCIONES 2D (3 combinaciones)
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle(f'Proyecciones 2D del Frente de Pareto {version_seleccionada.capitalize()}', 
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
nombre_archivo_2d = f'tesis3/results/frente_pareto_{version_seleccionada.lower()}_2d.png'
plt.savefig(nombre_archivo_2d, dpi=300, bbox_inches='tight')
print(f"   Guardado: frente_pareto_{version_seleccionada.lower()}_2d.png")
plt.close()

# ============================================================
# GRÁFICO 3: EVOLUCIÓN DEL FRENTE
# ============================================================
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(historial, linewidth=2, color='#2E86AB')
ax.set_xlabel('Generación', fontsize=12)
ax.set_ylabel('Tamaño del Frente de Pareto', fontsize=12)
ax.set_title(f'Evolución del Frente de Pareto (Algoritmo {version_seleccionada.capitalize()})', 
             fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)

plt.tight_layout()
nombre_archivo_evol = f'tesis3/results/evolucion_frente_{version_seleccionada.lower()}.png'
plt.savefig(nombre_archivo_evol, dpi=300, bbox_inches='tight')
print(f"   Guardado: evolucion_frente_{version_seleccionada.lower()}.png")
plt.close()

# ============================================================
# GUARDAR DATOS DEL FRENTE EN CSV
# ============================================================
import csv

nombre_archivo_csv = f'tesis3/results/frente_pareto_{version_seleccionada.lower()}.csv'
with open(nombre_archivo_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ID', 'Makespan', 'Balance', 'Energia'])
    for i, (mk, bal, eng) in enumerate(metricas, 1):
        writer.writerow([i, f"{mk:.2f}", f"{bal:.2f}", f"{eng:.2f}"])

print(f"   Guardado: frente_pareto_{version_seleccionada.lower()}.csv")

# ============================================================
# TOP 10 SOLUCIONES
# ============================================================
print("\n" + "="*60)
print(f"TOP 10 SOLUCIONES DEL FRENTE DE PARETO {version_seleccionada.upper()}")
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
print(f"  1. frente_pareto_{version_seleccionada.lower()}_3d.png (3D: Makespan vs Balance vs Energía)")
print(f"  2. frente_pareto_{version_seleccionada.lower()}_2d.png (3 proyecciones 2D)")
print(f"  3. evolucion_frente_{version_seleccionada.lower()}.png (evolución del frente)")
print(f"  4. frente_pareto_{version_seleccionada.lower()}.csv (datos)")
print("="*60)
