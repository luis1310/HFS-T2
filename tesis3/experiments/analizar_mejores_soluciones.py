"""Analiza las mejores soluciones del frente de Pareto usando la mejor versión (estándar o memético)"""
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
import numpy as np
import yaml
import os
import glob
import pickle
import json
from datetime import datetime

print("="*70)
print("ANÁLISIS DE LAS MEJORES SOLUCIONES DEL FRENTE DE PARETO")
print("="*70)

# DETERMINAR QUE VERSION USAR (basado en resultados de Fase 4)
print("\nDeterminando que version usar (estandar o memetico)...")
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
                print(f"   Version recomendada: MEMETICO")
                print(f"   Razon: {razon}")
            else:
                usar_memetico = False
                version_seleccionada = "estándar"
                print(f"   Version recomendada: ESTANDAR")
                print(f"   Razon: {razon}")
        elif 'comparacion' in resumen and 'mejora_score_pct' in resumen['comparacion']:
            # Fallback: inferir de mejora_score_pct (para compatibilidad con archivos antiguos)
            mejora_score = resumen['comparacion']['mejora_score_pct']
            
            if mejora_score > 0:
                usar_memetico = True
                version_seleccionada = "memético"
                print(f"   Memetico es MEJOR (mejora: {mejora_score:+.2f}%)")
                print(f"   Usando algoritmo MEMETICO para analisis")
            else:
                usar_memetico = False
                version_seleccionada = "estándar"
                print(f"   AVISO: Memetico NO mejora (mejora: {mejora_score:+.2f}%)")
                print(f"   Usando algoritmo ESTANDAR para analisis")
        else:
            print(f"   AVISO: No se encontro informacion de version recomendada en el resumen")
            print(f"   Usando algoritmo MEMETICO por defecto")
    except Exception as e:
        print(f"   AVISO: Error al leer resumen: {e}")
        print(f"   Usando algoritmo MEMETICO por defecto")
else:
    print(f"   AVISO: No se encontraron archivos de resumen de la Fase 4")
    print(f"   Usando algoritmo MEMETICO por defecto")
    print(f"   Ejecuta primero la Fase 4 para determinar la mejor version")

# Cargar configuración
config = ProblemConfig.from_yaml("tesis3/config/config.yaml")

# Leer parámetros del algoritmo
with open("tesis3/config/config.yaml") as f:
    full_config = yaml.safe_load(f)

alg_params = full_config['algorithm']['nsga2']
memetic_params = full_config['algorithm']['memetic']
operators_params = full_config['algorithm']['operators']

# Cargar operadores desde config.yaml (optimizados tras comparacion_operadores.py)
tipo_cruce = operators_params['cruce']
tipo_mutacion = operators_params['mutacion']

print(f"\nParámetros del algoritmo (desde config.yaml):")
print(f"   Población: {alg_params['tamano_poblacion']}")
print(f"   Generaciones: {alg_params['num_generaciones']}")
print(f"   Prob. cruce: {alg_params['prob_cruce']}")
print(f"   Prob. mutación: {alg_params['prob_mutacion']}")
print(f"   Operador cruce: {tipo_cruce}")
print(f"   Operador mutación: {tipo_mutacion}")
print(f"   Memético - cada_k_gen: {memetic_params['cada_k_generaciones']}")
print(f"   Memético - max_iter_local: {memetic_params['max_iteraciones_local']}")

def cruce(p1, p2, cfg, prob):
    return aplicar_cruce(p1, p2, cfg, metodo=tipo_cruce, prob_cruce=prob)

def mutacion(pob, cfg, prob):
    return aplicar_mutacion(pob, cfg, metodo=tipo_mutacion, tasa_mut=prob)

print(f"\nEjecutando NSGA-II {version_seleccionada.capitalize()} para obtener frente de Pareto...")
print(f"(Esto puede tomar ~{alg_params['num_generaciones'] * 0.05:.0f} segundos)\n")

# Ejecutar algoritmo con parámetros optimizados desde config.yaml
if usar_memetico:
    frente_pareto, fitness_pareto, _ = nsga2_memetic(
        config, cruce, mutacion,
        tamano_poblacion=alg_params['tamano_poblacion'],  # Usar parámetros optimizados
        num_generaciones=alg_params['num_generaciones'],  # Usar parámetros optimizados
        prob_cruce=alg_params['prob_cruce'],
        prob_mutacion=alg_params['prob_mutacion'],
        cada_k_gen=memetic_params['cada_k_generaciones'],
        max_iter_local=memetic_params['max_iteraciones_local'],
        verbose=False  # Sin output detallado
    )
