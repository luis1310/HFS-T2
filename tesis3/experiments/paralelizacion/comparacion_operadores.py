"""Comparación de operadores con paralelización REAL de semillas"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tesis3.src.core.problem import ProblemConfig
from tesis3.src.algorithms.nsga2_memetic import nsga2_memetic
from tesis3.src.operators.crossover import aplicar_cruce
from tesis3.src.operators.mutation import aplicar_mutacion
import numpy as np
import time
import csv
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import psutil

print("="*70)
print("COMPARACIÓN DE OPERADORES - PARALELIZACIÓN REAL")
print("="*70)

# Configuración del problema
config = ProblemConfig.from_yaml("tesis3/config/config.yaml")

def cruce_uniforme(p1, p2, cfg, prob):
    return aplicar_cruce(p1, p2, cfg, metodo='uniforme', prob_cruce=prob)

def cruce_un_punto(p1, p2, cfg, prob):
    return aplicar_cruce(p1, p2, cfg, metodo='un_punto', prob_cruce=prob)

def mutacion_swap(pob, cfg, prob):
    return aplicar_mutacion(pob, cfg, metodo='swap', tasa_mut=prob)

def mutacion_insert(pob, cfg, prob):
    return aplicar_mutacion(pob, cfg, metodo='insert', tasa_mut=prob)

def mutacion_invert(pob, cfg, prob):
    return aplicar_mutacion(pob, cfg, metodo='invert', tasa_mut=prob)

def guardar_resultados_parciales(todos_resultados, num_semillas):
    """Guarda resultados parciales cada vez que se completa una configuración"""
    # Agrupar resultados por configuración
    resultados_agrupados = {}
    for res in todos_resultados:
        config_key = res['configuracion']['nombre']
        if config_key not in resultados_agrupados:
            resultados_agrupados[config_key] = []
        resultados_agrupados[config_key].append(res)
    
    # Calcular promedios solo para configuraciones completas
    configuraciones_completas = []
    for config_key, res_list in resultados_agrupados.items():
        if len(res_list) == num_semillas:  # Solo configuraciones completas
            avg_mk = np.mean([r['makespan'] for r in res_list])
            avg_bal = np.mean([r['balance'] for r in res_list])
            avg_eng = np.mean([r['energia'] for r in res_list])
            avg_time = np.mean([r['tiempo'] for r in res_list])
            avg_score = np.mean([r['score_agregado'] for r in res_list])
            
            configuraciones_completas.append({
                'configuracion_nombre': config_key,
                'cruce': res_list[0]['configuracion']['cruce'],
                'mutacion': res_list[0]['configuracion']['mutacion'],
                'prom_makespan': avg_mk,
                'prom_balance': avg_bal,
                'prom_energia': avg_eng,
                'prom_tiempo': avg_time,
                'prom_score': avg_score
            })
    
    # Guardar en CSV con timestamp
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    output_file = f'tesis3/results/comparacion_operadores_parcial_{timestamp}.csv'
    with open(output_file, 'w', newline='') as f:
        fieldnames = ['configuracion_nombre', 'cruce', 'mutacion',
                      'prom_makespan', 'prom_balance', 'prom_energia',
                      'prom_tiempo', 'prom_score']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for res in configuraciones_completas:
            writer.writerow(res)
    
    print(f"    💾 Resultados parciales guardados: {len(configuraciones_completas)} configuraciones completas")

def verificar_configuraciones_completas(todos_resultados, num_semillas):
    """Verifica qué configuraciones están completas (tienen todas sus semillas)"""
    # Agrupar resultados por configuración
    resultados_agrupados = {}
    for res in todos_resultados:
        config_key = res['configuracion']['nombre']
        if config_key not in resultados_agrupados:
            resultados_agrupados[config_key] = []
        resultados_agrupados[config_key].append(res)
    
    # Identificar configuraciones completas
    configuraciones_completas = []
    for config_key, res_list in resultados_agrupados.items():
        if len(res_list) == num_semillas:  # Configuración completa
            configuraciones_completas.append(config_key)
    
    return configuraciones_completas

def ejecutar_semilla_operador(args):
    """Ejecuta una semilla específica para una configuración de operadores"""
    configuracion, semilla = args
    
    # Timestamp de inicio del proceso
    timestamp_inicio = time.strftime('%H:%M:%S.%f')[:-3]  # Incluir milisegundos
    print(f"🚀 INICIO: {timestamp_inicio} - Config {configuracion['nombre']} - Semilla {semilla}")
    
    # Configurar semilla para reproducibilidad
    np.random.seed(semilla)
    
    # Seleccionar operadores
    if configuracion['cruce'] == 'uniforme':
        cruce_func = cruce_uniforme
    else:  # un_punto
        cruce_func = cruce_un_punto
    
    if configuracion['mutacion'] == 'swap':
        mutacion_func = mutacion_swap
    elif configuracion['mutacion'] == 'insert':
        mutacion_func = mutacion_insert
    else:  # invert
        mutacion_func = mutacion_invert
    
    inicio = time.time()
    frente_pareto, fitness_pareto, _ = nsga2_memetic(
        config, cruce_func, mutacion_func,
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
    print(f"✅ FIN: {timestamp_fin} - Config {configuracion['nombre']} - Semilla {semilla} - Tiempo: {tiempo:.1f}s")
    
    # Convertir fitness a métricas reales
    metricas = [(1/f[0], 1/f[1]-1, 1/f[2]-1) for f in fitness_pareto]
    
    makespans = [m[0] for m in metricas]
    balances = [m[1] for m in metricas]
    energias = [m[2] for m in metricas]
    
    # Calcular métrica agregada normalizada (menor es mejor)
    ref_mk = 2000  # Makespan máximo esperado
    ref_bal = 300  # Balance máximo esperado
    ref_eng = 700  # Energía máxima esperada
    
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

def detectar_capacidades_sistema():
    """Detecta núcleos físicos y lógicos del sistema"""
    nucleos_fisicos = psutil.cpu_count(logical=False)
    nucleos_logicos = psutil.cpu_count(logical=True)
    memoria_gb = psutil.virtual_memory().total / (1024**3)
    
    print(f"Sistema detectado:")
    print(f"   Núcleos físicos: {nucleos_fisicos}")
    print(f"   Núcleos lógicos: {nucleos_logicos}")
    print(f"   Memoria RAM: {memoria_gb:.1f} GB")
    
    return nucleos_fisicos, nucleos_logicos, memoria_gb

def main():
    # Detectar capacidades del sistema
    nucleos_fisicos, nucleos_logicos, memoria_gb = detectar_capacidades_sistema()
    
    print("\nSeleccione cuántos núcleos usar para la paralelización:")
    print(f"1. Núcleos físicos ({nucleos_fisicos}) - Recomendado")
    print(f"2. Núcleos lógicos ({nucleos_logicos}) - Máximo rendimiento")
    print(f"3. Seguro (6 núcleos) - Para evitar sobrecalentamiento")
    print(f"4. Personalizado")
    
    while True:
        try:
            opcion = input("Ingrese opción (1-4): ").strip()
            if opcion == "1":
                num_nucleos = nucleos_fisicos
                break
            elif opcion == "2":
                num_nucleos = nucleos_logicos
                break
            elif opcion == "3":
                num_nucleos = min(6, nucleos_fisicos)  # Máximo 6 núcleos para seguridad
                print(f"Usando {num_nucleos} núcleos para evitar sobrecalentamiento")
                break
            elif opcion == "4":
                num_nucleos = int(input(f"Ingrese número de núcleos (1-{nucleos_logicos}): "))
                if 1 <= num_nucleos <= nucleos_logicos:
                    break
                else:
                    print("Número inválido")
            else:
                print("Opción inválida")
        except ValueError:
            print("Ingrese un número válido")
    
    print(f"\nUsando {num_nucleos} núcleos para paralelización")
    
    # Configuraciones de operadores a comparar
    configuraciones_operadores = [
        {'cruce': 'uniforme', 'mutacion': 'swap', 'nombre': 'Uniforme + Swap'},
        {'cruce': 'uniforme', 'mutacion': 'insert', 'nombre': 'Uniforme + Insert'},
        {'cruce': 'uniforme', 'mutacion': 'invert', 'nombre': 'Uniforme + Invert'},
        {'cruce': 'un_punto', 'mutacion': 'swap', 'nombre': '1-Punto + Swap'},
        {'cruce': 'un_punto', 'mutacion': 'insert', 'nombre': '1-Punto + Insert'},
        {'cruce': 'un_punto', 'mutacion': 'invert', 'nombre': '1-Punto + Invert'},
    ]
    
    # Parámetros fijos del algoritmo
    parametros_algoritmo = {
        'tamano_poblacion': 100,
        'num_generaciones': 400,
        'prob_cruce': 0.8,
        'prob_mutacion': 0.1,
        'cada_k_gen': 10,
        'max_iter_local': 5
    }
    
    # Número de semillas por configuración
    num_semillas = 30
    
    print(f"\nTotal de configuraciones a evaluar: {len(configuraciones_operadores)}")
    print(f"Semillas por configuración: {num_semillas}")
    print(f"Total de ejecuciones: {len(configuraciones_operadores) * num_semillas}")
    print(f"Tiempo estimado: {len(configuraciones_operadores) * num_semillas * 2 / num_nucleos / 60:.1f} horas")
    
    # Confirmar ejecución
    confirmar = input("\n¿Continuar con la comparación? (s/n): ").lower()
    if confirmar != 's':
        print("Comparación cancelada")
        return
    
    print(f"\nIniciando comparación con {num_nucleos} núcleos...")
    inicio_total = time.time()
    
    # Crear todas las tareas (configuración, semilla)
    tareas = []
    for configuracion in configuraciones_operadores:
        configuracion_completa = {**parametros_algoritmo, **configuracion}
        for semilla in range(num_semillas):
            tareas.append((configuracion_completa, semilla))
    
    print(f"Total de tareas: {len(tareas)}")
    print("Iniciando paralelización REAL...")
    
    # Ejecutar comparación en paralelo REAL
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
            futures.append(executor.submit(ejecutar_semilla_operador, tarea))
        
        # Procesar resultados conforme se completan
        for i, future in enumerate(as_completed(futures)):
            try:
                resultado = future.result()
                todos_resultados.append(resultado)
                
                # Agrupar resultados por configuración
                config_key = resultado['configuracion']['nombre']
                
                # Calcular promedio de la configuración actual
                config_resultados = [r for r in todos_resultados if r['configuracion']['nombre'] == config_key]
                if len(config_resultados) == num_semillas:
                    prom_score = np.mean([r['score_agregado'] for r in config_resultados])
                    if prom_score < mejor_score:
                        mejor_score = prom_score
                        mejor_config = resultado['configuracion']['nombre']
                
                # Mostrar progreso detallado
                progreso = (i+1) / len(tareas) * 100
                tiempo_transcurrido = time.time() - inicio_total
                tiempo_por_ejecucion = tiempo_transcurrido / (i+1)
                tiempo_restante = tiempo_por_ejecucion * (len(tareas) - i-1)
                
                timestamp = time.strftime('%H:%M:%S')
                print(f"  [{progreso:5.1f}%] {i+1:4d}/{len(tareas)} - {timestamp} - "
                      f"Config: {resultado['configuracion']['nombre']:<20} - "
                      f"Semilla: {resultado['semilla']:2d} - "
                      f"Score: {resultado['score_agregado']:.4f} - "
                      f"Mejor: {mejor_score:.4f} - "
                      f"ETA: {tiempo_restante/60:.1f}min")
                
                # Verificar si se completó alguna configuración
                configuraciones_completas = verificar_configuraciones_completas(todos_resultados, 30)
                if configuraciones_completas:
                    # Verificar si hay configuraciones nuevas completadas
                    configuraciones_nuevas = []
                    for config in configuraciones_completas:
                        if config not in configuraciones_ya_guardadas:
                            configuraciones_nuevas.append(config)
                            configuraciones_ya_guardadas.add(config)
                    
                    if configuraciones_nuevas:
                        print(f"    Mejor config actual: {mejor_config}")
                        print(f"    ✅ Configuraciones completadas: {len(configuraciones_nuevas)}")
                        
                        # Guardar resultados parciales
                        guardar_resultados_parciales(todos_resultados, 30)
                    
            except Exception as exc:
                print(f"  Generó una excepción: {exc}")
    
    tiempo_total = time.time() - inicio_total
    print(f"\nComparación completada en {tiempo_total:.1f} segundos")
    
    # Analizar resultados
    print("\n" + "="*70)
    print("ANÁLISIS DE RESULTADOS")
    print("="*70)
    
    # Agrupar resultados por configuración
    resultados_por_config = {}
    for resultado in todos_resultados:
        config_key = resultado['configuracion']['nombre']
        if config_key not in resultados_por_config:
            resultados_por_config[config_key] = []
        resultados_por_config[config_key].append(resultado)
    
    # Calcular promedios por configuración
    configuraciones_analizadas = []
    for config_key, resultados in resultados_por_config.items():
        if len(resultados) == num_semillas:  # Solo configuraciones completas
            prom_score = np.mean([r['score_agregado'] for r in resultados])
            std_score = np.std([r['score_agregado'] for r in resultados])
            prom_makespan = np.mean([r['makespan'] for r in resultados])
            std_makespan = np.std([r['makespan'] for r in resultados])
            prom_balance = np.mean([r['balance'] for r in resultados])
            std_balance = np.std([r['balance'] for r in resultados])
            prom_energia = np.mean([r['energia'] for r in resultados])
            std_energia = np.std([r['energia'] for r in resultados])
            prom_tiempo = np.mean([r['tiempo'] for r in resultados])
            prom_tamano_frente = np.mean([r['tamano_frente'] for r in resultados])
            
            configuraciones_analizadas.append({
                'configuracion': config_key,
                'prom_score': prom_score,
                'std_score': std_score,
                'prom_makespan': prom_makespan,
                'std_makespan': std_makespan,
                'prom_balance': prom_balance,
                'std_balance': std_balance,
                'prom_energia': prom_energia,
                'std_energia': std_energia,
                'prom_tiempo': prom_tiempo,
                'prom_tamano_frente': prom_tamano_frente
            })
    
    # Ordenar por score agregado (menor es mejor)
    configuraciones_analizadas.sort(key=lambda x: x['prom_score'])
    
    print("\nRanking de configuraciones (promedio de {} semillas):".format(num_semillas))
    print(f"{'Rank':<4} {'Configuración':<20} {'Score':<8} {'MK':<8} {'Bal':<8} {'Eng':<8} {'Tiempo':<8}")
    print("-"*80)
    
    for i, res in enumerate(configuraciones_analizadas, 1):
        print(f"{i:<4} {res['configuracion']:<20} {res['prom_score']:<8.4f} "
              f"{res['prom_makespan']:<8.2f} {res['prom_balance']:<8.2f} "
              f"{res['prom_energia']:<8.2f} {res['prom_tiempo']:<8.2f}")
    
    # Mejor configuración
    if configuraciones_analizadas:
        mejor = configuraciones_analizadas[0]
        print(f"\n" + "="*70)
        print("MEJOR CONFIGURACIÓN ENCONTRADA")
        print("="*70)
        print(f"Configuración: {mejor['configuracion']}")
        print(f"Score agregado: {mejor['prom_score']:.4f} ± {mejor['std_score']:.4f}")
        print(f"Makespan: {mejor['prom_makespan']:.2f} ± {mejor['std_makespan']:.2f}")
        print(f"Balance: {mejor['prom_balance']:.2f} ± {mejor['std_balance']:.2f}")
        print(f"Energía: {mejor['prom_energia']:.2f} ± {mejor['std_energia']:.2f}")
        print(f"Tiempo: {mejor['prom_tiempo']:.2f}s")
    
    # Guardar resultados
    timestamp_final = time.strftime('%Y%m%d_%H%M%S')
    with open(f'tesis3/results/comparacion_operadores_real_{timestamp_final}.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'configuracion', 'cruce', 'mutacion', 'semilla', 'makespan', 'balance',
            'energia', 'tamano_frente', 'score_agregado', 'tiempo'
        ])
        writer.writeheader()
        for resultado in todos_resultados:
            row = {
                'configuracion': resultado['configuracion']['nombre'],
                'cruce': resultado['configuracion']['cruce'],
                'mutacion': resultado['configuracion']['mutacion'],
                'semilla': resultado['semilla'],
                'makespan': resultado['makespan'],
                'balance': resultado['balance'],
                'energia': resultado['energia'],
                'tamano_frente': resultado['tamano_frente'],
                'score_agregado': resultado['score_agregado'],
                'tiempo': resultado['tiempo']
            }
            writer.writerow(row)
    
    print(f"\nResultados guardados en: tesis3/results/comparacion_operadores_real_{timestamp_final}.csv")
    print("="*70)

if __name__ == "__main__":
    main()
