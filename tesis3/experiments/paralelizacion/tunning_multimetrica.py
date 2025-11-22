"""Tunning multimétrica con paralelización REAL de semillas"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tesis3.src.core.problem import ProblemConfig
from tesis3.src.algorithms.nsga2_memetic import nsga2_memetic
from tesis3.src.operators.crossover import aplicar_cruce
from tesis3.src.operators.mutation import aplicar_mutacion
from tesis3.src.utils.seeds import cargar_semillas
import numpy as np
import random
import time
import csv
from itertools import product
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import psutil
import glob
import os
import yaml

print("="*70)
print("TUNNING MULTIMÉTRICA - PARALELIZACIÓN REAL")
print("="*70)

# Configuración del problema
config = ProblemConfig.from_yaml("tesis3/config/config.yaml")

# Cargar valores de referencia para el score agregado
with open("tesis3/config/config.yaml", 'r') as f:
    config_completa = yaml.safe_load(f)
valores_ref = config_completa['experiments']['valores_referencia']

def cruce(p1, p2, cfg, prob):
    return aplicar_cruce(p1, p2, cfg, metodo='uniforme', prob_cruce=prob)

def mutacion(pob, cfg, prob):
    return aplicar_mutacion(pob, cfg, metodo='invert', tasa_mut=prob)

def detectar_resultados_previos(num_semillas=30, semillas_esperadas=None):
    """Detecta y carga resultados de ejecuciones previas
    
    Verifica que cada configuración tenga exactamente las semillas esperadas
    para asegurar que siempre se usan las mismas semillas.
    
    Args:
        num_semillas: Número de semillas esperadas (para compatibilidad)
        semillas_esperadas: Lista de semillas esperadas. Si es None, usa range(num_semillas)
    """
    print("🔍 Detectando resultados previos...")
    
    # Si no se proporcionan semillas específicas, usar range()
    if semillas_esperadas is None:
        semillas_esperadas = list(range(num_semillas))
    
    # Buscar archivo parcial (ahora es uno solo, sin timestamp)
    archivo_parcial = 'tesis3/results/tunning_multimetrica_parcial.csv'
    archivos_finales = glob.glob('tesis3/results/tunning_multimetrica_real_*.csv')
    
    existe_parcial = os.path.exists(archivo_parcial)
    print(f"   Archivo parcial existente: {'Sí' if existe_parcial else 'No'}")
    print(f"   Archivos finales encontrados: {len(archivos_finales)}")
    
    # Cargar todos los resultados previos
    resultados_por_config = {}  # {config_key: set(semillas)}
    
    # 🔄 NUEVO: Cargar primero desde archivo parcial si existe (protección contra interrupciones)
    if existe_parcial:
        try:
            print(f"   [RECUPERACIÓN] Cargando configuraciones del archivo parcial...")
            with open(archivo_parcial, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # El archivo parcial tiene configuraciones COMPLETAS (30 semillas)
                    config_key = (
                        ('tamano_poblacion', int(row['tamano_poblacion'])),
                        ('num_generaciones', int(row['num_generaciones'])),
                        ('prob_cruce', float(row['prob_cruce'])),
                        ('prob_mutacion', float(row['prob_mutacion'])),
                        ('cada_k_gen', int(row['cada_k_gen'])),
                        ('max_iter_local', int(row['max_iter_local']))
                    )
                    # Marcar como completa (tiene todas las semillas esperadas)
                    if config_key not in resultados_por_config:
                        resultados_por_config[config_key] = set(semillas_esperadas)
            print(f"   [RECUPERACIÓN] Configuraciones recuperadas del parcial: {len(resultados_por_config)}")
        except Exception as e:
            print(f"   [ADVERTENCIA] Error al cargar archivo parcial: {e}")
    
    # Cargar desde archivos finales (estos tienen semillas individuales y sobreescriben el parcial)
    for archivo in archivos_finales:
        try:
            with open(archivo, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    configuracion = {
                        'tamano_poblacion': int(row['tamano_poblacion']),
                        'num_generaciones': int(row['num_generaciones']),
                        'prob_cruce': float(row['prob_cruce']),
                        'prob_mutacion': float(row['prob_mutacion']),
                        'cada_k_gen': int(row['cada_k_gen']),
                        'max_iter_local': int(row['max_iter_local'])
                    }
                    semilla = int(row['semilla'])
                    config_key = tuple(sorted(configuracion.items()))
                    
                    if config_key not in resultados_por_config:
                        resultados_por_config[config_key] = set()
                    resultados_por_config[config_key].add(semilla)
        except Exception as e:
            print(f"   Error leyendo {archivo}: {e}")
    
    # Cargar desde archivo parcial (ahora es uno solo)
    # El archivo parcial contiene solo configuraciones completas (30/30 semillas)
    if existe_parcial:
        try:
            with open(archivo_parcial, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    configuracion = {
                        'tamano_poblacion': int(row['tamano_poblacion']),
                        'num_generaciones': int(row['num_generaciones']),
                        'prob_cruce': float(row['prob_cruce']),
                        'prob_mutacion': float(row['prob_mutacion']),
                        'cada_k_gen': int(row['cada_k_gen']),
                        'max_iter_local': int(row['max_iter_local'])
                    }
                    config_key = tuple(sorted(configuracion.items()))
                    # Si está en parcial, asumimos que tiene todas las semillas (se guarda solo cuando está completa)
                    if config_key not in resultados_por_config:
                        resultados_por_config[config_key] = set(semillas_esperadas)
        except Exception as e:
            print(f"   Error leyendo archivo parcial: {e}")
    
    # Verificar configuraciones completas: deben tener exactamente las semillas esperadas
    semillas_esperadas_set = set(semillas_esperadas)
    configuraciones_completas_previas = set()
    
    for config_key, semillas_encontradas in resultados_por_config.items():
        if semillas_encontradas == semillas_esperadas_set:
            configuraciones_completas_previas.add(config_key)
            config_dict = dict(config_key)
            print(f"   [OK] Configuración completa detectada: {config_dict} (semillas {min(semillas_esperadas)}-{max(semillas_esperadas)} verificadas)")
        elif len(semillas_encontradas) > 0:
            faltantes = semillas_esperadas_set - semillas_encontradas
            config_dict = dict(config_key)
            print(f"   [PARCIAL] Configuración parcial: {config_dict} - Semillas faltantes: {sorted(faltantes)} ({len(faltantes)} faltantes)")
    
    print(f"   Total configuraciones completas previas: {len(configuraciones_completas_previas)}")
    return configuraciones_completas_previas

def guardar_resultados_parciales(todos_resultados, num_semillas):
    """
    Guarda resultados parciales en UN SOLO archivo que se actualiza constantemente.
    Esto evita generar cientos de archivos CSV durante la ejecución.
    """
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
    
    # Guardar en UN SOLO archivo sin timestamp (se sobrescribe constantemente)
    output_file = 'tesis3/results/tunning_multimetrica_parcial.csv'
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
    
    print(f"    [GUARDADO] Progreso guardado: {len(configuraciones_completas)} configuraciones completas")

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
    """Ejecuta una semilla específica para una configuración"""
    configuracion, semilla = args
    
    # Timestamp de inicio del proceso
    timestamp_inicio = time.strftime('%H:%M:%S.%f')[:-3]  # Incluir milisegundos
    print(f"INICIO: {timestamp_inicio} - Config {configuracion['tamano_poblacion']}-{configuracion['num_generaciones']}-{configuracion['prob_cruce']:.1f}-{configuracion['prob_mutacion']:.2f} - Semilla {semilla}")
    
    # Configurar semilla para reproducibilidad
    # IMPORTANTE: Inicializar ambos generadores aleatorios (Python y NumPy)
    # para garantizar reproducibilidad completa
    import random
    random.seed(semilla)
    np.random.seed(semilla)
    
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
    print(f"FIN: {timestamp_fin} - Config {configuracion['tamano_poblacion']}-{configuracion['num_generaciones']}-{configuracion['prob_cruce']:.1f}-{configuracion['prob_mutacion']:.2f} - Semilla {semilla} - Tiempo: {tiempo:.1f}s")
    
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
    
    # Definir espacio de búsqueda de hiperparámetros
    espacio_busqueda = {
        'tamano_poblacion': [100, 150, 200],        # 3 valores
        'num_generaciones': [400, 500, 600],        # 3 valores
        'prob_cruce': [0.6, 0.7, 0.8, 0.9, 0.95],              # 5 valores
        'prob_mutacion': [0.5, 0.75, 0.1, 0.15, 0.20, 0.25, 0.30],        # 7 valores
        'cada_k_gen': [5, 10, 20],                      # 3 valores
        'max_iter_local': [3, 5]                    # 2 valores
    }

    # Generar todas las combinaciones
    combinaciones = list(product(*espacio_busqueda.values()))
    combinaciones = [dict(zip(espacio_busqueda.keys(), combo)) for combo in combinaciones]
    
    # Cargar semillas centralizadas desde archivo de configuración
    try:
        semillas = cargar_semillas(tipo="estandar")
        num_semillas = len(semillas)
        print(f"\n[OK] Semillas cargadas desde archivo centralizado: {num_semillas} semillas")
        print(f"   Semillas a usar: {semillas}")
    except (FileNotFoundError, KeyError) as e:
        print(f"\n[ADVERTENCIA] No se pudo cargar semillas centralizadas: {e}")
        print(f"   Usando semillas estándar (0-29)")
        semillas = list(range(30))
        num_semillas = 30
    
    print(f"\nTotal de combinaciones a evaluar: {len(combinaciones)}")
    print(f"Semillas por combinación: {num_semillas}")
    print(f"Total de ejecuciones: {len(combinaciones) * num_semillas}")
    
    # 🔍 DETECTAR RESULTADOS PREVIOS
    configuraciones_completas_previas = detectar_resultados_previos(num_semillas, semillas_esperadas=semillas)
    
    # Filtrar configuraciones que ya están completas
    combinaciones_faltantes = []
    for combo in combinaciones:
        config_key = tuple(sorted(combo.items()))
        if config_key not in configuraciones_completas_previas:
            combinaciones_faltantes.append(combo)
    
    print(f"\nRESUMEN:")
    print(f"   Configuraciones totales: {len(combinaciones)}")
    print(f"   Configuraciones completas previas: {len(configuraciones_completas_previas)}")
    print(f"   Configuraciones faltantes: {len(combinaciones_faltantes)}")
    
    # Variable para indicar si todo está completo
    todo_completo = (len(combinaciones_faltantes) == 0)
    
    if todo_completo:
        print("🎉 ¡Todas las configuraciones ya están completas!")
        print("   No hay trabajo pendiente.")
        print("   Sin embargo, se generará el YAML con la mejor configuración global...")
        # Inicializar todos_resultados vacío (solo usaremos archivos previos)
        todos_resultados = []
    
    # Solo ejecutar si hay configuraciones faltantes
    if not todo_completo:
        print(f"Tiempo estimado restante: {len(combinaciones_faltantes) * num_semillas * 2 / num_nucleos / 60:.1f} horas")
        
        # Confirmar ejecución
        confirmar = input(f"\n¿Continuar con las {len(combinaciones_faltantes)} configuraciones faltantes? (s/n): ").lower()
        if confirmar != 's':
            print("Optimización cancelada")
            return
        
        print(f"\nIniciando optimización con {num_nucleos} núcleos...")
        inicio_total = time.time()
        
        # Crear todas las tareas (combinación, semilla) SOLO para las faltantes
        # Usar las semillas cargadas desde el archivo centralizado
        tareas = []
        for configuracion in combinaciones_faltantes:
            for semilla in semillas:  # Usar semillas del archivo, no range()
                tareas.append((configuracion, semilla))
        
        print(f"Total de tareas pendientes: {len(tareas)}")
        print("Iniciando paralelización REAL...")
        
        # 🔄 CARGAR RESULTADOS DEL ARCHIVO PARCIAL (si existe)
    else:
        # Si todo está completo, inicializar inicio_total para el mensaje de tiempo
        inicio_total = time.time()
    # Esto garantiza que si hubo una interrupción, esos resultados se incluyan en el archivo final
    todos_resultados = []
    archivo_parcial = 'tesis3/results/tunning_multimetrica_parcial.csv'
    if os.path.exists(archivo_parcial):
        print(f"\n[RECUPERACIÓN] Cargando resultados previos del archivo parcial...")
        try:
            with open(archivo_parcial, 'r') as f:
                reader = csv.DictReader(f)
                configs_recuperadas = 0
                for row in reader:
                    # Cargar cada configuración × semilla del archivo parcial
                    # Necesitamos expandir cada config a sus 30 semillas
                    config = {
                        'tamano_poblacion': int(row['tamano_poblacion']),
                        'num_generaciones': int(row['num_generaciones']),
                        'prob_cruce': float(row['prob_cruce']),
                        'prob_mutacion': float(row['prob_mutacion']),
                        'cada_k_gen': int(row['cada_k_gen']),
                        'max_iter_local': int(row['max_iter_local'])
                    }
                    configs_recuperadas += 1
                # El archivo parcial tiene promedios, no semillas individuales
                # Por lo tanto, necesitamos leer desde archivos *_real_*.csv para recuperar las individuales
            print(f"[ADVERTENCIA] Archivo parcial contiene configuraciones agregadas (sin semillas individuales)")
            print(f"[INFO] Los resultados completos se recuperarán desde archivos finales previos")
            
            # Cargar resultados individuales desde archivos finales previos
            archivos_finales_previos = glob.glob('tesis3/results/tunning_multimetrica_real_*.csv')
            for archivo in archivos_finales_previos:
                with open(archivo, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        resultado = {
                            'configuracion': {
                                'tamano_poblacion': int(row['tamano_poblacion']),
                                'num_generaciones': int(row['num_generaciones']),
                                'prob_cruce': float(row['prob_cruce']),
                                'prob_mutacion': float(row['prob_mutacion']),
                                'cada_k_gen': int(row['cada_k_gen']),
                                'max_iter_local': int(row['max_iter_local'])
                            },
                            'semilla': int(row['semilla']),
                            'makespan': float(row['makespan']),
                            'balance': float(row['balance']),
                            'energia': float(row['energia']),
                            'tiempo': float(row['tiempo']),
                            'tamano_frente': int(row['tamano_frente']),
                            'score_agregado': float(row['score_agregado'])
                        }
                        # Solo agregar si esta configuración NO se va a ejecutar de nuevo
                        config_key = tuple(sorted(resultado['configuracion'].items()))
                        if config_key in configuraciones_completas_previas:
                            todos_resultados.append(resultado)
            print(f"[RECUPERACIÓN] Resultados previos cargados: {len(todos_resultados)} ejecuciones")
        except Exception as e:
            print(f"[ADVERTENCIA] Error al cargar archivo parcial: {e}")
            todos_resultados = []
    
    mejor_score = float('inf')
    mejor_config = None
    configuraciones_ya_guardadas = set()  # Para evitar guardar la misma configuración múltiples veces
    
    with ProcessPoolExecutor(max_workers=num_nucleos) as executor:
        print(f"INICIANDO {len(tareas)} TAREAS EN {num_nucleos} NÚCLEOS...")
        print(f"Timestamp inicio: {time.strftime('%H:%M:%S')}")
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
                print(f"  [{progreso:5.1f}%] {i+1:4d}/{len(tareas)} - {timestamp} - "
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
                        print(f"    Configuraciones completadas: {len(configuraciones_nuevas)}")
                        
                        # Guardar resultados parciales
                        guardar_resultados_parciales(todos_resultados, num_semillas)
                    
            except Exception as exc:
                print(f"  Generó una excepción: {exc}")
        
        tiempo_total = time.time() - inicio_total
        print(f"\nOptimización completada en {tiempo_total:.1f} segundos")
    
    # 📊 CARGAR TODOS LOS RESULTADOS PREVIOS PARA ANÁLISIS GLOBAL
    # (Esto se ejecuta siempre, incluso si todo estaba completo)
    print("\n" + "="*70)
    print("CARGANDO RESULTADOS DE TODAS LAS EJECUCIONES")
    print("="*70)
    
    # Buscar todos los archivos CSV finales previos
    archivos_finales_previos = glob.glob('tesis3/results/tunning_multimetrica_real_*.csv')
    print(f"   Archivos finales encontrados: {len(archivos_finales_previos)}")
    
    # Combinar resultados actuales con todos los previos
    todos_resultados_global = todos_resultados.copy()  # Empezar con la ejecución actual
    
    # Cargar resultados de archivos previos
    for archivo in archivos_finales_previos:
        try:
            with open(archivo, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Reconstruir resultado desde CSV
                    resultado_previo = {
                        'configuracion': {
                            'tamano_poblacion': int(row['tamano_poblacion']),
                            'num_generaciones': int(row['num_generaciones']),
                            'prob_cruce': float(row['prob_cruce']),
                            'prob_mutacion': float(row['prob_mutacion']),
                            'cada_k_gen': int(row['cada_k_gen']),
                            'max_iter_local': int(row['max_iter_local'])
                        },
                        'semilla': int(row['semilla']),
                        'makespan': float(row['makespan']),
                        'balance': float(row['balance']),
                        'energia': float(row['energia']),
                        'tiempo': float(row['tiempo']),
                        'tamano_frente': int(row['tamano_frente']),
                        'score_agregado': float(row['score_agregado'])
                    }
                    todos_resultados_global.append(resultado_previo)
        except Exception as e:
            print(f"   [ADVERTENCIA] Error al cargar {archivo}: {e}")
    
    print(f"   Resultados de ejecución actual: {len(todos_resultados)}")
    print(f"   Resultados totales (actual + previos): {len(todos_resultados_global)}")
    
    # Analizar resultados
    print("\n" + "="*70)
    print("ANÁLISIS DE RESULTADOS (TODAS LAS EJECUCIONES)")
    print("="*70)
    
    # Agrupar resultados por configuración (usando todos los resultados)
    resultados_por_config = {}
    for resultado in todos_resultados_global:
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
    
    print("\nTop 10 configuraciones:")
    print(f"{'Rank':<4} {'Pob':<4} {'Gen':<4} {'PC':<5} {'PM':<5} {'K':<3} {'IL':<3} "
          f"{'Score':<8} {'MK':<8} {'Bal':<8} {'Eng':<8} {'Tiempo':<8}")
    print("-"*90)
    
    for i, res in enumerate(configuraciones_analizadas[:10], 1):
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
        
        # Guardar mejor configuración en YAML
        timestamp_final = time.strftime('%Y%m%d_%H%M%S')
        os.makedirs('tesis3/results', exist_ok=True)
        
        mejor_config_yaml = {
            'mejor_configuracion': mejor['configuracion'],
            'metricas_promedio': {
                'score_agregado': float(mejor['prom_score']),
                'makespan': float(mejor['prom_makespan']),
                'balance': float(mejor['prom_balance']),
                'energia': float(mejor['prom_energia']),
                'tiempo': float(mejor['prom_tiempo']),
                'tamano_frente': float(mejor['prom_tamano_frente'])
            },
            'timestamp': timestamp_final
        }
        
        yaml_file = f'tesis3/results/mejor_configuracion_tunning_{timestamp_final}.yaml'
        with open(yaml_file, 'w') as f:
            yaml.dump(mejor_config_yaml, f, default_flow_style=False, sort_keys=False)
        
        print(f"\nMejor configuración guardada en: {yaml_file}")
        
        # 🔄 ACTUALIZAR config.yaml directamente con la mejor configuración
        # Esto permite que otros scripts (como ejecutar_memetico.py) usen automáticamente los parámetros optimizados
        print("\n" + "="*70)
        print("ACTUALIZANDO config.yaml CON LA MEJOR CONFIGURACIÓN")
        print("="*70)
        
        config_yaml_path = 'tesis3/config/config.yaml'
        try:
            # Leer config.yaml actual
            with open(config_yaml_path, 'r') as f:
                config_completa = yaml.safe_load(f)
            
            # Actualizar parámetros con la mejor configuración encontrada
            mejor_config = mejor['configuracion']
            
            # Actualizar algoritmo NSGA-II
            config_completa['algorithm']['nsga2']['tamano_poblacion'] = mejor_config['tamano_poblacion']
            config_completa['algorithm']['nsga2']['num_generaciones'] = mejor_config['num_generaciones']
            config_completa['algorithm']['nsga2']['prob_cruce'] = mejor_config['prob_cruce']
            config_completa['algorithm']['nsga2']['prob_mutacion'] = mejor_config['prob_mutacion']
            
            # Actualizar algoritmo memético
            config_completa['algorithm']['memetic']['cada_k_generaciones'] = mejor_config['cada_k_gen']
            config_completa['algorithm']['memetic']['max_iteraciones_local'] = mejor_config['max_iter_local']
            
            # Guardar config.yaml actualizado
            with open(config_yaml_path, 'w') as f:
                yaml.dump(config_completa, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
            print(f"✅ config.yaml actualizado con la mejor configuración:")
            print(f"   Población: {mejor_config['tamano_poblacion']}")
            print(f"   Generaciones: {mejor_config['num_generaciones']}")
            print(f"   Prob. cruce: {mejor_config['prob_cruce']}")
            print(f"   Prob. mutación: {mejor_config['prob_mutacion']}")
            print(f"   Cada K gen: {mejor_config['cada_k_gen']}")
            print(f"   Max iter local: {mejor_config['max_iter_local']}")
            print(f"\n📝 Los scripts futuros (ejecutar_memetico.py, etc.) usarán estos parámetros optimizados.")
            
        except Exception as e:
            print(f"⚠️  [ADVERTENCIA] No se pudo actualizar config.yaml: {e}")
            print(f"   La mejor configuración está guardada en: {yaml_file}")
    
    # Guardar resultados SOLO si hubo ejecución (todos_resultados no está vacío)
    if len(todos_resultados) > 0:
        timestamp_final = time.strftime('%Y%m%d_%H%M%S')
        os.makedirs('tesis3/results', exist_ok=True)
        with open(f'tesis3/results/tunning_multimetrica_real_{timestamp_final}.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'tamano_poblacion', 'num_generaciones', 'prob_cruce', 'prob_mutacion',
                'cada_k_gen', 'max_iter_local', 'semilla', 'makespan', 'balance',
                'energia', 'tamano_frente', 'score_agregado', 'tiempo'
            ])
            writer.writeheader()
            for resultado in todos_resultados:
                row = resultado['configuracion'].copy()
                row.update({
                    'semilla': resultado['semilla'],
                    'makespan': resultado['makespan'],
                    'balance': resultado['balance'],
                    'energia': resultado['energia'],
                    'tamano_frente': resultado['tamano_frente'],
                    'score_agregado': resultado['score_agregado'],
                    'tiempo': resultado['tiempo']
                })
                writer.writerow(row)
        
        print(f"\nResultados guardados en: tesis3/results/tunning_multimetrica_real_{timestamp_final}.csv")
    else:
        print(f"\n✅ No se generó archivo final nuevo (todo estaba completo, se usa YAML global)")
    print("="*70)

if __name__ == "__main__":
    main()