else:
    # Usar versión estándar (sin búsqueda local)
    frente_pareto, fitness_pareto, _ = nsga2(
        config, cruce, mutacion,
        tamano_poblacion=alg_params['tamano_poblacion'],
        num_generaciones=alg_params['num_generaciones'],
        prob_cruce=alg_params['prob_cruce'],
        prob_mutacion=alg_params['prob_mutacion'],
        verbose=False
    )

print(f"Frente de Pareto obtenido: {len(frente_pareto)} soluciones")

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

# ============================================================
# IDENTIFICAR LAS 3 MEJORES SOLUCIONES
# ============================================================
print("\n" + "="*70)
print("IDENTIFICANDO LAS 3 MEJORES SOLUCIONES")
print("="*70)

# Solución 1: Mejor Makespan
idx_mejor_makespan = np.argmin(makespans)
solucion_1 = {
    'nombre': 'Solución 1: Prioriza Makespan',
    'indice': idx_mejor_makespan,
    'makespan': makespans[idx_mejor_makespan],
    'balance': balances[idx_mejor_makespan],
    'energia': energias[idx_mejor_makespan],
    'cromosoma': frente_pareto[idx_mejor_makespan]
}

# Solución 2: Mejor Balance
idx_mejor_balance = np.argmin(balances)
solucion_2 = {
    'nombre': 'Solución 2: Prioriza Balance de Carga',
    'indice': idx_mejor_balance,
    'makespan': makespans[idx_mejor_balance],
    'balance': balances[idx_mejor_balance],
    'energia': energias[idx_mejor_balance],
    'cromosoma': frente_pareto[idx_mejor_balance]
}

# Solución 3: Mejor Energía
idx_mejor_energia = np.argmin(energias)
solucion_3 = {
    'nombre': 'Solución 3: Prioriza Consumo Energético',
    'indice': idx_mejor_energia,
    'makespan': makespans[idx_mejor_energia],
    'balance': balances[idx_mejor_energia],
    'energia': energias[idx_mejor_energia],
    'cromosoma': frente_pareto[idx_mejor_energia]
}

# ============================================================
# PRESENTAR LAS 3 MEJORES SOLUCIONES
# ============================================================
print("\n" + "="*70)
print("LAS 3 MEJORES SOLUCIONES DEL FRENTE DE PARETO")
print("="*70)

soluciones = [solucion_1, solucion_2, solucion_3]

for i, sol in enumerate(soluciones, 1):
    print(f"\n{sol['nombre']}:")
    print(f"   Makespan:     {sol['makespan']:.2f}s")
    print(f"   Balance:      {sol['balance']:.2f}")
    print(f"   Energía:       {sol['energia']:.2f} kWh")
    print(f"   Índice:       {sol['indice']}")

# ============================================================
# ANÁLISIS DE TRADE-OFFS
# ============================================================
print("\n" + "="*70)
print("ANÁLISIS DE TRADE-OFFS")
print("="*70)

print("\nComparación entre soluciones:")
print(f"{'Métrica':<15} {'Sol. 1 (MK)':<15} {'Sol. 2 (Bal)':<15} {'Sol. 3 (Eng)':<15}")
print("-"*70)
print(f"{'Makespan (s)':<15} {solucion_1['makespan']:<15.2f} {solucion_2['makespan']:<15.2f} {solucion_3['makespan']:<15.2f}")
print(f"{'Balance':<15} {solucion_1['balance']:<15.2f} {solucion_2['balance']:<15.2f} {solucion_3['balance']:<15.2f}")
print(f"{'Energía (kWh)':<15} {solucion_1['energia']:<15.2f} {solucion_2['energia']:<15.2f} {solucion_3['energia']:<15.2f}")

# Calcular diferencias
print(f"\nDiferencias respecto a la mejor en cada objetivo:")
print(f"   Makespan: Sol.1 es {solucion_1['makespan']:.2f}s (mejor)")
print(f"   Balance:  Sol.2 es {solucion_2['balance']:.2f} (mejor)")
print(f"   Energía:  Sol.3 es {solucion_3['energia']:.2f} kWh (mejor)")

# ============================================================
# VERIFICAR DOMINANCIA
# ============================================================
print("\n" + "="*70)
print("VERIFICACIÓN DE DOMINANCIA")
print("="*70)

