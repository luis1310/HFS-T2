"""
Algoritmo Evolutivo Multiobjetivo basado en NSGA-II
Para problema de Hybrid Flow Shop con 4 objetivos:
1. Makespan
2. Balance de carga
3. Minimización de enfriamientos
4. Minimización de consumo energético
"""

from Parametros.Parametros_tot import *
from Aptitud.funcion_fitness_multiobjetivo import fitness_multiobjetivo
from Poblacion.Fun_poblacion import inicializar_poblacion
import numpy as np


def dominancia(objetivos1, objetivos2):
    """
    Determina si objetivos1 domina a objetivos2 (Pareto dominance)
    Retorna True si objetivos1 domina a objetivos2
    
    Para maximización: obj1 domina a obj2 si:
    - obj1 es mejor o igual en todos los objetivos
    - obj1 es estrictamente mejor en al menos un objetivo
    """
    mejor_en_alguno = False
    for o1, o2 in zip(objetivos1, objetivos2):
        if o1 < o2:  # Peor en algún objetivo
            return False
        if o1 > o2:  # Mejor en algún objetivo
            mejor_en_alguno = True
    return mejor_en_alguno


def clasificacion_no_dominada(poblacion, fitness_poblacion):
    """
    Clasifica la población en frentes de Pareto (Non-dominated sorting)
    
    Args:
        poblacion: Lista de individuos
        fitness_poblacion: Lista de tuplas (obj1, obj2, obj3, obj4) para cada individuo
    
    Returns:
        Lista de frentes, donde cada frente es una lista de índices
    """
    n = len(poblacion)
    dominados_por = [[] for _ in range(n)]  # Individuos que dominan a i
    num_dominados = [0] * n  # Número de individuos que dominan a i
    
    # Calcular dominancia entre todos los pares
    for i in range(n):
        for j in range(i + 1, n):
            if dominancia(fitness_poblacion[i], fitness_poblacion[j]):
                dominados_por[i].append(j)
                num_dominados[j] += 1
            elif dominancia(fitness_poblacion[j], fitness_poblacion[i]):
                dominados_por[j].append(i)
                num_dominados[i] += 1
    
    # Crear frentes
    frentes = [[]]
    for i in range(n):
        if num_dominados[i] == 0:  # Primer frente (no dominados)
            frentes[0].append(i)
    
    # Generar frentes subsecuentes
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
    Calcula la distancia de crowding para mantener diversidad
    
    Args:
        fitness_frente: Lista de tuplas (obj1, obj2, obj3, obj4) del frente
    
    Returns:
        Lista de distancias de crowding para cada individuo
    """
    n = len(fitness_frente)
    if n <= 2:
        return [float('inf')] * n
    
    num_objetivos = len(fitness_frente[0])
    distancias = [0.0] * n
    
    # Para cada objetivo
    for m in range(num_objetivos):
        # Ordenar por objetivo m
        indices_ordenados = sorted(range(n), key=lambda i: fitness_frente[i][m])
        
        # Valores extremos tienen distancia infinita
        distancias[indices_ordenados[0]] = float('inf')
        distancias[indices_ordenados[-1]] = float('inf')
        
        # Normalizar por rango del objetivo
        rango = fitness_frente[indices_ordenados[-1]][m] - fitness_frente[indices_ordenados[0]][m]
        
        if rango == 0:
            continue
        
        # Calcular distancia para puntos intermedios
        for i in range(1, n - 1):
            idx = indices_ordenados[i]
            idx_prev = indices_ordenados[i - 1]
            idx_next = indices_ordenados[i + 1]
            
            distancias[idx] += (fitness_frente[idx_next][m] - fitness_frente[idx_prev][m]) / rango
    
    return distancias


def seleccion_nsga2(poblacion, fitness_poblacion, tamano_seleccion):
    """
    Selección basada en NSGA-II usando frentes de Pareto y crowding distance
    
    Returns:
        Lista de individuos seleccionados
    """
    frentes = clasificacion_no_dominada(poblacion, fitness_poblacion)
    seleccionados = []
    
    for frente_idx in frentes:
        if len(seleccionados) + len(frente_idx) <= tamano_seleccion:
            # Agregar todo el frente
            seleccionados.extend([poblacion[i] for i in frente_idx])
        else:
            # Calcular crowding distance para el último frente
            fitness_frente = [fitness_poblacion[i] for i in frente_idx]
            distancias = distancia_crowding(fitness_frente)
            
            # Ordenar por crowding distance (mayor primero)
            indices_ordenados = sorted(range(len(frente_idx)), 
                                      key=lambda i: distancias[i], 
                                      reverse=True)
            
            # Agregar los necesarios para completar
            faltantes = tamano_seleccion - len(seleccionados)
            for i in range(faltantes):
                idx_original = frente_idx[indices_ordenados[i]]
                seleccionados.append(poblacion[idx_original])
            break
    
    return seleccionados


def algoritmo_evolutivo_multiobjetivo(
    poblacion_inicial,
    metodo_seleccion,  # Se ignorará, usaremos NSGA-II
    metodo_cruce,
    metodo_mutacion,
    prob_cruz=0.95,
    prob_mut=0.3,
    tamano_poblacion=50,
    num_generaciones=300
):
    """
    Algoritmo evolutivo multiobjetivo basado en NSGA-II con 4 objetivos
    
    Returns:
        - frente_pareto_final: Individuos del frente de Pareto final
        - fitness_pareto_final: Fitness de cada individuo del frente de Pareto
        - historial_hipervolumen: Evolución del hipervolumen por generación
    """
    
    poblacion = copy.deepcopy(poblacion_inicial)
    
    # Historial para análisis
    historial_frentes = []
    
    print(f"\n🚀 Iniciando NSGA-II Multiobjetivo (4 objetivos)")
    print(f"   Población: {tamano_poblacion} | Generaciones: {num_generaciones}")
    print(f"   Objetivos: Makespan, Balance de Carga, Enfriamientos, Consumo Energético\n")
    
    for gen in range(num_generaciones):
        # Evaluar fitness multiobjetivo de toda la población
        fitness_poblacion = [fitness_multiobjetivo(ind) for ind in poblacion]
        
        # Clasificar en frentes de Pareto
        frentes = clasificacion_no_dominada(poblacion, fitness_poblacion)
        
        # Guardar tamaño del primer frente
        historial_frentes.append(len(frentes[0]))
        
        # Imprimir progreso cada 50 generaciones
        if (gen + 1) % 50 == 0 or gen == 0:
            primer_frente = [fitness_poblacion[i] for i in frentes[0]]
            print(f"Gen {gen+1:3d} | Frente Pareto: {len(frentes[0]):3d} individuos")
        
        # Crear descendencia (cruce y mutación)
        descendencia = []
        
        while len(descendencia) < tamano_poblacion:
            # Seleccionar 2 padres usando torneo binario basado en NSGA-II
            indices = random.sample(range(len(poblacion)), 4)
            
            # Torneo 1
            if es_mejor_nsga2(indices[0], indices[1], frentes, fitness_poblacion):
                padre1 = poblacion[indices[0]]
            else:
                padre1 = poblacion[indices[1]]
            
            # Torneo 2
            if es_mejor_nsga2(indices[2], indices[3], frentes, fitness_poblacion):
                padre2 = poblacion[indices[2]]
            else:
                padre2 = poblacion[indices[3]]
            
            # Cruce
            if random.random() < prob_cruz:
                hijos = metodo_cruce(padre1, padre2)
                descendencia.extend(hijos)
            else:
                descendencia.extend([copy.deepcopy(padre1), copy.deepcopy(padre2)])
        
        # Limitar descendencia al tamaño de población
        descendencia = descendencia[:tamano_poblacion]
        
        # Mutación
        descendencia = metodo_mutacion(descendencia, prob_mut)
        
        # Combinar población actual + descendencia
        poblacion_combinada = poblacion + descendencia
        fitness_combinada = [fitness_multiobjetivo(ind) for ind in poblacion_combinada]
        
        # Selección NSGA-II para nueva generación
        poblacion = seleccion_nsga2(poblacion_combinada, fitness_combinada, tamano_poblacion)
    
    # Al final, retornar el frente de Pareto final
    fitness_final = [fitness_multiobjetivo(ind) for ind in poblacion]
    frentes_final = clasificacion_no_dominada(poblacion, fitness_final)
    
    frente_pareto = [poblacion[i] for i in frentes_final[0]]
    fitness_pareto = [fitness_final[i] for i in frentes_final[0]]
    
    print(f"\n✅ Optimización completada")
    print(f"   Frente de Pareto final: {len(frente_pareto)} soluciones\n")
    
    return frente_pareto, fitness_pareto, historial_frentes


def es_mejor_nsga2(idx1, idx2, frentes, fitness_poblacion):
    """
    Determina si el individuo idx1 es mejor que idx2 según NSGA-II
    (menor frente o, si están en el mismo frente, mayor crowding distance)
    """
    # Encontrar en qué frente está cada uno
    frente1, frente2 = None, None
    
    for i, frente in enumerate(frentes):
        if idx1 in frente:
            frente1 = i
        if idx2 in frente:
            frente2 = i
    
    # Si están en frentes diferentes, el de menor frente es mejor
    if frente1 != frente2:
        return frente1 < frente2
    
    # Si están en el mismo frente, usar crowding distance
    # (simplificación: usar dominancia directa)
    return dominancia(fitness_poblacion[idx1], fitness_poblacion[idx2])
    """Algoritmo Evolutivo Multiobjetivo basado en NSGA-II
        Para problema de Hybrid Flow Shop con 3 objetivos:
        1. Makespan
        2. Balance de carga
        3. Minimización de enfriamientos
    """

from Parametros.Parametros_tot import *
from Aptitud.funcion_fitness_multiobjetivo import fitness_multiobjetivo
from Poblacion.Fun_poblacion import inicializar_poblacion
import numpy as np


def dominancia(objetivos1, objetivos2):
    """
    Determina si objetivos1 domina a objetivos2 (Pareto dominance)
    Retorna True si objetivos1 domina a objetivos2
    
    Para maximización: obj1 domina a obj2 si:
    - obj1 es mejor o igual en todos los objetivos
    - obj1 es estrictamente mejor en al menos un objetivo
    """
    mejor_en_alguno = False
    for o1, o2 in zip(objetivos1, objetivos2):
        if o1 < o2:  # Peor en algún objetivo
            return False
        if o1 > o2:  # Mejor en algún objetivo
            mejor_en_alguno = True
    return mejor_en_alguno


def clasificacion_no_dominada(poblacion, fitness_poblacion):
    """
    Clasifica la población en frentes de Pareto (Non-dominated sorting)
    
    Args:
        poblacion: Lista de individuos
        fitness_poblacion: Lista de tuplas (obj1, obj2, obj3) para cada individuo
    
    Returns:
        Lista de frentes, donde cada frente es una lista de índices
    """
    n = len(poblacion)
    dominados_por = [[] for _ in range(n)]  # Individuos que dominan a i
    num_dominados = [0] * n  # Número de individuos que dominan a i
    
    # Calcular dominancia entre todos los pares
    for i in range(n):
        for j in range(i + 1, n):
            if dominancia(fitness_poblacion[i], fitness_poblacion[j]):
                dominados_por[i].append(j)
                num_dominados[j] += 1
            elif dominancia(fitness_poblacion[j], fitness_poblacion[i]):
                dominados_por[j].append(i)
                num_dominados[i] += 1
    
    # Crear frentes
    frentes = [[]]
    for i in range(n):
        if num_dominados[i] == 0:  # Primer frente (no dominados)
            frentes[0].append(i)
    
    # Generar frentes subsecuentes
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
    Calcula la distancia de crowding para mantener diversidad
    
    Args:
        fitness_frente: Lista de tuplas (obj1, obj2, obj3) del frente
    
    Returns:
        Lista de distancias de crowding para cada individuo
    """
    n = len(fitness_frente)
    if n <= 2:
        return [float('inf')] * n
    
    num_objetivos = len(fitness_frente[0])
    distancias = [0.0] * n
    
    # Para cada objetivo
    for m in range(num_objetivos):
        # Ordenar por objetivo m
        indices_ordenados = sorted(range(n), key=lambda i: fitness_frente[i][m])
        
        # Valores extremos tienen distancia infinita
        distancias[indices_ordenados[0]] = float('inf')
        distancias[indices_ordenados[-1]] = float('inf')
        
        # Normalizar por rango del objetivo
        rango = fitness_frente[indices_ordenados[-1]][m] - fitness_frente[indices_ordenados[0]][m]
        
        if rango == 0:
            continue
        
        # Calcular distancia para puntos intermedios
        for i in range(1, n - 1):
            idx = indices_ordenados[i]
            idx_prev = indices_ordenados[i - 1]
            idx_next = indices_ordenados[i + 1]
            
            distancias[idx] += (fitness_frente[idx_next][m] - fitness_frente[idx_prev][m]) / rango
    
    return distancias


