"""
Estudio de ablación para identificar componentes más relevantes
en NSGA2 estándar vs memético

Componentes que se pueden comparar:
1. Operadores genéticos:
   - Cruce: uniforme vs one-point
   - Mutación: swap vs insert vs invert
2. Componentes del algoritmo:
   - Filtro epsilon (epsilon-filtering)
   - Búsqueda local (solo memético)
   - Cache de fitness (solo memético)
   - Optimizaciones adaptativas (solo memético):
     * Reducción de frecuencia de clasificación no dominada
     * Limitación de individuos en búsqueda local
     * Reducción de frecuencia de filtrado
"""
import time
import csv
import numpy as np
from tesis3.src.core.problem import ProblemConfig
from tesis3.src.operators.crossover import aplicar_cruce
from tesis3.src.operators.mutation import aplicar_mutacion
from tesis3.src.algorithms.nsga2 import nsga2
from tesis3.src.algorithms.nsga2_memetic import nsga2_memetic
from tesis3.src.fitness.multi_objective import fitness_multiobjetivo
import yaml


def cargar_configuracion():
    """Carga configuración desde config.yaml"""
    with open('tesis3/config/config.yaml', 'r') as f:
        config_data = yaml.safe_load(f)
    
    problem_config = config_data['problem']
    config = ProblemConfig(
        num_pedidos=problem_config['num_pedidos'],
        num_etapas=problem_config['num_etapas'],
        maquinas_por_etapa=problem_config['maquinas_por_etapa'],
        tiempos_procesamiento=problem_config['tiempos_procesamiento'],
        potencias=problem_config['potencias']
    )
    
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
    
    # Valores de referencia (normalización)
    ref_mk = 2000.0
    ref_bal = 400.0
    ref_eng = 800.0
    
    score_agregado = (prom_mk / ref_mk) + (prom_bal / ref_bal) + (prom_eng / ref_eng)
    
    return {
        'makespan': prom_mk,
        'balance': prom_bal,
        'energia': prom_eng,
        'score_agregado': score_agregado,
        'tamano_frente': len(frente_pareto)
    }


def ejecutar_ablacion_nsga2(config, algoritmo_config, variante, semilla=42):
    """
    Ejecuta una variante del algoritmo con componentes desactivados
    
    Args:
        config: ProblemConfig
        algoritmo_config: dict con parámetros del algoritmo
        variante: dict con flags de componentes activados/desactivados
        semilla: semilla aleatoria
    
    Returns:
        dict con resultados (tiempo, métricas)
    """
    import random
    random.seed(semilla)
    np.random.seed(semilla)
    
    tamano_poblacion = algoritmo_config['poblacion']
    num_generaciones = algoritmo_config['generaciones']
    prob_cruce = algoritmo_config['prob_cruce']
    prob_mutacion = algoritmo_config['prob_mutacion']
    
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
        'historial': historial
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


def main():
    """Ejecuta estudio de ablación completo"""
    print("="*80)
    print("ESTUDIO DE ABLACIÓN: Componentes Relevantes en NSGA2")
    print("="*80)
    
    config, algoritmo_config = cargar_configuracion()
    variantes = generar_variantes()
    
    # Número de semillas: usar al menos 10 para resultados estadísticamente significativos
    # Idealmente 30 como en el tunning, pero para ablación 10-15 es razonable
    num_semillas = 10
    semillas = list(range(42, 42 + num_semillas))
    
    print(f"Configuración del estudio:")
    print(f"  Variantes a probar: {len(variantes)}")
    print(f"  Semillas por variante: {num_semillas}")
    print(f"  Total ejecuciones: {len(variantes) * num_semillas}")
    print(f"  Semillas: {semillas}")
    
    resultados = []
    
    for variante in variantes:
        print(f"\n{'='*80}")
        print(f"Variante: {variante['nombre']}")
        print(f"Descripción: {variante['descripcion']}")
        print(f"{'='*80}")
        
        resultados_variante = []
        
        for semilla in semillas:
            print(f"  Semilla {semilla}...", end=' ', flush=True)
            resultado = ejecutar_ablacion_nsga2(
                config, algoritmo_config, variante, semilla
            )
            resultado['variante'] = variante['nombre']
            resultado['semilla'] = semilla
            resultado['cruce'] = variante.get('cruce', 'uniforme')
            resultado['mutacion'] = variante.get('mutacion', 'swap')
            resultados_variante.append(resultado)
            print(f"Tiempo: {resultado['tiempo']:.2f}s, "
                  f"Score: {resultado['score_agregado']:.4f}")
        
        # Calcular promedios
        prom_tiempo = np.mean([r['tiempo'] for r in resultados_variante])
        prom_score = np.mean([r['score_agregado'] for r in resultados_variante])
        prom_makespan = np.mean([r['makespan'] for r in resultados_variante])
        prom_balance = np.mean([r['balance'] for r in resultados_variante])
        prom_energia = np.mean([r['energia'] for r in resultados_variante])
        prom_tamano_frente = np.mean([r['tamano_frente'] for r in resultados_variante])
        
        resultados.append({
            'variante': variante['nombre'],
            'descripcion': variante['descripcion'],
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