def verificar_dominancia(sol1, sol2):
    """Verifica si sol1 domina a sol2"""
    domina = False
    igual = True
    
    if sol1['makespan'] < sol2['makespan']:
        domina = True
        igual = False
    elif sol1['makespan'] > sol2['makespan']:
        igual = False
    
    if sol1['balance'] < sol2['balance']:
        domina = True
        igual = False
    elif sol1['balance'] > sol2['balance']:
        igual = False
    
    if sol1['energia'] < sol2['energia']:
        domina = True
        igual = False
    elif sol1['energia'] > sol2['energia']:
        igual = False
    
    return domina, igual

def analizar_dominancia_parcial(sol1, sol2):
    """Analiza dominancia parcial entre dos soluciones"""
    objetivos = ['makespan', 'balance', 'energia']
    sol1_mejor = 0
    sol2_mejor = 0
    iguales = 0
    
    for obj in objetivos:
        if sol1[obj] < sol2[obj]:
            sol1_mejor += 1
        elif sol1[obj] > sol2[obj]:
            sol2_mejor += 1
        else:
            iguales += 1
    
    return sol1_mejor, sol2_mejor, iguales

print("Verificando si alguna solución domina a otra:")
for i in range(3):
    for j in range(3):
        if i != j:
            sol_i = soluciones[i]
            sol_j = soluciones[j]
            domina, igual = verificar_dominancia(sol_i, sol_j)
            
            if domina:
                print(f"   {sol_i['nombre']} DOMINA a {sol_j['nombre']}")
            elif igual:
                print(f"   {sol_i['nombre']} es IGUAL a {sol_j['nombre']}")
            else:
                print(f"   {sol_i['nombre']} NO domina a {sol_j['nombre']} (trade-off)")

# ============================================================
# ANÁLISIS DE DOMINANCIA PARCIAL
# ============================================================
print("\n" + "="*70)
print("ANÁLISIS DE DOMINANCIA PARCIAL")
print("="*70)

print("Análisis detallado de dominancia parcial:")
for i in range(3):
    for j in range(3):
        if i != j:
            sol_i = soluciones[i]
            sol_j = soluciones[j]
            sol_i_mejor, sol_j_mejor, iguales = analizar_dominancia_parcial(sol_i, sol_j)
            
            print(f"\n{sol_i['nombre']} vs {sol_j['nombre']}:")
            print(f"   {sol_i['nombre']} es mejor en {sol_i_mejor} objetivos")
            print(f"   {sol_j['nombre']} es mejor en {sol_j_mejor} objetivos")
            print(f"   Iguales en {iguales} objetivos")
            
            if sol_i_mejor > sol_j_mejor:
                print(f"   {sol_i['nombre']} tiene ventaja parcial")
            elif sol_j_mejor > sol_i_mejor:
                print(f"   {sol_j['nombre']} tiene ventaja parcial")
            else:
                print(f"   Empate en dominancia parcial")

# ============================================================
# GRÁFICO DE LAS 3 MEJORES SOLUCIONES
# ============================================================
print("\n" + "="*70)
print("GENERANDO VISUALIZACIÓN")
print("="*70)

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Las 3 Mejores Soluciones del Frente de Pareto', 
             fontsize=16, fontweight='bold')

# Colores para las 3 soluciones
colores = ['#FF6B6B', '#4ECDC4', '#45B7D1']
nombres = ['Sol. 1 (MK)', 'Sol. 2 (Bal)', 'Sol. 3 (Eng)']

# Makespan vs Balance
axes[0].scatter(makespans, balances, c='lightgray', s=20, alpha=0.5, label='Frente completo')
for i, sol in enumerate(soluciones):
    axes[0].scatter(sol['makespan'], sol['balance'], c=colores[i], s=200, 
                   edgecolors='black', linewidth=2, label=nombres[i])