def seleccion_nsga2(poblacion, fitness_poblacion, tamano_seleccion):
    """
    Selección basada en NSGA-II usando frentes de Pareto y crowding distance
    
    Returns:
        Lista de individuos seleccionados
    """
    frentes = clasificacion_no_dominada(poblacion, fitness_poblacion)
    seleccionados = []
    
    for frente_idx in frentes:
        if len(seleccionados) + len(frente_idx) <= tamano_seleccion:
            # Agregar todo el frente
            seleccionados.extend([poblacion[i] for i in frente_idx])
        else:
            # Calcular crowding distance para el último frente
            fitness_frente = [fitness_poblacion[i] for i in frente_idx]
            distancias = distancia_crowding(fitness_frente)
            
            # Ordenar por crowding distance (mayor primero)
            indices_ordenados = sorted(range(len(frente_idx)), 
                                      key=lambda i: distancias[i], 
                                      reverse=True)
            
            # Agregar los necesarios para completar
            faltantes = tamano_seleccion - len(seleccionados)
            for i in range(faltantes):
                idx_original = frente_idx[indices_ordenados[i]]
                seleccionados.append(poblacion[idx_original])
            break
    
    return seleccionados


def algoritmo_evolutivo_multiobjetivo(
    poblacion_inicial,
    metodo_seleccion,  # Se ignorará, usaremos NSGA-II
    metodo_cruce,
    metodo_mutacion,
    prob_cruz=0.95,
    prob_mut=0.3,
    tamano_poblacion=50,
    num_generaciones=300
):
    """
    Algoritmo evolutivo multiobjetivo basado en NSGA-II
    
    Returns:
        - frente_pareto_final: Individuos del frente de Pareto final
        - fitness_pareto_final: Fitness de cada individuo del frente de Pareto
        - historial_hipervolumen: Evolución del hipervolumen por generación
    """
    
    poblacion = copy.deepcopy(poblacion_inicial)
    
    # Historial para análisis
    historial_frentes = []
    
    print(f"\n🚀 Iniciando NSGA-II Multiobjetivo")
    print(f"   Población: {tamano_poblacion} | Generaciones: {num_generaciones}")
    print(f"   Objetivos: Makespan, Balance de Carga, Enfriamientos\n")
    
    for gen in range(num_generaciones):
        # Evaluar fitness multiobjetivo de toda la población
        fitness_poblacion = [fitness_multiobjetivo(ind) for ind in poblacion]
        
        # Clasificar en frentes de Pareto
        frentes = clasificacion_no_dominada(poblacion, fitness_poblacion)
        
        # Guardar tamaño del primer frente
        historial_frentes.append(len(frentes[0]))
        
        # Imprimir progreso cada 50 generaciones
        if (gen + 1) % 50 == 0 or gen == 0:
            primer_frente = [fitness_poblacion[i] for i in frentes[0]]
            print(f"Gen {gen+1:3d} | Frente Pareto: {len(frentes[0]):3d} individuos")
        
        # Crear descendencia (cruce y mutación)
        descendencia = []
        
        while len(descendencia) < tamano_poblacion:
            # Seleccionar 2 padres usando torneo binario basado en NSGA-II
            indices = random.sample(range(len(poblacion)), 4)
            
            # Torneo 1
            if es_mejor_nsga2(indices[0], indices[1], frentes, fitness_poblacion):
                padre1 = poblacion[indices[0]]
            else:
                padre1 = poblacion[indices[1]]
            
            # Torneo 2
            if es_mejor_nsga2(indices[2], indices[3], frentes, fitness_poblacion):
                padre2 = poblacion[indices[2]]
            else:
                padre2 = poblacion[indices[3]]
            
            # Cruce
            if random.random() < prob_cruz:
                hijos = metodo_cruce(padre1, padre2)
                descendencia.extend(hijos)
            else:
                descendencia.extend([copy.deepcopy(padre1), copy.deepcopy(padre2)])
        
        # Limitar descendencia al tamaño de población
        descendencia = descendencia[:tamano_poblacion]
        
        # Mutación
        descendencia = metodo_mutacion(descendencia, prob_mut)
        
        # Combinar población actual + descendencia
        poblacion_combinada = poblacion + descendencia
        fitness_combinada = [fitness_multiobjetivo(ind) for ind in poblacion_combinada]
        
        # Selección NSGA-II para nueva generación
        poblacion = seleccion_nsga2(poblacion_combinada, fitness_combinada, tamano_poblacion)
    
    # Al final, retornar el frente de Pareto final
    fitness_final = [fitness_multiobjetivo(ind) for ind in poblacion]
    frentes_final = clasificacion_no_dominada(poblacion, fitness_final)
    
    frente_pareto = [poblacion[i] for i in frentes_final[0]]
    fitness_pareto = [fitness_final[i] for i in frentes_final[0]]
    
    print(f"\n✅ Optimización completada")
    print(f"   Frente de Pareto final: {len(frente_pareto)} soluciones\n")
    
    return frente_pareto, fitness_pareto, historial_frentes


def es_mejor_nsga2(idx1, idx2, frentes, fitness_poblacion):
    """
    Determina si el individuo idx1 es mejor que idx2 según NSGA-II
    (menor frente o, si están en el mismo frente, mayor crowding distance)
    """
    # Encontrar en qué frente está cada uno
    frente1, frente2 = None, None
    
    for i, frente in enumerate(frentes):
        if idx1 in frente:
            frente1 = i
        if idx2 in frente:
            frente2 = i
    
    # Si están en frentes diferentes, el de menor frente es mejor
    if frente1 != frente2:
        return frente1 < frente2
    
    # Si están en el mismo frente, usar crowding distance
    # (simplificación: usar dominancia directa)
    return dominancia(fitness_poblacion[idx1], fitness_poblacion[idx2])