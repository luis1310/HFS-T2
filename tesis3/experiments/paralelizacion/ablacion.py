"""Estudio de ablación con paralelización REAL de semillas"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tesis3.src.core.problem import ProblemConfig
from tesis3.src.operators.crossover import aplicar_cruce
from tesis3.src.operators.mutation import aplicar_mutacion
from tesis3.src.algorithms.nsga2 import nsga2
from tesis3.src.algorithms.nsga2_memetic import nsga2_memetic
from tesis3.src.fitness.multi_objective import fitness_multiobjetivo
from tesis3.src.utils.seeds import cargar_semillas
import numpy as np
import random
import time
import csv
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import psutil
import yaml

print("="*70)
print("ESTUDIO DE ABLACIÓN - PARALELIZACIÓN REAL")
print("="*70)


def cargar_configuracion():
    """Carga configuración desde config.yaml"""
    # Usar el método estándar como los otros scripts
    config = ProblemConfig.from_yaml("tesis3/config/config.yaml")
    
    # Cargar configuración completa para obtener parámetros del algoritmo
    with open("tesis3/config/config.yaml", 'r') as f:
        config_data = yaml.safe_load(f)
    
    return config, config_data['algorithm']


def calcular_metricas(frente_pareto, fitness_pareto, config):
    """Calcula métricas de calidad del frente"""
    if len(frente_pareto) == 0:
        return {
            'makespan': float('inf'),
            'balance': float('inf'),
            'energia': float('inf'),
            'score_agregado': float('inf'),
            'tamano_frente': 0
        }
    
    # Convertir fitness a métricas reales
    metricas = []
    for f in fitness_pareto:
        obj_mk, obj_bal, obj_eng = f
        mk = 1 / obj_mk if obj_mk > 0 else float('inf')
        bal = 1 / obj_bal - 1 if obj_bal > 0 else float('inf')
        eng = 1 / obj_eng - 1 if obj_eng > 0 else float('inf')
        metricas.append((mk, bal, eng))
    
    makespans = [m[0] for m in metricas]
    balances = [m[1] for m in metricas]
    energias = [m[2] for m in metricas]
    
    prom_mk = np.mean(makespans)
    prom_bal = np.mean(balances)
    prom_eng = np.mean(energias)
    
    # Cargar valores de referencia desde config.yaml
    with open('tesis3/config/config.yaml', 'r') as f:
        config_completa = yaml.safe_load(f)
    valores_ref = config_completa['experiments']['valores_referencia']
    
    ref_mk = valores_ref['makespan']
    ref_bal = valores_ref['balance']
    ref_eng = valores_ref['energia']
    
    score_agregado = (prom_mk / ref_mk) + (prom_bal / ref_bal) + (prom_eng / ref_eng)
    
    return {
        'makespan': prom_mk,
        'balance': prom_bal,
        'energia': prom_eng,
        'score_agregado': score_agregado,
        'tamano_frente': len(frente_pareto)
    }


def ejecutar_semilla_ablacion(args):
    """
    Ejecuta una semilla específica para una variante (función para paralelización)
    
    Args:
        args: tuple (config, algoritmo_config, variante, semilla)
    
    Returns:
        dict con resultados (tiempo, métricas, variante, semilla)
    """
    config, algoritmo_config, variante, semilla = args
    
    import random
    random.seed(semilla)
    np.random.seed(semilla)
    
    # Acceder a parámetros de NSGA2 desde config
    tamano_poblacion = algoritmo_config['nsga2']['tamano_poblacion']
    num_generaciones = algoritmo_config['nsga2']['num_generaciones']
    prob_cruce = algoritmo_config['nsga2']['prob_cruce']
    prob_mutacion = algoritmo_config['nsga2']['prob_mutacion']
    
    # Seleccionar operadores según variante
    metodo_cruce = variante.get('cruce', 'uniforme')
    metodo_mutacion = variante.get('mutacion', 'swap')
    
    # Crear wrappers para los operadores
    def cruce(p1, p2, cfg, prob):
        # Mapear nombres: 'one_point' -> 'un_punto'
        metodo = 'un_punto' if metodo_cruce == 'one_point' else metodo_cruce
        return aplicar_cruce(p1, p2, cfg, metodo=metodo, prob_cruce=prob)
    
    def mutacion(pob, cfg, prob):
        return aplicar_mutacion(pob, cfg, metodo=metodo_mutacion, tasa_mut=prob)
    
    inicio = time.time()
    
    # Determinar qué algoritmo usar
    if variante['algoritmo'] == 'nsga2':
        # NSGA2 estándar
        epsilon_filtro = 0.01 if variante.get('filtro_epsilon', True) else 0.0
        
        frente_pareto, fitness_pareto, historial = nsga2(
            config, cruce, mutacion,
            tamano_poblacion=tamano_poblacion,
            num_generaciones=num_generaciones,
            prob_cruce=prob_cruce,
            prob_mutacion=prob_mutacion,
            epsilon_filtro=epsilon_filtro,
            cada_k_filtro=30,
            verbose=False
        )
    else:  # memetic
        epsilon_filtro = 0.01 if variante.get('filtro_epsilon', True) else 0.0
        cada_k_gen = algoritmo_config['memetic']['cada_k_generaciones']
        max_iter_local = algoritmo_config['memetic']['max_iteraciones_local']
        
        # Si búsqueda local está desactivada, usar frecuencia muy alta
        # para que nunca se ejecute (básicamente se convierte en NSGA2 estándar
        # pero con cache de fitness y optimizaciones adaptativas)
        if not variante.get('busqueda_local', True):
            cada_k_gen = num_generaciones + 1
        
        frente_pareto, fitness_pareto, historial = nsga2_memetic(
            config, cruce, mutacion,
            tamano_poblacion=tamano_poblacion,
            num_generaciones=num_generaciones,
            prob_cruce=prob_cruce,
            prob_mutacion=prob_mutacion,
            cada_k_gen=cada_k_gen,
            max_iter_local=max_iter_local,
            epsilon_filtro=epsilon_filtro,
            cada_k_filtro=30,
            verbose=False
        )
    
    tiempo = time.time() - inicio
    metricas = calcular_metricas(frente_pareto, fitness_pareto, config)
    
    return {
        'tiempo': tiempo,
        **metricas,
        'historial': historial,
        'variante': variante['nombre'],
        'semilla': semilla,
        'cruce': variante.get('cruce', 'uniforme'),
        'mutacion': variante.get('mutacion', 'swap')
    }


def generar_variantes():
    """
    Genera todas las variantes de ablación a probar
    
    Componentes que se pueden desactivar:
    - filtro_epsilon: Filtro de soluciones similares (epsilon-filtering)
    - busqueda_local: Búsqueda local (solo memético)
      NOTA: Si se desactiva en memético, se convierte en algo similar a NSGA2
            estándar pero con cache de fitness y optimizaciones adaptativas
    - cruce: Operador de cruce ('uniforme' o 'one_point')
    - mutacion: Operador de mutación ('swap', 'insert', 'invert')
    
    Optimizaciones adaptativas (solo memético, no se pueden desactivar fácilmente):
    - Reducción de frecuencia de clasificación no dominada en generaciones avanzadas
    - Limitación de individuos en búsqueda local (80 en 50%, 60 en 75%)
    - Reducción de frecuencia de filtrado en generaciones avanzadas
    
    Returns:
        List[dict]: Lista de variantes con componentes activados/desactivados
    """
    variantes = []
    
    # ===== VARIANTES BASE: NSGA2 estándar =====
    variantes.append({
        'nombre': 'NSGA2_completo',
        'algoritmo': 'nsga2',
        'filtro_epsilon': True,
        'cruce': 'uniforme',
        'mutacion': 'swap',
        'descripcion': 'NSGA2 completo (filtro epsilon + cruce uniforme + mutación swap)'
    })
    
    variantes.append({
        'nombre': 'NSGA2_sin_filtro',
        'algoritmo': 'nsga2',
        'filtro_epsilon': False,
        'cruce': 'uniforme',
        'mutacion': 'swap',
        'descripcion': 'NSGA2 sin filtro epsilon (base NSGA2)'
    })
    
    # ===== VARIANTES: Operadores genéticos en NSGA2 =====
    variantes.append({
        'nombre': 'NSGA2_one_point',
        'algoritmo': 'nsga2',
        'filtro_epsilon': True,
        'cruce': 'one_point',
        'mutacion': 'swap',
        'descripcion': 'NSGA2 con cruce one-point'
    })
    
    variantes.append({
        'nombre': 'NSGA2_mutacion_insert',
        'algoritmo': 'nsga2',
        'filtro_epsilon': True,
        'cruce': 'uniforme',
        'mutacion': 'insert',
        'descripcion': 'NSGA2 con mutación insert'
    })
    
    variantes.append({
        'nombre': 'NSGA2_mutacion_invert',
        'algoritmo': 'nsga2',
        'filtro_epsilon': True,
        'cruce': 'uniforme',
        'mutacion': 'invert',
        'descripcion': 'NSGA2 con mutación invert'
    })
    
    # ===== VARIANTES: NSGA2 memético =====
    variantes.append({
        'nombre': 'Memetico_completo',
        'algoritmo': 'memetic',
        'filtro_epsilon': True,
        'busqueda_local': True,
        'cruce': 'uniforme',
        'mutacion': 'swap',
        'descripcion': 'Memético completo (filtro + búsqueda local + cache + optimizaciones)'
    })
    
    variantes.append({
        'nombre': 'Memetico_sin_filtro',
        'algoritmo': 'memetic',
        'filtro_epsilon': False,
        'busqueda_local': True,
        'cruce': 'uniforme',
        'mutacion': 'swap',
        'descripcion': 'Memético sin filtro epsilon (solo búsqueda local)'
    })
    
    variantes.append({
        'nombre': 'Memetico_sin_busqueda_local',
        'algoritmo': 'memetic',
        'filtro_epsilon': True,
        'busqueda_local': False,
        'cruce': 'uniforme',
        'mutacion': 'swap',
        'descripcion': 'Memético sin búsqueda local (≈NSGA2 con cache y optimizaciones)'
    })
    
    variantes.append({
        'nombre': 'Memetico_sin_filtro_ni_busqueda',
        'algoritmo': 'memetic',
        'filtro_epsilon': False,
        'busqueda_local': False,
        'cruce': 'uniforme',
        'mutacion': 'swap',
        'descripcion': 'Memético base (≈NSGA2 estándar con cache y optimizaciones)'
    })
    
    # ===== VARIANTES: Operadores genéticos en memético =====
    variantes.append({
        'nombre': 'Memetico_one_point',
        'algoritmo': 'memetic',
        'filtro_epsilon': True,
        'busqueda_local': True,
        'cruce': 'one_point',
        'mutacion': 'swap',
        'descripcion': 'Memético con cruce one-point'
    })
    
    variantes.append({
        'nombre': 'Memetico_mutacion_insert',
        'algoritmo': 'memetic',
        'filtro_epsilon': True,
        'busqueda_local': True,
        'cruce': 'uniforme',
        'mutacion': 'insert',
        'descripcion': 'Memético con mutación insert'
    })
    
    return variantes


def detectar_capacidades_sistema():
    """Detecta núcleos físicos y lógicos del sistema"""
    nucleos_fisicos = psutil.cpu_count(logical=False)
    nucleos_logicos = psutil.cpu_count(logical=True)
    memoria = psutil.virtual_memory()
    memoria_gb = memoria.total / (1024**3)
    return nucleos_fisicos, nucleos_logicos, memoria_gb


def main():
    """Ejecuta estudio de ablación completo con paralelización"""
    print("="*80)
    print("ESTUDIO DE ABLACIÓN: Componentes Relevantes en NSGA2")
    print("PARALELIZADO - Ejecución rápida con múltiples núcleos")
    print("="*80)
    
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
                num_nucleos = min(6, nucleos_fisicos)
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
    
    config, algoritmo_config = cargar_configuracion()
    variantes = generar_variantes()
    
    # Cargar semillas centralizadas desde archivo de configuración
    # Esto garantiza que se usen las mismas semillas que en otros experimentos
    try:
        semillas = cargar_semillas(tipo="estandar")
        num_semillas = len(semillas)
        print(f"\n[OK] Semillas cargadas desde archivo centralizado: {num_semillas} semillas")
        print(f"   Semillas a usar: {semillas}")
    except (FileNotFoundError, KeyError) as e:
        print(f"\n[ADVERTENCIA] No se pudo cargar semillas centralizadas: {e}")
        print(f"   Usando semillas estándar (42-71) como fallback")
        num_semillas = 30
        semillas = list(range(42, 42 + num_semillas))
    
    print(f"\nConfiguración del estudio:")
    print(f"  Variantes a probar: {len(variantes)}")
    print(f"  Semillas por variante: {num_semillas}")
    print(f"  Total ejecuciones: {len(variantes) * num_semillas}")
    
    # Crear todas las tareas (variante, semilla)
    tareas = []
    for variante in variantes:
        for semilla in semillas:
            tareas.append((config, algoritmo_config, variante, semilla))
    
    print(f"\nTiempo estimado: {len(tareas) * 25 / num_nucleos / 60:.1f} minutos "
          f"(asumiendo ~25s por ejecución)")
    
    # Confirmar ejecución
    confirmar = input(f"\n¿Continuar con {len(tareas)} ejecuciones? (s/n): ").lower()
    if confirmar != 's':
        print("Ejecución cancelada.")
        return
    
    # Ejecutar en paralelo
    todos_resultados = []
    inicio_total = time.time()
    
    print(f"\n{'='*80}")
    print(f"INICIANDO {len(tareas)} TAREAS EN {num_nucleos} NÚCLEOS...")
    print(f"Timestamp inicio: {time.strftime('%H:%M:%S')}")
    print(f"{'='*80}\n")
    
    with ProcessPoolExecutor(max_workers=num_nucleos) as executor:
        # Enviar todas las tareas
        futures = []
        for tarea in tareas:
            futures.append(executor.submit(ejecutar_semilla_ablacion, tarea))
        
        # Procesar resultados conforme se completan
        for i, future in enumerate(as_completed(futures)):
            try:
                resultado = future.result()
                todos_resultados.append(resultado)
                
                # Mostrar progreso
                progreso = (i+1) / len(tareas) * 100
                tiempo_transcurrido = time.time() - inicio_total
                tiempo_por_ejecucion = tiempo_transcurrido / (i+1)
                tiempo_restante = tiempo_por_ejecucion * (len(tareas) - i-1)
                
                timestamp = time.strftime('%H:%M:%S')
                print(f"  [{progreso:5.1f}%] {i+1:4d}/{len(tareas)} - "
                      f"{resultado['variante']:<30} Semilla {resultado['semilla']:<3} - "
                      f"Tiempo: {resultado['tiempo']:.2f}s - "
                      f"Score: {resultado['score_agregado']:.4f} - "
                      f"Restante: {tiempo_restante/60:.1f}min")
            except Exception as e:
                print(f"  [ERROR] Tarea falló: {e}")
    
    tiempo_total = time.time() - inicio_total
    print(f"\n{'='*80}")
    print(f"EJECUCIÓN COMPLETADA")
    print(f"Tiempo total: {tiempo_total/60:.1f} minutos")
    print(f"{'='*80}\n")
    
    # Agrupar resultados por variante y calcular promedios
    resultados_por_variante = {}
    for resultado in todos_resultados:
        variante_nombre = resultado['variante']
        if variante_nombre not in resultados_por_variante:
            resultados_por_variante[variante_nombre] = []
        resultados_por_variante[variante_nombre].append(resultado)
    
    resultados = []
    resultados_resumen = []
    
    for variante_nombre, resultados_variante in resultados_por_variante.items():
        # Calcular promedios
        prom_tiempo = np.mean([r['tiempo'] for r in resultados_variante])
        prom_score = np.mean([r['score_agregado'] for r in resultados_variante])
        prom_makespan = np.mean([r['makespan'] for r in resultados_variante])
        prom_balance = np.mean([r['balance'] for r in resultados_variante])
        prom_energia = np.mean([r['energia'] for r in resultados_variante])
        prom_tamano_frente = np.mean([r['tamano_frente'] for r in resultados_variante])
        
        # Buscar descripción de la variante
        descripcion = next(
            (v['descripcion'] for v in variantes if v['nombre'] == variante_nombre),
            variante_nombre
        )
        
        resultados_resumen.append({
            'variante': variante_nombre,
            'descripcion': descripcion,
            'prom_tiempo': prom_tiempo,
            'prom_score': prom_score,
            'prom_makespan': prom_makespan,
            'prom_balance': prom_balance,
            'prom_energia': prom_energia,
            'prom_tamano_frente': prom_tamano_frente,
            'std_tiempo': np.std([r['tiempo'] for r in resultados_variante]),
            'std_score': np.std([r['score_agregado'] for r in resultados_variante])
        })
        
        resultados.extend(resultados_variante)
    
    # Mostrar resumen
    print(f"\n{'='*80}")
    print("RESUMEN DE RESULTADOS")
    print(f"{'='*80}")
    print(f"{'Variante':<30} {'Tiempo (s)':<12} {'Score':<10} "
          f"{'Makespan':<10} {'Balance':<10} {'Energía':<10} {'Frente':<8}")
    print("-"*80)
    
    # Ordenar por tiempo
    resultados_resumen = sorted(
        [r for r in resultados if 'prom_tiempo' in r],
        key=lambda x: x['prom_tiempo']
    )
    
    for res in resultados_resumen:
        print(f"{res['variante']:<30} {res['prom_tiempo']:<12.2f} "
              f"{res['prom_score']:<10.4f} {res['prom_makespan']:<10.2f} "
              f"{res['prom_balance']:<10.2f} {res['prom_energia']:<10.2f} "
              f"{res['prom_tamano_frente']:<8.1f}")
    
    # Guardar resultados
    import os
    from datetime import datetime
    os.makedirs('tesis3/results', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Guardar resultados detallados
    archivo_detallado = f'tesis3/results/ablacion_detallado_{timestamp}.csv'
    with open(archivo_detallado, 'w', newline='') as f:
        fieldnames = ['variante', 'semilla', 'cruce', 'mutacion', 'tiempo',
                     'makespan', 'balance', 'energia', 'score_agregado',
                     'tamano_frente']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in resultados:
            if 'semilla' in r:
                writer.writerow({
                    'variante': r['variante'],
                    'semilla': r['semilla'],
                    'cruce': r.get('cruce', 'uniforme'),
                    'mutacion': r.get('mutacion', 'swap'),
                    'tiempo': r['tiempo'],
                    'makespan': r['makespan'],
                    'balance': r['balance'],
                    'energia': r['energia'],
                    'score_agregado': r['score_agregado'],
                    'tamano_frente': r['tamano_frente']
                })
    
    # Guardar resumen
    archivo_resumen = f'tesis3/results/ablacion_resumen_{timestamp}.csv'
    with open(archivo_resumen, 'w', newline='') as f:
        fieldnames = ['variante', 'descripcion', 'prom_tiempo', 'std_tiempo',
                     'prom_score', 'std_score', 'prom_makespan', 'prom_balance',
                     'prom_energia', 'prom_tamano_frente']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in resultados_resumen:
            writer.writerow(r)
    
    print(f"\n✅ Resultados guardados:")
    print(f"   Detallado: {archivo_detallado}")
    print(f"   Resumen: {archivo_resumen}")
    
    # Análisis de impacto
    print(f"\n{'='*80}")
    print("ANÁLISIS DE IMPACTO DE COMPONENTES")
    print(f"{'='*80}")
    
    # Encontrar variantes base
    nsga2_completo = next(
        (r for r in resultados_resumen if r['variante'] == 'NSGA2_completo'),
        None
    )
    memetico_completo = next(
        (r for r in resultados_resumen if r['variante'] == 'Memetico_completo'),
        None
    )
    
    if nsga2_completo:
        print("\nImpacto en NSGA2 estándar:")
        nsga2_sin_filtro = next(
            (r for r in resultados_resumen 
             if r['variante'] == 'NSGA2_sin_filtro'),
            None
        )
        if nsga2_sin_filtro:
            impacto_tiempo = ((nsga2_sin_filtro['prom_tiempo'] - 
                              nsga2_completo['prom_tiempo']) / 
                             nsga2_completo['prom_tiempo'] * 100)
            impacto_score = ((nsga2_sin_filtro['prom_score'] - 
                             nsga2_completo['prom_score']) / 
                            nsga2_completo['prom_score'] * 100)
            print(f"  Filtro epsilon:")
            print(f"    Tiempo: {impacto_tiempo:+.1f}%")
            print(f"    Score: {impacto_score:+.1f}%")
    
    if memetico_completo:
        print("\nImpacto en NSGA2 memético:")
        memetico_sin_filtro = next(
            (r for r in resultados_resumen 
             if r['variante'] == 'Memetico_sin_filtro'),
            None
        )
        memetico_sin_busqueda = next(
            (r for r in resultados_resumen 
             if r['variante'] == 'Memetico_sin_busqueda_local'),
            None
        )
        
        if memetico_sin_filtro:
            impacto_tiempo = ((memetico_sin_filtro['prom_tiempo'] - 
                              memetico_completo['prom_tiempo']) / 
                             memetico_completo['prom_tiempo'] * 100)
            impacto_score = ((memetico_sin_filtro['prom_score'] - 
                             memetico_completo['prom_score']) / 
                            memetico_completo['prom_score'] * 100)
            print(f"  Filtro epsilon:")
            print(f"    Tiempo: {impacto_tiempo:+.1f}%")
            print(f"    Score: {impacto_score:+.1f}%")
        
        if memetico_sin_busqueda:
            impacto_tiempo = ((memetico_sin_busqueda['prom_tiempo'] - 
                             memetico_completo['prom_tiempo']) / 
                            memetico_completo['prom_tiempo'] * 100)
            impacto_score = ((memetico_sin_busqueda['prom_score'] - 
                             memetico_completo['prom_score']) / 
                            memetico_completo['prom_score'] * 100)
            print(f"  Búsqueda local:")
            print(f"    Tiempo: {impacto_tiempo:+.1f}%")
            print(f"    Score: {impacto_score:+.1f}%")


if __name__ == "__main__":
    main()