axes[0].set_xlabel('Makespan (s)', fontsize=11)
axes[0].set_ylabel('Balance (Desv. Std)', fontsize=11)
axes[0].set_title('Makespan vs Balance', fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Makespan vs Energía
axes[1].scatter(makespans, energias, c='lightgray', s=20, alpha=0.5, label='Frente completo')
for i, sol in enumerate(soluciones):
    axes[1].scatter(sol['makespan'], sol['energia'], c=colores[i], s=200, 
                   edgecolors='black', linewidth=2, label=nombres[i])
axes[1].set_xlabel('Makespan (s)', fontsize=11)
axes[1].set_ylabel('Energía (kWh)', fontsize=11)
axes[1].set_title('Makespan vs Energía', fontweight='bold')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Balance vs Energía
axes[2].scatter(balances, energias, c='lightgray', s=20, alpha=0.5, label='Frente completo')
for i, sol in enumerate(soluciones):
    axes[2].scatter(sol['balance'], sol['energia'], c=colores[i], s=200, 
                   edgecolors='black', linewidth=2, label=nombres[i])
axes[2].set_xlabel('Balance (Desv. Std)', fontsize=11)
axes[2].set_ylabel('Energía (kWh)', fontsize=11)
axes[2].set_title('Balance vs Energía', fontweight='bold')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()

# Asegurar que el directorio existe
os.makedirs('tesis3/results', exist_ok=True)

plt.savefig('tesis3/results/mejores_soluciones_pareto.png', dpi=300, bbox_inches='tight')
print("   Guardado: mejores_soluciones_pareto.png")

# ============================================================
# GUARDAR DATOS
# ============================================================
import csv

with open('tesis3/results/mejores_soluciones.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Solucion', 'Makespan', 'Balance', 'Energia', 'Indice'])
    for sol in soluciones:
        writer.writerow([
            sol['nombre'], 
            f"{sol['makespan']:.2f}", 
            f"{sol['balance']:.2f}", 
            f"{sol['energia']:.2f}",
            sol['indice']
        ])

print("   Guardado: mejores_soluciones.csv")

# ============================================================
# GUARDAR CROMOSOMAS COMPLETOS (SOLUCIONES)
# ============================================================
print("\n" + "="*70)
print("GUARDANDO SOLUCIONES COMPLETAS")
print("="*70)

# Guardar cromosomas usando pickle (formato binario, preserva objetos completos)
pickle_file = f'tesis3/results/mejores_soluciones_cromosomas_{timestamp}.pkl'
soluciones_completas = {
    'solucion_1_prioriza_makespan': {
        'cromosoma': solucion_1['cromosoma'],
        'metricas': {
            'makespan': solucion_1['makespan'],
            'balance': solucion_1['balance'],
            'energia': solucion_1['energia']
        }
    },
    'solucion_2_prioriza_balance': {
        'cromosoma': solucion_2['cromosoma'],
        'metricas': {
            'makespan': solucion_2['makespan'],
            'balance': solucion_2['balance'],
            'energia': solucion_2['energia']
        }
    },
    'solucion_3_prioriza_energia': {
        'cromosoma': solucion_3['cromosoma'],
        'metricas': {
            'makespan': solucion_3['makespan'],
            'balance': solucion_3['balance'],
            'energia': solucion_3['energia']
        }
    },
    'config': config  # Guardar también la configuración para poder evaluar después
}

with open(pickle_file, 'wb') as f:
    pickle.dump(soluciones_completas, f)

print(f"   Guardado: mejores_soluciones_cromosomas_{timestamp}.pkl")
print("   (Formato binario, contiene los cromosomas completos para recuperación)")

# Guardar también los genes en formato JSON (legible)
json_file = f'tesis3/results/mejores_soluciones_genes_{timestamp}.json'
# Los genes son listas de listas de enteros, se pueden serializar directamente
genes_serializados = {
    'solucion_1_prioriza_makespan': {
        'genes': solucion_1['cromosoma'].genes,
        'metricas': {
            'makespan': float(solucion_1['makespan']),
            'balance': float(solucion_1['balance']),
            'energia': float(solucion_1['energia'])
        },
        'descripcion': 'Solución que prioriza minimizar el makespan (tiempo de ejecución total)'
    },
    'solucion_2_prioriza_balance': {
        'genes': solucion_2['cromosoma'].genes,
        'metricas': {
            'makespan': float(solucion_2['makespan']),
            'balance': float(solucion_2['balance']),
            'energia': float(solucion_2['energia'])
        },
        'descripcion': 'Solución que prioriza minimizar el balance de carga entre máquinas'
    },
    'solucion_3_prioriza_energia': {
        'genes': solucion_3['cromosoma'].genes,
        'metricas': {
            'makespan': float(solucion_3['makespan']),
            'balance': float(solucion_3['balance']),
            'energia': float(solucion_3['energia'])
        },
        'descripcion': 'Solución que prioriza minimizar el consumo energético'
    },
    'formato_genes': 'Los genes son una lista de listas: genes[pedido][etapa] = maquina_asignada'
}

with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(genes_serializados, f, indent=2, ensure_ascii=False)

print(f"   Guardado: mejores_soluciones_genes_{timestamp}.json")
print("   (Formato JSON legible, contiene los genes de cada solución)")

