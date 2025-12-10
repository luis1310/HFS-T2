"""Regenera el archivo de resumen de ablación desde el archivo detallado"""
import csv
import numpy as np
from collections import defaultdict

# Archivo detallado existente
archivo_detallado = 'tesis3/results/ablacion_detallado_20251130_080815.csv'
archivo_resumen = 'tesis3/results/ablacion_resumen_20251130_080815.csv'

# Leer resultados detallados
resultados_por_variante = defaultdict(list)

with open(archivo_detallado, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        variante = row['variante']
        resultados_por_variante[variante].append({
            'tiempo': float(row['tiempo']),
            'score_agregado': float(row['score_agregado']),
            'makespan': float(row['makespan']),
            'balance': float(row['balance']),
            'energia': float(row['energia']),
            'tamano_frente': float(row['tamano_frente'])
        })

# Calcular promedios por variante
resultados_resumen = []

# Descripciones de variantes
descripciones = {
    'NSGA2_completo': 'NSGA2 completo (filtro epsilon + cruce uniforme + mutación swap)',
    'NSGA2_sin_filtro': 'NSGA2 sin filtro epsilon (base NSGA2)',
    'NSGA2_one_point': 'NSGA2 con cruce one-point',
    'NSGA2_mutacion_insert': 'NSGA2 con mutación insert',
    'NSGA2_mutacion_invert': 'NSGA2 con mutación invert',
    'Memetico_completo': 'Memético completo (filtro + búsqueda local + cache + optimizaciones)',
    'Memetico_sin_filtro': 'Memético sin filtro epsilon (solo búsqueda local)',
    'Memetico_sin_busqueda_local': 'Memético sin búsqueda local (≈NSGA2 con cache y optimizaciones)',
    'Memetico_sin_filtro_ni_busqueda': 'Memético base (≈NSGA2 estándar con cache y optimizaciones)',
    'Memetico_one_point': 'Memético con cruce one-point',
    'Memetico_mutacion_insert': 'Memético con mutación insert'
}

for variante_nombre, resultados_variante in resultados_por_variante.items():
    if len(resultados_variante) == 0:
        continue
    
    prom_tiempo = np.mean([r['tiempo'] for r in resultados_variante])
    prom_score = np.mean([r['score_agregado'] for r in resultados_variante])
    prom_makespan = np.mean([r['makespan'] for r in resultados_variante])
    prom_balance = np.mean([r['balance'] for r in resultados_variante])
    prom_energia = np.mean([r['energia'] for r in resultados_variante])
    prom_tamano_frente = np.mean([r['tamano_frente'] for r in resultados_variante])
    
    std_tiempo = np.std([r['tiempo'] for r in resultados_variante])
    std_score = np.std([r['score_agregado'] for r in resultados_variante])
    
    descripcion = descripciones.get(variante_nombre, variante_nombre)
    
    resultados_resumen.append({
        'variante': variante_nombre,
        'descripcion': descripcion,
        'prom_tiempo': prom_tiempo,
        'std_tiempo': std_tiempo,
        'prom_score': prom_score,
        'std_score': std_score,
        'prom_makespan': prom_makespan,
        'prom_balance': prom_balance,
        'prom_energia': prom_energia,
        'prom_tamano_frente': prom_tamano_frente
    })

# Ordenar por tiempo
resultados_resumen = sorted(resultados_resumen, key=lambda x: x['prom_tiempo'])

# Guardar resumen
with open(archivo_resumen, 'w', newline='') as f:
    fieldnames = ['variante', 'descripcion', 'prom_tiempo', 'std_tiempo',
                 'prom_score', 'std_score', 'prom_makespan', 'prom_balance',
                 'prom_energia', 'prom_tamano_frente']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in resultados_resumen:
        writer.writerow(r)

print(f"Resumen regenerado: {archivo_resumen}")
print(f"   Variantes procesadas: {len(resultados_resumen)}")
print(f"\nResumen:")
print(f"{'Variante':<30} {'Tiempo (s)':<12} {'Score':<10} {'Makespan':<10} {'Balance':<10} {'Energía':<10} {'Frente':<8}")
print("-"*100)
for r in resultados_resumen:
    print(f"{r['variante']:<30} {r['prom_tiempo']:<12.2f} {r['prom_score']:<10.4f} "
          f"{r['prom_makespan']:<10.2f} {r['prom_balance']:<10.2f} {r['prom_energia']:<10.2f} "
          f"{r['prom_tamano_frente']:<8.1f}")

