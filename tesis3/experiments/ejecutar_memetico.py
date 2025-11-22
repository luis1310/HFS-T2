"""Compara NSGA-II estándar vs memético con paralelización real (30 semillas)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tesis3.src.core.problem import ProblemConfig
from tesis3.src.algorithms.nsga2 import nsga2
from tesis3.src.algorithms.nsga2_memetic import nsga2_memetic
from tesis3.src.operators.crossover import aplicar_cruce
from tesis3.src.operators.mutation import aplicar_mutacion
from tesis3.src.utils.seeds import cargar_semillas
import time
import numpy as np
import random
import os
import csv
import psutil
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import defaultdict
import yaml

def ejecutar_semilla_version(version, semilla, config_yaml_path='tesis3/config/config.yaml'):
    """
    Ejecuta una semilla para una versión específica (estándar o memético).
    
    Args:
        version: 'estandar' o 'memetico'
        semilla: número de semilla
        config_yaml_path: ruta al archivo de configuración
    
    Returns:
        dict con resultados de la ejecución
    """
    try:
        # Mensaje de inicio para debug (se verá en el output)
        import os
        print(f"[DEBUG] PID {os.getpid()}: Iniciando {version} semilla {semilla}...", flush=True)
        
        # Verificar que el archivo de configuración existe
        if not os.path.exists(config_yaml_path):
            raise FileNotFoundError(f"No se encontró el archivo de configuración: {config_yaml_path}")
        
        print(f"[DEBUG] PID {os.getpid()}: Archivo config encontrado, cargando...", flush=True)
        
        # Inicializar semillas para reproducibilidad
        random.seed(semilla)
        np.random.seed(semilla)
        
        # Cargar configuración del problema
        print(f"[DEBUG] PID {os.getpid()}: Cargando ProblemConfig...", flush=True)
        config = ProblemConfig.from_yaml(config_yaml_path)
        print(f"[DEBUG] PID {os.getpid()}: ProblemConfig cargado", flush=True)
        
        # Cargar parámetros del algoritmo desde config.yaml
        with open(config_yaml_path, 'r') as f:
            config_completa = yaml.safe_load(f)
        
        alg_params = config_completa['algorithm']['nsga2']
        memetic_params = config_completa['algorithm']['memetic']
        operators_params = config_completa['algorithm']['operators']
        
        # Usar parámetros desde config.yaml (optimizados tras el tunning)
        tamano_poblacion = alg_params['tamano_poblacion']
        num_generaciones = alg_params['num_generaciones']
        prob_cruce = alg_params['prob_cruce']
        prob_mutacion = alg_params['prob_mutacion']
        cada_k_gen = memetic_params['cada_k_generaciones']
        max_iter_local = memetic_params['max_iteraciones_local']
        
        # Cargar operadores desde config.yaml
        tipo_cruce = operators_params['cruce']
        tipo_mutacion = operators_params['mutacion']
        
        print(f"[DEBUG] PID {os.getpid()}: Parámetros cargados - Pob:{tamano_poblacion}, Gen:{num_generaciones}", flush=True)
        
        # Crear funciones de operadores con los tipos cargados
        def cruce(p1, p2, cfg, prob):
            return aplicar_cruce(p1, p2, cfg, metodo=tipo_cruce, prob_cruce=prob)
        
        def mutacion(pob, cfg, prob):
            return aplicar_mutacion(pob, cfg, metodo=tipo_mutacion, tasa_mut=prob)
        
        print(f"[DEBUG] PID {os.getpid()}: Iniciando ejecución del algoritmo {version}...", flush=True)
        inicio = time.time()
        
        if version == 'estandar':
            frente, fitness, _ = nsga2(
                config, cruce, mutacion,
                tamano_poblacion=tamano_poblacion,
                num_generaciones=num_generaciones,
                prob_cruce=prob_cruce,
                prob_mutacion=prob_mutacion,
                verbose=False
            )
        else:  # memético
            frente, fitness, _ = nsga2_memetic(
                config, cruce, mutacion,
                tamano_poblacion=tamano_poblacion,
                num_generaciones=num_generaciones,
                prob_cruce=prob_cruce,
                prob_mutacion=prob_mutacion,
                cada_k_gen=cada_k_gen,
                max_iter_local=max_iter_local,
                verbose=False
            )
        
        tiempo_ejecucion = time.time() - inicio
        print(f"[DEBUG] PID {os.getpid()}: Algoritmo {version} completado en {tiempo_ejecucion:.1f}s", flush=True)
        
        # Cargar valores de referencia desde config.yaml
        with open(config_yaml_path, 'r') as f:
            config_completa = yaml.safe_load(f)
        valores_ref = config_completa['experiments']['valores_referencia']
        print(f"[DEBUG] PID {os.getpid()}: Calculando métricas...", flush=True)
        
        # Convertir fitness a métricas reales (3 objetivos)
        metricas = [(1/f[0], 1/f[1]-1, 1/f[2]-1) for f in fitness]
        
        # Calcular métricas del frente de Pareto
        makespans = [m[0] for m in metricas]
        balances = [m[1] for m in metricas]
        energias = [m[2] for m in metricas]
        
        # Promedios del frente de Pareto
        prom_mk = np.mean(makespans)
        prom_bal = np.mean(balances)
        prom_eng = np.mean(energias)
        
        # Score agregado con normalización (igual que tunning y comparacion_operadores)
        # Los valores de referencia se leen desde config.yaml
        ref_mk = valores_ref['makespan']
        ref_bal = valores_ref['balance']
        ref_eng = valores_ref['energia']
        
        score_agregado = (prom_mk / ref_mk) + (prom_bal / ref_bal) + (prom_eng / ref_eng)
        
        print(f"[DEBUG] Completado {version} semilla {semilla} en {tiempo_ejecucion:.1f}s", flush=True)
        
        return {
            'version': version,
            'semilla': semilla,
            'makespan': prom_mk,
            'balance': prom_bal,
            'energia': prom_eng,
            'score_agregado': score_agregado,
            'tamano_frente': len(frente),
            'tiempo_ejecucion': tiempo_ejecucion
        }
    except Exception as e:
        import traceback
        error_msg = f"ERROR en {version} semilla {semilla}: {str(e)}\n{traceback.format_exc()}"
        print(f"[ERROR] {error_msg}", flush=True)
        raise  # Re-lanzar para que el proceso principal lo capture

def detectar_capacidades_sistema():
    """Detecta capacidades del sistema (núcleos y RAM)"""
    nucleos_fisicos = psutil.cpu_count(logical=False)
    nucleos_logicos = psutil.cpu_count(logical=True)
    memoria_gb = psutil.virtual_memory().total / (1024**3)
    return nucleos_fisicos, nucleos_logicos, memoria_gb

def detectar_resultados_previos(num_semillas=30):
    """
    Detecta qué semillas ya fueron ejecutadas previamente.
    
    Returns:
        dict: {'estandar': set(semillas), 'memetico': set(semillas)}
    """
    resultados_por_version = {
        'estandar': set(),
        'memetico': set()
    }
    
    # Buscar archivos de resultados parciales
    import glob
    archivo_parcial = 'tesis3/results/comparacion_memetica_parcial.csv'
    
    if not os.path.exists(archivo_parcial):
        print("No se encontraron resultados previos.")
        return resultados_por_version
    
    print(f"\nEncontrado archivo de resultados previos")
    
    # Leer el archivo parcial
    try:
        with open(archivo_parcial, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    version = row['version']
                    semilla = int(row['semilla'])
                    resultados_por_version[version].add(semilla)
    except Exception as e:
        print(f"Error leyendo archivo parcial: {e}")
    
    # Mostrar resumen
    print("\nEstado de ejecuciones previas:")
    for version in ['estandar', 'memetico']:
        semillas_ejecutadas = resultados_por_version[version]
        print(f"  {version.capitalize()}: {len(semillas_ejecutadas)}/{num_semillas} semillas completadas")
        
        if 0 < len(semillas_ejecutadas) < num_semillas:
            semillas_faltantes = set(range(num_semillas)) - semillas_ejecutadas
            print(f"    Faltantes: {sorted(semillas_faltantes)[:10]}{'...' if len(semillas_faltantes) > 10 else ''}")
    
    return resultados_por_version

def guardar_resultado_parcial(resultado):
    """
    Guarda un resultado individual en el archivo parcial.
    Usa UN SOLO archivo sin timestamp para permitir continuación si se interrumpe.
    """
    archivo = 'tesis3/results/comparacion_memetica_parcial.csv'
    
    # Si el archivo no existe, crear con encabezados
    file_exists = os.path.exists(archivo)
    
    with open(archivo, 'a', newline='') as f:
        fieldnames = ['version', 'semilla', 'makespan', 'balance', 'energia', 
                     'score_agregado', 'tamano_frente', 'tiempo_ejecucion']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(resultado)

def main():
    print("="*70)
    print("COMPARACIÓN: NSGA-II ESTÁNDAR vs MEMÉTICO - PARALELIZACIÓN REAL")
    print("="*70)
    
    # Detectar capacidades del sistema
    nucleos_fisicos, nucleos_logicos, memoria_gb = detectar_capacidades_sistema()
    
    print(f"\nSistema detectado:")
    print(f"   Núcleos físicos: {nucleos_fisicos}")
    print(f"   Núcleos lógicos: {nucleos_logicos}")
    print(f"   Memoria RAM: {memoria_gb:.1f} GB")
    
    # Menú de selección de núcleos
    print("\nSeleccione cuántos núcleos usar para la paralelización:")
    print(f"   1. Núcleos físicos ({nucleos_fisicos}) - Recomendado")
    print(f"   2. Núcleos lógicos ({nucleos_logicos}) - Máximo rendimiento")
    print(f"   3. Seguro (6 núcleos) - Para evitar sobrecalentamiento")
    print(f"   4. Personalizado")
    
    while True:
        try:
            opcion = int(input("\nIngrese opción (1-4): "))
            if opcion == 1:
                num_nucleos = nucleos_fisicos
                break
            elif opcion == 2:
                num_nucleos = nucleos_logicos
                break
            elif opcion == 3:
                num_nucleos = min(6, nucleos_fisicos)  # Máximo 6 núcleos para seguridad
                print(f"Usando {num_nucleos} núcleos para evitar sobrecalentamiento")
                break
            elif opcion == 4:
                num_nucleos = int(input(f"Ingrese número de núcleos (1-{nucleos_logicos}): "))
                if 1 <= num_nucleos <= nucleos_logicos:
                    break
                else:
                    print(f"Debe ser entre 1 y {nucleos_logicos}")
            else:
                print("Opción inválida. Intente nuevamente.")
        except ValueError:
            print("Por favor ingrese un número válido.")
    
    print(f"\nUsando {num_nucleos} núcleos para paralelización")
    
    # Cargar semillas desde archivo centralizado
    semillas = cargar_semillas(tipo='estandar')  # 30 semillas
    num_semillas = len(semillas)
    
    # Cargar parámetros desde config.yaml para mostrar
    with open('tesis3/config/config.yaml', 'r') as f:
        config_completa = yaml.safe_load(f)
    
    alg_params = config_completa['algorithm']['nsga2']
    memetic_params = config_completa['algorithm']['memetic']
    operators_params = config_completa['algorithm']['operators']
    
    print(f"\nParámetros de comparación (desde config.yaml):")
    print(f"   Población: {alg_params['tamano_poblacion']} individuos")
    print(f"   Generaciones: {alg_params['num_generaciones']}")
    print(f"   Prob. cruce: {alg_params['prob_cruce']}")
    print(f"   Prob. mutación: {alg_params['prob_mutacion']}")
    print(f"   Operador cruce: {operators_params['cruce']}")
    print(f"   Operador mutación: {operators_params['mutacion']}")
    print(f"   Memético - cada_k_gen: {memetic_params['cada_k_generaciones']}")
    print(f"   Memético - max_iter_local: {memetic_params['max_iteraciones_local']}")
    print(f"   Semillas: {num_semillas} (0-{num_semillas-1})")
    
    # Detectar resultados previos
    resultados_previos = detectar_resultados_previos(num_semillas)
    
    # Crear lista de tareas pendientes
    tareas = []
    for version in ['estandar', 'memetico']:
        semillas_ejecutadas = resultados_previos[version]
        for semilla in semillas:
            if semilla not in semillas_ejecutadas:
                tareas.append((version, semilla))
    
    if not tareas:
        print("\n¡Todas las ejecuciones ya están completas!")
        print("Para reejecutar, elimine los archivos parciales en tesis3/results/")
        return
    
    print(f"\nTareas pendientes: {len(tareas)} de {num_semillas * 2} totales")
    print(f"   Estándar faltantes: {num_semillas - len(resultados_previos['estandar'])}")
    print(f"   Memético faltantes: {num_semillas - len(resultados_previos['memetico'])}")
    
    # Estimación de tiempo
    tiempo_estimado_total = len(tareas) * 2 / num_nucleos / 60  # ~2 segundos por tarea
    print(f"\nTiempo estimado: {tiempo_estimado_total:.1f} minutos")
    
    # Asegurar que el directorio de resultados existe
    os.makedirs('tesis3/results', exist_ok=True)
    
    print(f"\nIniciando comparación con {num_nucleos} núcleos...")
    print("="*70)
    
    # Contador de progreso
    total_tareas = len(tareas)
    completadas = 0
    errores = 0
    
    inicio_total = time.time()
    
    # Ejecutar en paralelo
    print(f"\n🚀 INICIANDO {len(tareas)} TAREAS EN {num_nucleos} NÚCLEOS...")
    print(f"   Esto puede tomar varios minutos. Los procesos se ejecutan en paralelo.\n")
    
    with ProcessPoolExecutor(max_workers=num_nucleos) as executor:
        # Enviar todas las tareas
        print(f"📤 Enviando {len(tareas)} tareas al pool de procesos...")
        futures = {}
        for i, (version, semilla) in enumerate(tareas, 1):
            future = executor.submit(ejecutar_semilla_version, version, semilla)
            futures[future] = (version, semilla)
            if i % 10 == 0 or i == len(tareas):
                print(f"   [{i}/{len(tareas)}] Tareas enviadas...", flush=True)
        
        print(f"\n⏳ Esperando resultados (los procesos están ejecutándose)...\n")
        
        # Procesar resultados conforme se completan
        for future in as_completed(futures):
            version, semilla = futures[future]
            try:
                resultado = future.result()
                
                # Guardar resultado parcial inmediatamente
                guardar_resultado_parcial(resultado)
                
                completadas += 1
                progreso = (completadas / total_tareas) * 100
                
                print(f"[{completadas}/{total_tareas}] ({progreso:.1f}%) | "
                      f"{version.capitalize():9s} | Semilla {semilla:2d} | "
                      f"Makespan: {resultado['makespan']:6.2f}s | "
                      f"Score: {resultado['score_agregado']:.4f} | "
                      f"Tiempo: {resultado['tiempo_ejecucion']:.1f}s")
                
            except Exception as e:
                errores += 1
                print(f"ERROR en {version} semilla {semilla}: {e}")
    
    tiempo_total = time.time() - inicio_total
    
    print("\n" + "="*70)
    print(f"PARALELIZACIÓN COMPLETADA")
    print("="*70)
    print(f"Tiempo total: {tiempo_total/60:.2f} minutos")
    print(f"Tareas completadas: {completadas}/{total_tareas}")
    print(f"Errores: {errores}")
    print(f"Velocidad promedio: {completadas/(tiempo_total/60):.1f} tareas/minuto")

    # Análisis de resultados finales
    print("\n" + "="*70)
    print("ANÁLISIS DE RESULTADOS (30 semillas)")
    print("="*70)

    # Leer todos los resultados (incluyendo los previos)
    archivo_parcial = 'tesis3/results/comparacion_memetica_parcial.csv'
    
    resultados = defaultdict(list)
    
    if os.path.exists(archivo_parcial):
        with open(archivo_parcial, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                version = row['version']
                resultados[version].append({
                    'semilla': int(row['semilla']),
                    'makespan': float(row['makespan']),
                    'balance': float(row['balance']),
                    'energia': float(row['energia']),
                    'score_agregado': float(row['score_agregado']),
                    'tamano_frente': int(row['tamano_frente']),
                    'tiempo_ejecucion': float(row['tiempo_ejecucion'])
                })
    else:
        print("\n[ADVERTENCIA] No se encontró archivo parcial para análisis final")
    
    # Verificar que tengamos 30 semillas de cada versión
    for version in ['estandar', 'memetico']:
        if len(resultados[version]) != num_semillas:
            print(f"\nADVERTENCIA: {version} tiene {len(resultados[version])} semillas (esperadas: {num_semillas})")
    
    # Calcular estadísticas
    if len(resultados['estandar']) > 0 and len(resultados['memetico']) > 0:
        mk_std = [r['makespan'] for r in resultados['estandar']]
        mk_mem = [r['makespan'] for r in resultados['memetico']]
        
        bal_std = [r['balance'] for r in resultados['estandar']]
        bal_mem = [r['balance'] for r in resultados['memetico']]
        
        eng_std = [r['energia'] for r in resultados['estandar']]
        eng_mem = [r['energia'] for r in resultados['memetico']]
        
        score_std = [r['score_agregado'] for r in resultados['estandar']]
        score_mem = [r['score_agregado'] for r in resultados['memetico']]
        
        t_std = [r['tiempo_ejecucion'] for r in resultados['estandar']]
        t_mem = [r['tiempo_ejecucion'] for r in resultados['memetico']]

        print(f"\nNSGA-II ESTÁNDAR (n={len(resultados['estandar'])}):")
        print(f"   Makespan:        {np.mean(mk_std):7.2f}s ± {np.std(mk_std):5.2f} (mejor: {np.min(mk_std):.2f}, peor: {np.max(mk_std):.2f})")
        print(f"   Balance:         {np.mean(bal_std):7.2f}s ± {np.std(bal_std):5.2f}")
        print(f"   Energía:         {np.mean(eng_std):7.2f}  ± {np.std(eng_std):5.2f}")
        print(f"   Score agregado:  {np.mean(score_std):7.4f} ± {np.std(score_std):6.4f}")
        print(f"   Tiempo ejecución: {np.mean(t_std):6.2f}s ± {np.std(t_std):5.2f}")

        print(f"\nNSGA-II MEMÉTICO (n={len(resultados['memetico'])}):")
        print(f"   Makespan:        {np.mean(mk_mem):7.2f}s ± {np.std(mk_mem):5.2f} (mejor: {np.min(mk_mem):.2f}, peor: {np.max(mk_mem):.2f})")
        print(f"   Balance:         {np.mean(bal_mem):7.2f}s ± {np.std(bal_mem):5.2f}")
        print(f"   Energía:         {np.mean(eng_mem):7.2f}  ± {np.std(eng_mem):5.2f}")
        print(f"   Score agregado:  {np.mean(score_mem):7.4f} ± {np.std(score_mem):6.4f}")
        print(f"   Tiempo ejecución: {np.mean(t_mem):6.2f}s ± {np.std(t_mem):5.2f}")

        # Calcular mejoras (3 objetivos)
        mejora_mk = ((np.mean(mk_std) - np.mean(mk_mem)) / np.mean(mk_std)) * 100
        mejora_bal = ((np.mean(bal_std) - np.mean(bal_mem)) / np.mean(bal_std)) * 100
        mejora_eng = ((np.mean(eng_std) - np.mean(eng_mem)) / np.mean(eng_std)) * 100
        mejora_score = ((np.mean(score_std) - np.mean(score_mem)) / np.mean(score_std)) * 100
        
        overhead = ((np.mean(t_mem) - np.mean(t_std)) / np.mean(t_std)) * 100
        
        print(f"\nCOMPARACIÓN Y MEJORAS (3 objetivos):")
        print(f"   Mejora en Makespan:       {mejora_mk:+6.2f}%")
        print(f"   Mejora en Balance:        {mejora_bal:+6.2f}%")
        print(f"   Mejora en Energía:        {mejora_eng:+6.2f}%")
        print(f"   Mejora en Score agregado: {mejora_score:+6.2f}%")
        print(f"   Overhead computacional:   {overhead:+6.2f}%")

        print(f"\nCONCLUSIONES:")
        if mejora_score > 5:
            print(f"   La búsqueda local MEJORA SIGNIFICATIVAMENTE los resultados ({mejora_score:+.2f}%)")
        elif mejora_score > 0:
            print(f"   La búsqueda local MEJORA MODERADAMENTE los resultados ({mejora_score:+.2f}%)")
        else:
            print(f"   La búsqueda local NO mejora significativamente ({mejora_score:+.2f}%)")

        if overhead < 50:
            print(f"   El overhead computacional es ACEPTABLE ({overhead:+.2f}%)")
        else:
            print(f"   El overhead computacional es ALTO ({overhead:+.2f}%)")

        # Guardar resultado final consolidado con timestamp
        timestamp_final = time.strftime('%Y%m%d_%H%M%S')
        archivo_final = f'tesis3/results/comparacion_memetica_final_{timestamp_final}.csv'
        with open(archivo_final, 'w', newline='') as f:
            fieldnames = ['version', 'semilla', 'makespan', 'balance', 'energia', 
                         'score_agregado', 'tamano_frente', 'tiempo_ejecucion']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for version in ['estandar', 'memetico']:
                for resultado in sorted(resultados[version], key=lambda x: x['semilla']):
                    writer.writerow({
                        'version': version,
                        'semilla': resultado['semilla'],
                        'makespan': resultado['makespan'],
                        'balance': resultado['balance'],
                        'energia': resultado['energia'],
                        'score_agregado': resultado['score_agregado'],
                        'tamano_frente': resultado['tamano_frente'],
                        'tiempo_ejecucion': resultado['tiempo_ejecucion']
                    })
        
        print(f"\nResultado final guardado: {archivo_final}")
        
        # Guardar resumen en YAML
        yaml_file = f'tesis3/results/comparacion_memetica_resumen_{timestamp_final}.yaml'
        with open(yaml_file, 'w') as f:
            yaml.dump({
                'estandar': {
                    'makespan': {'promedio': float(np.mean(mk_std)), 'std': float(np.std(mk_std)), 'min': float(np.min(mk_std)), 'max': float(np.max(mk_std))},
                    'balance': {'promedio': float(np.mean(bal_std)), 'std': float(np.std(bal_std))},
                    'energia': {'promedio': float(np.mean(eng_std)), 'std': float(np.std(eng_std))},
                    'score_agregado': {'promedio': float(np.mean(score_std)), 'std': float(np.std(score_std))},
                    'tiempo_ejecucion': {'promedio': float(np.mean(t_std)), 'std': float(np.std(t_std))}
                },
                'memetico': {
                    'makespan': {'promedio': float(np.mean(mk_mem)), 'std': float(np.std(mk_mem)), 'min': float(np.min(mk_mem)), 'max': float(np.max(mk_mem))},
                    'balance': {'promedio': float(np.mean(bal_mem)), 'std': float(np.std(bal_mem))},
                    'energia': {'promedio': float(np.mean(eng_mem)), 'std': float(np.std(eng_mem))},
                    'score_agregado': {'promedio': float(np.mean(score_mem)), 'std': float(np.std(score_mem))},
                    'tiempo_ejecucion': {'promedio': float(np.mean(t_mem)), 'std': float(np.std(t_mem))}
                },
                'comparacion': {
                    'mejora_makespan_pct': float(mejora_mk),
                    'mejora_balance_pct': float(mejora_bal),
                    'mejora_energia_pct': float(mejora_eng),
                    'mejora_score_pct': float(mejora_score),
                    'overhead_computacional_pct': float(overhead)
                }
            }, f, sort_keys=False)
        
        print(f"Resumen guardado: {yaml_file}")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    main()