# ============================================================
# GENERAR RESUMEN ESTRUCTURADO PARA EL CLIENTE
# ============================================================
print("\n" + "="*70)
print("GENERANDO RESUMEN PARA CLIENTE")
print("="*70)

# Calcular diferencias porcentuales entre soluciones
def calcular_diferencias(sol_ref, sol_comp):
    """Calcula diferencias porcentuales entre dos soluciones"""
    return {
        'makespan_pct': ((sol_comp['makespan'] - sol_ref['makespan']) / sol_ref['makespan']) * 100,
        'balance_pct': ((sol_comp['balance'] - sol_ref['balance']) / sol_ref['balance']) * 100,
        'energia_pct': ((sol_comp['energia'] - sol_ref['energia']) / sol_ref['energia']) * 100
    }

# Generar recomendaciones de uso
recomendaciones = {
    'solucion_1': {
        'cuando_usar': 'Cuando el tiempo de ejecución (makespan) es crítico y se necesita minimizar el tiempo total de procesamiento.',
        'ventajas': f'Makespan mínimo: {solucion_1["makespan"]:.2f}s. Ideal para sistemas con restricciones de tiempo estrictas.',
        'desventajas': f'Balance y energía pueden ser mayores que otras soluciones.'
    },
    'solucion_2': {
        'cuando_usar': 'Cuando se requiere balancear la carga entre máquinas para evitar sobrecargas y mejorar la distribución del trabajo.',
        'ventajas': f'Balance óptimo: {solucion_2["balance"]:.2f}. Distribución más uniforme de tareas entre máquinas.',
        'desventajas': f'Makespan y energía pueden ser mayores que otras soluciones.'
    },
    'solucion_3': {
        'cuando_usar': 'Cuando el consumo energético es una preocupación principal y se busca minimizar costos operativos.',
        'ventajas': f'Energía mínima: {solucion_3["energia"]:.2f} kWh. Reduce costos operativos y huella de carbono.',
        'desventajas': f'Makespan y balance pueden ser mayores que otras soluciones.'
    }
}

# Crear resumen estructurado
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
resumen_yaml = {
    'metadata': {
        'fecha_analisis': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'version_algoritmo': version_seleccionada,
        'total_soluciones_frente': len(frente_pareto),
        'parametros_algoritmo': {
            'tamano_poblacion': alg_params['tamano_poblacion'],
            'num_generaciones': alg_params['num_generaciones'],
            'prob_cruce': alg_params['prob_cruce'],
            'prob_mutacion': alg_params['prob_mutacion'],
            'operador_cruce': tipo_cruce,
            'operador_mutacion': tipo_mutacion
        }
    },
    'mejores_soluciones': {
        'solucion_1_prioriza_makespan': {
            'metricas': {
                'makespan_s': float(solucion_1['makespan']),
                'balance': float(solucion_1['balance']),
                'energia_kwh': float(solucion_1['energia']),
                'indice_frente': int(solucion_1['indice'])
            },
            'recomendacion': recomendaciones['solucion_1']
        },
        'solucion_2_prioriza_balance': {
            'metricas': {
                'makespan_s': float(solucion_2['makespan']),
                'balance': float(solucion_2['balance']),
                'energia_kwh': float(solucion_2['energia']),
                'indice_frente': int(solucion_2['indice'])
            },
            'recomendacion': recomendaciones['solucion_2']
        },
        'solucion_3_prioriza_energia': {
            'metricas': {
                'makespan_s': float(solucion_3['makespan']),
                'balance': float(solucion_3['balance']),
                'energia_kwh': float(solucion_3['energia']),
                'indice_frente': int(solucion_3['indice'])
            },
            'recomendacion': recomendaciones['solucion_3']
        }
    },
    'comparacion': {
        'rango_makespan': {
            'min': float(min(solucion_1['makespan'], solucion_2['makespan'], solucion_3['makespan'])),
            'max': float(max(solucion_1['makespan'], solucion_2['makespan'], solucion_3['makespan'])),
            'diferencia_pct': float(((max(solucion_1['makespan'], solucion_2['makespan'], solucion_3['makespan']) - 
                                    min(solucion_1['makespan'], solucion_2['makespan'], solucion_3['makespan'])) / 
                                   min(solucion_1['makespan'], solucion_2['makespan'], solucion_3['makespan'])) * 100)
        },
        'rango_balance': {
            'min': float(min(solucion_1['balance'], solucion_2['balance'], solucion_3['balance'])),
            'max': float(max(solucion_1['balance'], solucion_2['balance'], solucion_3['balance'])),
            'diferencia_pct': float(((max(solucion_1['balance'], solucion_2['balance'], solucion_3['balance']) - 
                                    min(solucion_1['balance'], solucion_2['balance'], solucion_3['balance'])) / 
                                   min(solucion_1['balance'], solucion_2['balance'], solucion_3['balance'])) * 100)
        },
        'rango_energia': {
            'min': float(min(solucion_1['energia'], solucion_2['energia'], solucion_3['energia'])),
            'max': float(max(solucion_1['energia'], solucion_2['energia'], solucion_3['energia'])),
            'diferencia_pct': float(((max(solucion_1['energia'], solucion_2['energia'], solucion_3['energia']) - 
                                    min(solucion_1['energia'], solucion_2['energia'], solucion_3['energia'])) / 
                                   min(solucion_1['energia'], solucion_2['energia'], solucion_3['energia'])) * 100)
        }
    },
    'resumen_ejecutivo': {
        'total_soluciones_analizadas': len(frente_pareto),
        'soluciones_recomendadas': 3,
        'conclusion': f'Se identificaron 3 soluciones óptimas que representan los trade-offs principales del problema multi-objetivo. Cada solución prioriza un objetivo diferente (makespan, balance o energía), permitiendo al cliente elegir según sus necesidades específicas.'
    }
}

