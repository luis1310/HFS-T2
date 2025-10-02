
"""Implementación de NSGA-II para optimización multiobjetivo"""
import random
from copy import deepcopy
from tesis3.src.fitness.multi_objective import fitness_multiobjetivo
from tesis3.src.utils.population import inicializar_poblacion


def dominancia(obj1, obj2):
    """
    Verifica si obj1 domina a obj2 (Pareto dominance)
    Para maximización: obj1 domina si es mejor en al menos uno y no peor en ninguno
    
    Returns:
        bool: True si obj1 domina a obj2
    """
    mejor_en_alguno = False
    for o1, o2 in zip(obj1, obj2):
        if o1 < o2:
            return False
        if o1 > o2:
            mejor_en_alguno = True
    return mejor_en_alguno


def clasificacion_no_dominada(poblacion, fitness_poblacion):
    """
    Clasifica población en frentes de Pareto
    
    Returns:
        List[List[int]]: Lista de frentes (cada frente es lista de índices)
    """
    n = len(poblacion)
    dominados_por = [[] for _ in range(n)]
    num_dominados = [0] * n
    
    for i in range(n):
        for j in range(i + 1, n):
            if dominancia(fitness_poblacion[i], fitness_poblacion[j]):
                dominados_por[i].append(j)
                num_dominados[j] += 1
            elif dominancia(fitness_poblacion[j], fitness_poblacion[i]):
                dominados_por[j].append(i)
                num_dominados[i] += 1
    
    frentes = [[]]
    for i in range(n):
        if num_dominados[i] == 0:
            frentes[0].append(i)
    
    k = 0
    while frentes[k]:
        siguiente_frente = []
        for i in frentes[k]:
            for j in dominados_por[i]:
                num_dominados[j] -= 1
                if num_dominados[j] == 0:
                    siguiente_frente.append(j)
        k += 1
        if siguiente_frente:
            frentes.append(siguiente_frente)
        else:
            break
    
    return frentes[:-1] if not frentes[-1] else frentes


def distancia_crowding(fitness_frente):
    """
    Calcula distancia de crowding para mantener diversidad
    
    Returns:
        List[float]: Distancias de crowding
    """
    n = len(fitness_frente)
    if n <= 2:
        return [float('inf')] * n
    
    num_objetivos = len(fitness_frente[0])
    distancias = [0.0] * n
    
    for m in range(num_objetivos):
        indices_ordenados = sorted(range(n), key=lambda i: fitness_frente[i][m])
        
        distancias[indices_ordenados[0]] = float('inf')
        distancias[indices_ordenados[-1]] = float('inf')
        
        rango = fitness_frente[indices_ordenados[-1]][m] - fitness_frente[indices_ordenados[0]][m]
        
        if rango == 0:
            continue
        
        for i in range(1, n - 1):
            idx = indices_ordenados[i]
            idx_prev = indices_ordenados[i - 1]
            idx_next = indices_ordenados[i + 1]
            
            distancias[idx] += (fitness_frente[idx_next][m] - fitness_frente[idx_prev][m]) / rango
    
    return distancias


def seleccion_nsga2(poblacion, fitness_poblacion, tamano_seleccion):
    """
    Selección basada en frentes y crowding distance
    
    Returns:
        List[Chromosome]: Población seleccionada
    """
    frentes = clasificacion_no_dominada(poblacion, fitness_poblacion)
    seleccionados = []
    
    for frente_idx in frentes:
        if len(seleccionados) + len(frente_idx) <= tamano_seleccion:
            seleccionados.extend([poblacion[i] for i in frente_idx])
        else:
            fitness_frente = [fitness_poblacion[i] for i in frente_idx]
            distancias = distancia_crowding(fitness_frente)
            
            indices_ordenados = sorted(range(len(frente_idx)), 
                                      key=lambda i: distancias[i], 
                                      reverse=True)
            
            faltantes = tamano_seleccion - len(seleccionados)
            for i in range(faltantes):
                idx_original = frente_idx[indices_ordenados[i]]
                seleccionados.append(poblacion[idx_original])
            break
    
    return seleccionados


def torneo_binario_nsga2(poblacion, fitness_poblacion, frentes):
    """
    Selecciona un individuo mediante torneo binario
    Criterio: mejor frente, luego mayor crowding distance
    """
    idx1, idx2 = random.sample(range(len(poblacion)), 2)
    
    frente1 = next(i for i, f in enumerate(frentes) if idx1 in f)
    frente2 = next(i for i, f in enumerate(frentes) if idx2 in f)
    
    if frente1 != frente2:
        return poblacion[idx1] if frente1 < frente2 else poblacion[idx2]
    
    if dominancia(fitness_poblacion[idx1], fitness_poblacion[idx2]):
        return poblacion[idx1]
    else:
        return poblacion[idx2]


def nsga2(config, metodo_cruce, metodo_mutacion, 
          tamano_poblacion=100, num_generaciones=500,
          prob_cruce=0.95, prob_mutacion=0.3,
          verbose=True):
    """
    Algoritmo NSGA-II principal
    
    Args:
        config: ProblemConfig
        metodo_cruce: función de cruce
        metodo_mutacion: función de mutación
        tamano_poblacion: tamaño de población
        num_generaciones: número de generaciones
        prob_cruce: probabilidad de cruce
        prob_mutacion: probabilidad de mutación
        verbose: imprimir progreso
    
    Returns:
        tuple: (frente_pareto, fitness_pareto, historial)
    """
    if verbose:
        print(f"Iniciando NSGA-II: {tamano_poblacion} ind, {num_generaciones} gen")
    
    poblacion = inicializar_poblacion(config, tamano_poblacion)
    historial_frentes = []
    
    for gen in range(num_generaciones):
        fitness_poblacion = [fitness_multiobjetivo(ind, config) for ind in poblacion]
        frentes = clasificacion_no_dominada(poblacion, fitness_poblacion)
        historial_frentes.append(len(frentes[0]))
        
        if verbose and (gen % 50 == 0 or gen == 0):
            print(f"Gen {gen:3d} | Frente Pareto: {len(frentes[0]):3d} individuos")
        
        descendencia = []
        while len(descendencia) < tamano_poblacion:
            padre1 = torneo_binario_nsga2(poblacion, fitness_poblacion, frentes)
            padre2 = torneo_binario_nsga2(poblacion, fitness_poblacion, frentes)
            
            hijo1, hijo2 = metodo_cruce(padre1, padre2, config, prob_cruce)
            descendencia.extend([hijo1, hijo2])
        
        descendencia = descendencia[:tamano_poblacion]
        descendencia = metodo_mutacion(descendencia, config, prob_mutacion)
        
        poblacion_combinada = poblacion + descendencia
        fitness_combinada = [fitness_multiobjetivo(ind, config) for ind in poblacion_combinada]
        
        poblacion = seleccion_nsga2(poblacion_combinada, fitness_combinada, tamano_poblacion)
    
    fitness_final = [fitness_multiobjetivo(ind, config) for ind in poblacion]
    frentes_final = clasificacion_no_dominada(poblacion, fitness_final)
    
    frente_pareto = [poblacion[i] for i in frentes_final[0]]
    fitness_pareto = [fitness_final[i] for i in frentes_final[0]]
    
    if verbose:
        print(f"Optimización completada. Frente final: {len(frente_pareto)} soluciones")
    
    return frente_pareto, fitness_pareto, historial_frentes
