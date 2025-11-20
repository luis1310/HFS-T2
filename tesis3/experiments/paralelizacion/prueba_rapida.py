"""Prueba rápida de paralelización REAL"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tesis3.src.core.problem import ProblemConfig
from tesis3.src.algorithms.nsga2_memetic import nsga2_memetic
from tesis3.src.operators.crossover import aplicar_cruce
from tesis3.src.operators.mutation import aplicar_mutacion
import numpy as np
import random
import time
import csv
import os
import yaml
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import psutil

print("="*70)
print("PRUEBA RÁPIDA - PARALELIZACIÓN REAL")
print("="*70)

# Configuración del problema
config = ProblemConfig.from_yaml("tesis3/config/config.yaml")

def cruce(p1, p2, cfg, prob):
    return aplicar_cruce(p1, p2, cfg, metodo='uniforme', prob_cruce=prob)

def mutacion(pob, cfg, prob):
    return aplicar_mutacion(pob, cfg, metodo='invert', tasa_mut=prob)

def guardar_resultados_parciales(todos_resultados, num_semillas):
    """Guarda resultados parciales cada vez que se completa una configuración"""
    # Agrupar resultados por configuración
    resultados_agrupados = {}
    for res in todos_resultados:
        param_key = tuple(sorted(res['configuracion'].items()))
        if param_key not in resultados_agrupados:
            resultados_agrupados[param_key] = []
        resultados_agrupados[param_key].append(res)
    
    # Calcular promedios solo para configuraciones completas
    configuraciones_completas = []
    for param_key, res_list in resultados_agrupados.items():
        if len(res_list) == num_semillas:  # Solo configuraciones completas
            avg_mk = np.mean([r['makespan'] for r in res_list])
            avg_bal = np.mean([r['balance'] for r in res_list])
            avg_eng = np.mean([r['energia'] for r in res_list])
            avg_time = np.mean([r['tiempo'] for r in res_list])
            avg_score = np.mean([r['score_agregado'] for r in res_list])
            
            configuraciones_completas.append({
                'configuracion': dict(param_key),
                'prom_makespan': avg_mk,
                'prom_balance': avg_bal,
                'prom_energia': avg_eng,
                'prom_tiempo': avg_time,
                'prom_score': avg_score
            })
    
    # Asegurar que el directorio existe
    os.makedirs('tesis3/results', exist_ok=True)
    
    # Guardar en CSV con timestamp
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    output_file = f'tesis3/results/prueba_rapida_parcial_{timestamp}.csv'
    with open(output_file, 'w', newline='') as f:
        fieldnames = ['tamano_poblacion', 'num_generaciones', 'prob_cruce', 'prob_mutacion',
                      'cada_k_gen', 'max_iter_local', 'prom_makespan', 'prom_balance',
                      'prom_energia', 'prom_tiempo', 'prom_score']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for res in configuraciones_completas:
            row = res['configuracion'].copy()
            row.update({
                'prom_makespan': res['prom_makespan'],
                'prom_balance': res['prom_balance'],
                'prom_energia': res['prom_energia'],
                'prom_tiempo': res['prom_tiempo'],
                'prom_score': res['prom_score']
            })
            writer.writerow(row)
    
    print(f"    💾 Resultados parciales guardados: {len(configuraciones_completas)} configuraciones completas")

def verificar_configuraciones_completas(todos_resultados, num_semillas):
    """Verifica qué configuraciones están completas (tienen todas sus semillas)"""
    # Agrupar resultados por configuración
    resultados_agrupados = {}
    for res in todos_resultados:
        param_key = tuple(sorted(res['configuracion'].items()))
        if param_key not in resultados_agrupados:
            resultados_agrupados[param_key] = []
        resultados_agrupados[param_key].append(res)
    
    # Identificar configuraciones completas
    configuraciones_completas = []
    for param_key, res_list in resultados_agrupados.items():
        if len(res_list) == num_semillas:  # Configuración completa
            configuraciones_completas.append(dict(param_key))
    
    return configuraciones_completas

def ejecutar_semilla(args):
    """Ejecuta una semilla específica"""
    configuracion, semilla = args
    
    # Timestamp de inicio del proceso
    timestamp_inicio = time.strftime('%H:%M:%S.%f')[:-3]  # Incluir milisegundos
    print(f"🚀 INICIO: {timestamp_inicio} - Config {configuracion['tamano_poblacion']}-{configuracion['num_generaciones']}-{configuracion['prob_cruce']:.1f}-{configuracion['prob_mutacion']:.2f} - Semilla {semilla}")
    
    # Configurar semilla para reproducibilidad
    np.random.seed(semilla)
    random.seed(semilla)
    
    # Cargar valores de referencia desde config.yaml
    with open('tesis3/config/config.yaml', 'r') as f:
        config_completa = yaml.safe_load(f)
    valores_ref = config_completa['experiments']['valores_referencia']
    
    inicio = time.time()
    frente_pareto, fitness_pareto, _ = nsga2_memetic(
        config, cruce, mutacion,
        tamano_poblacion=configuracion['tamano_poblacion'],
        num_generaciones=configuracion['num_generaciones'],
        prob_cruce=configuracion['prob_cruce'],
        prob_mutacion=configuracion['prob_mutacion'],
        cada_k_gen=configuracion['cada_k_gen'],
        max_iter_local=configuracion['max_iter_local'],
        verbose=False
    )
    tiempo = time.time() - inicio
    
    # Timestamp de fin del proceso
    timestamp_fin = time.strftime('%H:%M:%S.%f')[:-3]
    print(f"✅ FIN: {timestamp_fin} - Config {configuracion['tamano_poblacion']}-{configuracion['num_generaciones']}-{configuracion['prob_cruce']:.1f}-{configuracion['prob_mutacion']:.2f} - Semilla {semilla} - Tiempo: {tiempo:.1f}s")
    
    # Convertir fitness a métricas reales
    metricas = [(1/f[0], 1/f[1]-1, 1/f[2]-1) for f in fitness_pareto]
    
    makespans = [m[0] for m in metricas]
    balances = [m[1] for m in metricas]
    energias = [m[2] for m in metricas]
    
    # Calcular métrica agregada normalizada (menor es mejor)
    # Los valores de referencia se leen desde config.yaml
    ref_mk = valores_ref['makespan']
    ref_bal = valores_ref['balance']
    ref_eng = valores_ref['energia']
    
    prom_mk = np.mean(makespans)
    prom_bal = np.mean(balances)
    prom_eng = np.mean(energias)
    
    score_agregado = (prom_mk / ref_mk) + (prom_bal / ref_bal) + (prom_eng / ref_eng)
    
    return {
        'configuracion': configuracion,
        'semilla': semilla,
        'makespan': prom_mk,
        'balance': prom_bal,
        'energia': prom_eng,
        'tiempo': tiempo,
        'tamano_frente': len(frente_pareto),
        'score_agregado': score_agregado
    }

def main():
    # Detectar capacidades del sistema
    nucleos_fisicos = psutil.cpu_count(logical=False)
    nucleos_logicos = psutil.cpu_count(logical=True)
    memoria_gb = psutil.virtual_memory().total / (1024**3)
    
    print(f"Sistema detectado:")
    print(f"   Núcleos físicos: {nucleos_fisicos}")
    print(f"   Núcleos lógicos: {nucleos_logicos}")
    print(f"   Memoria RAM: {memoria_gb:.1f} GB")
    
    # Usar 6 núcleos para prueba
    num_nucleos = 6
    print(f"\nUsando {num_nucleos} núcleos para paralelización (prueba)")
    
    # 3 combinaciones para prueba rápida (semisuma de las dos primeras)
    combinaciones = [
        {'tamano_poblacion': 100, 'num_generaciones': 400, 'prob_cruce': 0.8, 'prob_mutacion': 0.1, 'cada_k_gen': 5, 'max_iter_local': 3},
        {'tamano_poblacion': 200, 'num_generaciones': 600, 'prob_cruce': 0.9, 'prob_mutacion': 0.15, 'cada_k_gen': 10, 'max_iter_local': 5},
        # Semisuma: (100+200)/2=150, (400+600)/2=500, (0.8+0.9)/2=0.85, (0.1+0.15)/2=0.125, (5+10)/2=7.5, (3+5)/2=4
        {'tamano_poblacion': 150, 'num_generaciones': 500, 'prob_cruce': 0.85, 'prob_mutacion': 0.125, 'cada_k_gen': 7, 'max_iter_local': 4}
    ]
    
    # 4 semillas para prueba rápida (para ver comportamiento con 6 núcleos)
    num_semillas = 4
    
    print(f"\nTotal de combinaciones a evaluar: {len(combinaciones)}")
    print(f"Semillas por combinación: {num_semillas}")
    print(f"Total de ejecuciones: {len(combinaciones) * num_semillas}")
    print(f"Tiempo estimado: {len(combinaciones) * num_semillas * 2 / num_nucleos:.1f} minutos")
    
    print(f"\nIniciando optimización con {num_nucleos} núcleos...")
    inicio_total = time.time()
    
    # Crear todas las tareas (combinación, semilla)
    tareas = []
    for configuracion in combinaciones:
        for semilla in range(num_semillas):
            tareas.append((configuracion, semilla))
    
    print(f"Total de tareas: {len(tareas)}")
    print(f"Tareas por núcleo: {len(tareas) / num_nucleos:.1f}")
    print("Iniciando paralelización REAL...")
    print("Verificando uso de núcleos...")
    
    # Debug: Mostrar las tareas creadas
    print("\nTareas creadas:")
    for i, tarea in enumerate(tareas):
        config, semilla = tarea
        print(f"  Tarea {i+1}: Config {config['tamano_poblacion']}-{config['num_generaciones']}-{config['prob_cruce']:.1f}-{config['prob_mutacion']:.2f}, Semilla {semilla}")
    print()
    
    print(f"📊 ANÁLISIS DE PARALELIZACIÓN:")
    print(f"   Total tareas: {len(tareas)}")
    print(f"   Núcleos disponibles: {num_nucleos}")
    print(f"   Tareas por núcleo: {len(tareas) / num_nucleos:.1f}")
    print(f"   Si hay paralelización real: {len(tareas)} tareas deberían ejecutarse en ~{len(tareas) / num_nucleos:.1f} lotes")
    print()
    
    # Ejecutar optimización en paralelo REAL
    todos_resultados = []
    mejor_score = float('inf')
    mejor_config = None
    configuraciones_ya_guardadas = set()  # Para evitar guardar la misma configuración múltiples veces
    
    with ProcessPoolExecutor(max_workers=num_nucleos) as executor:
        print(f"🚀 INICIANDO {len(tareas)} TAREAS EN {num_nucleos} NÚCLEOS...")
        print(f"⏰ Timestamp inicio: {time.strftime('%H:%M:%S')}")
        print()
        
        # Enviar todas las tareas
        futures = []
        for tarea in tareas:
            futures.append(executor.submit(ejecutar_semilla, tarea))
        
        # Procesar resultados conforme se completan
        for i, future in enumerate(as_completed(futures)):
            try:
                resultado = future.result()
                todos_resultados.append(resultado)
                
                # Agrupar resultados por configuración
                config_key = tuple(sorted(resultado['configuracion'].items()))
                
                # Calcular promedio de la configuración actual
                config_resultados = [r for r in todos_resultados if tuple(sorted(r['configuracion'].items())) == config_key]
                if len(config_resultados) == num_semillas:
                    prom_score = np.mean([r['score_agregado'] for r in config_resultados])
                    if prom_score < mejor_score:
                        mejor_score = prom_score
                        mejor_config = resultado['configuracion']
                
                # Mostrar progreso detallado
                progreso = (i+1) / len(tareas) * 100
                tiempo_transcurrido = time.time() - inicio_total
                tiempo_por_ejecucion = tiempo_transcurrido / (i+1)
                tiempo_restante = tiempo_por_ejecucion * (len(tareas) - i-1)
                
                timestamp = time.strftime('%H:%M:%S')
                print(f"  [{progreso:5.1f}%] {i+1:2d}/{len(tareas)} - {timestamp} - "
                      f"Config: {resultado['configuracion']['tamano_poblacion']}-{resultado['configuracion']['num_generaciones']}-{resultado['configuracion']['prob_cruce']:.1f}-{resultado['configuracion']['prob_mutacion']:.2f} - "
                      f"Semilla: {resultado['semilla']:2d} - "
                      f"Score: {resultado['score_agregado']:.4f} - "
                      f"Mejor: {mejor_score:.4f} - "
                      f"ETA: {tiempo_restante/60:.1f}min")
                
                # Verificar si se completó alguna configuración
                configuraciones_completas = verificar_configuraciones_completas(todos_resultados, num_semillas)
                if configuraciones_completas:
                    # Verificar si hay configuraciones nuevas completadas
                    configuraciones_nuevas = []
                    for config in configuraciones_completas:
                        config_key = tuple(sorted(config.items()))
                        if config_key not in configuraciones_ya_guardadas:
                            configuraciones_nuevas.append(config)
                            configuraciones_ya_guardadas.add(config_key)
                    
                    if configuraciones_nuevas:
                        print(f"    Mejor config actual: {mejor_config}")
                        print(f"    ✅ Configuraciones completadas: {len(configuraciones_nuevas)}")
                        
                        # Guardar resultados parciales
                        guardar_resultados_parciales(todos_resultados, num_semillas)
                    
            except Exception as exc:
                print(f"  Generó una excepción: {exc}")
    
    tiempo_total = time.time() - inicio_total
    print(f"\nOptimización completada en {tiempo_total:.1f} segundos")
    
    # Analizar resultados
    print("\n" + "="*70)
    print("RESULTADOS DE LA PRUEBA")
    print("="*70)
    
    # Agrupar resultados por configuración
    resultados_por_config = {}
    for resultado in todos_resultados:
        config_key = tuple(sorted(resultado['configuracion'].items()))
        if config_key not in resultados_por_config:
            resultados_por_config[config_key] = []
        resultados_por_config[config_key].append(resultado)
    
    # Calcular promedios por configuración
    configuraciones_analizadas = []
    for config_key, resultados in resultados_por_config.items():
        if len(resultados) == num_semillas:  # Solo configuraciones completas
            configuracion = dict(config_key)
            prom_score = np.mean([r['score_agregado'] for r in resultados])
            prom_makespan = np.mean([r['makespan'] for r in resultados])
            prom_balance = np.mean([r['balance'] for r in resultados])
            prom_energia = np.mean([r['energia'] for r in resultados])
            prom_tiempo = np.mean([r['tiempo'] for r in resultados])
            prom_tamano_frente = np.mean([r['tamano_frente'] for r in resultados])
            
            configuraciones_analizadas.append({
                'configuracion': configuracion,
                'prom_score': prom_score,
                'prom_makespan': prom_makespan,
                'prom_balance': prom_balance,
                'prom_energia': prom_energia,
                'prom_tiempo': prom_tiempo,
                'prom_tamano_frente': prom_tamano_frente
            })
    
    # Ordenar por score agregado (menor es mejor)
    configuraciones_analizadas.sort(key=lambda x: x['prom_score'])
    
    print("\nResultados:")
    print(f"{'Rank':<4} {'Pob':<4} {'Gen':<4} {'PC':<5} {'PM':<5} {'K':<3} {'IL':<3} "
          f"{'Score':<8} {'MK':<8} {'Bal':<8} {'Eng':<8} {'Tiempo':<8}")
    print("-"*90)
    
    for i, res in enumerate(configuraciones_analizadas, 1):
        print(f"{i:<4} {res['configuracion']['tamano_poblacion']:<4} "
              f"{res['configuracion']['num_generaciones']:<4} "
              f"{res['configuracion']['prob_cruce']:<5.2f} "
              f"{res['configuracion']['prob_mutacion']:<5.2f} "
              f"{res['configuracion']['cada_k_gen']:<3} "
              f"{res['configuracion']['max_iter_local']:<3} "
              f"{res['prom_score']:<8.4f} {res['prom_makespan']:<8.2f} "
              f"{res['prom_balance']:<8.2f} {res['prom_energia']:<8.2f} "
              f"{res['prom_tiempo']:<8.2f}")
    
    # Mejor configuración
    if configuraciones_analizadas:
        mejor = configuraciones_analizadas[0]
        print(f"\n" + "="*70)
        print("MEJOR CONFIGURACIÓN ENCONTRADA")
        print("="*70)
        print(f"Población: {mejor['configuracion']['tamano_poblacion']}")
        print(f"Generaciones: {mejor['configuracion']['num_generaciones']}")
        print(f"Prob. cruce: {mejor['configuracion']['prob_cruce']}")
        print(f"Prob. mutación: {mejor['configuracion']['prob_mutacion']}")
        print(f"Búsqueda local cada: {mejor['configuracion']['cada_k_gen']} gen")
        print(f"Iteraciones locales: {mejor['configuracion']['max_iter_local']}")
        print(f"\nMétricas promedio:")
        print(f"   Score agregado: {mejor['prom_score']:.4f}")
        print(f"   Makespan: {mejor['prom_makespan']:.2f}s")
        print(f"   Balance: {mejor['prom_balance']:.2f}")
        print(f"   Energía: {mejor['prom_energia']:.2f} kWh")
        print(f"   Tiempo: {mejor['prom_tiempo']:.2f}s")
    
    print(f"\nPrueba completada exitosamente!")
    print("="*70)

if __name__ == "__main__":
    main()
