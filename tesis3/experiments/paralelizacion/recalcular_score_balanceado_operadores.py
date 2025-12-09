"""Recalcula el score balanceado para comparación de operadores desde CSV existente"""
import csv
import glob
import numpy as np
import yaml
from datetime import datetime

# Buscar archivos CSV de comparación de operadores
archivos_csv = glob.glob('tesis3/results/comparacion_operadores_real_*.csv')

if not archivos_csv:
    print("No se encontraron archivos CSV de comparación de operadores")
    exit(1)

# Usar el más reciente
archivo_csv = sorted(archivos_csv)[-1]
print(f"Procesando: {archivo_csv}")

# Leer resultados
resultados = []
with open(archivo_csv, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        resultados.append({
            'configuracion': row['configuracion'],
            'cruce': row['cruce'],
            'mutacion': row['mutacion'],
            'semilla': int(row['semilla']),
            'makespan': float(row['makespan']),
            'balance': float(row['balance']),
            'energia': float(row['energia']),
            'tamano_frente': int(row['tamano_frente']),
            'score_agregado': float(row['score_agregado']),
            'tiempo': float(row['tiempo'])
        })

# Agrupar por configuración
resultados_por_config = {}
for res in resultados:
    config_key = f"{res['cruce']}_{res['mutacion']}"
    if config_key not in resultados_por_config:
        resultados_por_config[config_key] = []
    resultados_por_config[config_key].append(res)

# Calcular promedios y score balanceado
configuraciones_analizadas = []
for config_key, resultados_config in resultados_por_config.items():
    prom_score = np.mean([r['score_agregado'] for r in resultados_config])
    prom_tiempo = np.mean([r['tiempo'] for r in resultados_config])
    prom_makespan = np.mean([r['makespan'] for r in resultados_config])
    prom_balance = np.mean([r['balance'] for r in resultados_config])
    prom_energia = np.mean([r['energia'] for r in resultados_config])
    prom_tamano_frente = np.mean([r['tamano_frente'] for r in resultados_config])
    
    std_score = np.std([r['score_agregado'] for r in resultados_config])
    std_makespan = np.std([r['makespan'] for r in resultados_config])
    std_balance = np.std([r['balance'] for r in resultados_config])
    std_energia = np.std([r['energia'] for r in resultados_config])
    
    configuraciones_analizadas.append({
        'config_key': config_key,
        'cruce': resultados_config[0]['cruce'],
        'mutacion': resultados_config[0]['mutacion'],
        'prom_score': prom_score,
        'prom_tiempo': prom_tiempo,
        'prom_makespan': prom_makespan,
        'prom_balance': prom_balance,
        'prom_energia': prom_energia,
        'prom_tamano_frente': prom_tamano_frente,
        'std_score': std_score,
        'std_makespan': std_makespan,
        'std_balance': std_balance,
        'std_energia': std_energia
    })

# Calcular score balanceado (igual que en tunning)
peso_score = 0.7
peso_tiempo = 0.3

scores = [c['prom_score'] for c in configuraciones_analizadas]
tiempos = [c['prom_tiempo'] for c in configuraciones_analizadas]

min_score = min(scores)
max_score = max(scores)
min_tiempo = min(tiempos)
max_tiempo = max(tiempos)

rango_score = max_score - min_score if max_score != min_score else 1.0
rango_tiempo = max_tiempo - min_tiempo if max_tiempo != min_tiempo else 1.0

for config in configuraciones_analizadas:
    score_norm = (config['prom_score'] - min_score) / rango_score
    tiempo_norm = (config['prom_tiempo'] - min_tiempo) / rango_tiempo
    config['score_balanceado'] = peso_score * score_norm + peso_tiempo * tiempo_norm

# Ordenar por score balanceado
configuraciones_analizadas.sort(key=lambda x: x['score_balanceado'])

# Mostrar resultados
print("\n" + "="*80)
print("RANKING CON SCORE BALANCEADO")
print("="*80)
print(f"Métrica balanceada = {peso_score*100:.0f}% score + {peso_tiempo*100:.0f}% tiempo")
print(f"{'Rank':<4} {'Configuración':<25} {'Score':<8} {'Tiempo':<8} {'Balance':<8} {'MK':<8} {'Bal':<8} {'Eng':<8}")
print("-"*100)

for i, res in enumerate(configuraciones_analizadas, 1):
    print(f"{i:<4} {res['config_key']:<25} {res['prom_score']:<8.4f} "
          f"{res['prom_tiempo']:<8.2f} {res['score_balanceado']:<8.4f} "
          f"{res['prom_makespan']:<8.2f} {res['prom_balance']:<8.2f} "
          f"{res['prom_energia']:<8.2f}")

# Mejor configuración
mejor = configuraciones_analizadas[0]
print(f"\n" + "="*80)
print("MEJOR CONFIGURACIÓN (CON SCORE BALANCEADO)")
print("="*80)
print(f"Configuración: {mejor['config_key']}")
print(f"Cruce: {mejor['cruce']}")
print(f"Mutación: {mejor['mutacion']}")
print(f"Score agregado: {mejor['prom_score']:.4f} ± {mejor['std_score']:.4f}")
print(f"Score balanceado: {mejor['score_balanceado']:.4f}")
print(f"Tiempo: {mejor['prom_tiempo']:.2f}s")
print(f"Makespan: {mejor['prom_makespan']:.2f} ± {mejor['std_makespan']:.2f}")
print(f"Balance: {mejor['prom_balance']:.2f} ± {mejor['std_balance']:.2f}")
print(f"Energía: {mejor['prom_energia']:.2f} ± {mejor['std_energia']:.2f}")

# Guardar mejor configuración actualizada
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
mejor_config_yaml = {
    'mejor_combinacion_operadores': {
        'cruce': mejor['cruce'],
        'mutacion': mejor['mutacion'],
        'nombre': f"{mejor['cruce']} + {mejor['mutacion']}"
    },
    'metricas_promedio': {
        'score_agregado': {
            'promedio': float(mejor['prom_score']),
            'desviacion_std': float(mejor['std_score'])
        },
        'score_balanceado': {
            'valor': float(mejor['score_balanceado']),
            'pesos': {'score': peso_score, 'tiempo': peso_tiempo}
        },
        'makespan': {
            'promedio': float(mejor['prom_makespan']),
            'desviacion_std': float(mejor['std_makespan'])
        },
        'balance': {
            'promedio': float(mejor['prom_balance']),
            'desviacion_std': float(mejor['std_balance'])
        },
        'energia': {
            'promedio': float(mejor['prom_energia']),
            'desviacion_std': float(mejor['std_energia'])
        },
        'tiempo': float(mejor['prom_tiempo']),
        'tamano_frente': float(mejor['prom_tamano_frente'])
    },
    'timestamp': timestamp,
    'nota': 'Recalculado con score balanceado (70% score + 30% tiempo)'
}

yaml_file = f'tesis3/results/mejor_configuracion_operadores_balanceado_{timestamp}.yaml'
with open(yaml_file, 'w') as f:
    yaml.dump(mejor_config_yaml, f, default_flow_style=False, sort_keys=False)

print(f"\nMejor configuración guardada en: {yaml_file}")
print("="*80)