# Guardar resumen YAML
yaml_file = f'tesis3/results/mejores_soluciones_resumen_{timestamp}.yaml'
with open(yaml_file, 'w', encoding='utf-8') as f:
    yaml.dump(resumen_yaml, f, sort_keys=False, allow_unicode=True, default_flow_style=False)

print(f"   Guardado: mejores_soluciones_resumen_{timestamp}.yaml")

# ============================================================
# RESUMEN EJECUTIVO EN CONSOLA
# ============================================================
print("\n" + "="*70)
print("RESUMEN EJECUTIVO PARA CLIENTE")
print("="*70)

print(f"\nSe analizaron {len(frente_pareto)} soluciones del frente de Pareto")
print(f"Se identificaron 3 soluciones optimas segun prioridad de objetivos\n")

print("SOLUCION 1: Prioriza Makespan (Tiempo de Ejecucion)")
print(f"   Makespan: {solucion_1['makespan']:.2f}s (MEJOR)")
print(f"   Balance:  {solucion_1['balance']:.2f}")
print(f"   Energia:  {solucion_1['energia']:.2f} kWh")
print(f"   Cuando usar: {recomendaciones['solucion_1']['cuando_usar']}")

print("\nSOLUCION 2: Prioriza Balance de Carga")
print(f"   Makespan: {solucion_2['makespan']:.2f}s")
print(f"   Balance:  {solucion_2['balance']:.2f} (MEJOR)")
print(f"   Energia:  {solucion_2['energia']:.2f} kWh")
print(f"   Cuando usar: {recomendaciones['solucion_2']['cuando_usar']}")

print("\nSOLUCION 3: Prioriza Consumo Energetico")
print(f"   Makespan: {solucion_3['makespan']:.2f}s")
print(f"   Balance:  {solucion_3['balance']:.2f}")
print(f"   Energia:  {solucion_3['energia']:.2f} kWh (MEJOR)")
print(f"   Cuando usar: {recomendaciones['solucion_3']['cuando_usar']}")

print("\n" + "="*70)
print("ANALISIS COMPLETADO")
print("="*70)
print("\nArchivos generados:")
print("  1. mejores_soluciones_pareto.png (visualizacion grafica)")
print("  2. mejores_soluciones.csv (datos tabulares)")
print(f"  3. mejores_soluciones_resumen_{timestamp}.yaml (resumen estructurado)")
print(f"  4. mejores_soluciones_cromosomas_{timestamp}.pkl (cromosomas completos)")
print(f"  5. mejores_soluciones_genes_{timestamp}.json (genes en formato legible)")
print("\nEl archivo YAML contiene toda la informacion estructurada")
print("necesaria para presentar al cliente, incluyendo:")
print("  - Metricas detalladas de cada solucion")
print("  - Recomendaciones de cuando usar cada una")
print("  - Comparaciones y rangos de valores")
print("  - Resumen ejecutivo")
print("\nLos archivos .pkl y .json contienen las soluciones completas")
print("para poder recuperarlas y ejecutarlas posteriormente.")
print("="*70)
