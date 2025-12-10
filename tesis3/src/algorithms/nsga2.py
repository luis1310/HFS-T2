
"""Implementación de NSGA-II para optimización multiobjetivo"""
import random
import numpy as np
from tesis3.src.fitness.multi_objective import fitness_multiobjetivo
from tesis3.src.utils.population import inicializar_poblacion

"""
Analizar el cruding distance dentro del nsga2 memetico
"""


def convertir_fitness_a_metricas(fitness):
    """
    Convierte fitness (objetivos) a métricas reales (makespan, balance, energía)
    
    Args:
        fitness: tuple (obj_makespan, obj_balance, obj_energia)
    
    Returns:
        tuple: (makespan, balance, energia) en unidades reales
    """
    obj_mk, obj_bal, obj_eng = fitness
    makespan = 1 / obj_mk if obj_mk > 0 else float('inf')
    balance = 1 / obj_bal - 1 if obj_bal > 0 else float('inf')
    energia = 1 / obj_eng - 1 if obj_eng > 0 else float('inf')
    return makespan, balance, energia


def filtrar_soluciones_similares(poblacion, fitness_poblacion, epsilon=0.01):
    """
    Filtra soluciones similares del frente de Pareto manteniendo solo soluciones únicas dominantes.
    Versión ultra-optimizada usando grid espacial para reducir complejidad de O(n²) a ~O(n).
    
    Si dos soluciones son muy similares (distancia normalizada < epsilon), se elimina:
    1. La dominada (si una domina a la otra)
    2. La peor en términos generales (si ninguna domina pero son muy similares)
    
    Args:
        poblacion: Lista de Chromosome
        fitness_poblacion: Lista de tuplas de fitness (objetivos a maximizar)
        epsilon: Umbral de similitud (por defecto 0.01 = 1%)
    
    Returns:
        tuple: (poblacion_filtrada, fitness_filtrado) con soluciones únicas dominantes
    """
    if len(poblacion) <= 1:
        return poblacion, fitness_poblacion
    
    # Optimización: si el frente es pequeño, no filtrar (ahorro de tiempo)
    if len(poblacion) <= 20:
        return poblacion, fitness_poblacion
    
    # Optimización: si el frente es muy grande, usar epsilon más estricto para reducir más
    if len(poblacion) > 50:
        epsilon_efectivo = epsilon * 0.8  # 20% más estricto para frentes grandes
    else:
        epsilon_efectivo = epsilon
    
    # OPTIMIZACIÓN: Vectorizar conversión de fitness a métricas usando NumPy
    fitness_array = np.array(fitness_poblacion)
    
    # Vectorizar conversión: makespan = 1/obj_mk, balance = 1/obj_bal - 1, energia = 1/obj_eng - 1
    # Evitar división por cero
    makespans = np.where(fitness_array[:, 0] > 0, 1.0 / fitness_array[:, 0], np.inf)
    balances = np.where(fitness_array[:, 1] > 0, 1.0 / fitness_array[:, 1] - 1.0, np.inf)
    energias = np.where(fitness_array[:, 2] > 0, 1.0 / fitness_array[:, 2] - 1.0, np.inf)
    
    # Calcular rangos de cada objetivo para normalización (vectorizado)
    rango_mk = np.ptp(makespans) if np.ptp(makespans) > 0 else 1.0
    rango_bal = np.ptp(balances) if np.ptp(balances) > 0 else 1.0
    rango_eng = np.ptp(energias) if np.ptp(energias) > 0 else 1.0
    
    # OPTIMIZACIÓN: Usar grid espacial para agrupar soluciones similares
    # Dividir el espacio en celdas de tamaño epsilon para comparar solo vecinos cercanos
    num_celdas = max(10, int(1.0 / epsilon_efectivo))  # Al menos 10 celdas
    grid = {}
    
    # OPTIMIZACIÓN: Vectorizar cálculo de scores normalizados
    # Normalizar cada objetivo y sumar
    obj_norm = fitness_array / np.maximum(np.abs(fitness_array), 1e-10)
    scores_normalizados = np.sum(obj_norm, axis=1)
    
    # OPTIMIZACIÓN: Vectorizar normalización y cálculo de celdas
    # Normalizar métricas
    mk_min, bal_min, eng_min = makespans.min(), balances.min(), energias.min()
    mk_norm = np.where(rango_mk > 0, (makespans - mk_min) / rango_mk, 0)
    bal_norm = np.where(rango_bal > 0, (balances - bal_min) / rango_bal, 0)
    eng_norm = np.where(rango_eng > 0, (energias - eng_min) / rango_eng, 0)
    
    # Discretizar a celdas (vectorizado)
    celdas_mk = (mk_norm * num_celdas).astype(int)
    celdas_bal = (bal_norm * num_celdas).astype(int)
    celdas_eng = (eng_norm * num_celdas).astype(int)
    
    # Asignar soluciones a celdas del grid
    for i in range(len(poblacion)):
        celda_key = (celdas_mk[i], celdas_bal[i], celdas_eng[i])
        if celda_key not in grid:
            grid[celda_key] = []
        grid[celda_key].append(i)
    
    # Pre-calcular celdas para uso en el bucle de filtrado
    celdas_soluciones = list(zip(celdas_mk, celdas_bal, celdas_eng))
    
    indices_eliminar = set()
    indices_mantener = []
    epsilon_sq = epsilon_efectivo ** 2
    
    for i in range(len(poblacion)):
        if i in indices_eliminar:
            continue
        
        # OPTIMIZACIÓN: Usar arrays NumPy para acceso más rápido
        mk_i, bal_i, eng_i = makespans[i], balances[i], energias[i]
        obj_i = fitness_poblacion[i]
        i_eliminado = False
        
        celda_mk_i, celda_bal_i, celda_eng_i = celdas_soluciones[i]
        
        # Comparar solo con soluciones en celdas adyacentes (máximo 27 celdas: 3x3x3)
        # OPTIMIZACIÓN: Usar set para evitar duplicados y comparaciones innecesarias
        celdas_visitadas = set()
        for dm in [-1, 0, 1]:
            for db in [-1, 0, 1]:
                for de in [-1, 0, 1]:
                    celda_key = (celda_mk_i + dm, celda_bal_i + db, celda_eng_i + de)
                    if celda_key in celdas_visitadas or celda_key not in grid:
                        continue
                    celdas_visitadas.add(celda_key)
                    
                    for j in grid[celda_key]:
                        if j <= i or j in indices_eliminar or i_eliminado:
                            continue
                        
                        # OPTIMIZACIÓN: Usar arrays NumPy para acceso más rápido
                        mk_j, bal_j, eng_j = makespans[j], balances[j], energias[j]
                        
                        # OPTIMIZACIÓN: Vectorizar verificación rápida de similitud
                        diff_mk_norm = abs(mk_i - mk_j) / rango_mk if rango_mk > 0 else 0
                        if diff_mk_norm > epsilon_efectivo:  # Early exit si diferencia grande
                            continue
                        
                        diff_bal_norm = abs(bal_i - bal_j) / rango_bal if rango_bal > 0 else 0
                        if diff_bal_norm > epsilon_efectivo:  # Early exit
                            continue
                        
                        diff_eng_norm = abs(eng_i - eng_j) / rango_eng if rango_eng > 0 else 0
                        if diff_eng_norm > epsilon_efectivo:  # Early exit
                            continue
                        
                        distancia_sq = diff_mk_norm**2 + diff_bal_norm**2 + diff_eng_norm**2
                        
                        if distancia_sq <= epsilon_sq:
                            obj_j = fitness_poblacion[j]
                            
                            # Verificar dominancia
                            i_domina_j = dominancia(obj_i, obj_j)
                            if i_domina_j:
                                indices_eliminar.add(j)
                                continue
                            
                            j_domina_i = dominancia(obj_j, obj_i)
                            if j_domina_i:
                                indices_eliminar.add(i)
                                i_eliminado = True
                                break
                            
                            # Ninguna domina, usar scores pre-calculados
                            if scores_normalizados[i] >= scores_normalizados[j]:
                                indices_eliminar.add(j)
                            else:
                                indices_eliminar.add(i)
                                i_eliminado = True
                                break
                    
                    if i_eliminado:
                        break
                if i_eliminado:
                    break
            if i_eliminado:
                break
        
        if not i_eliminado and i not in indices_eliminar:
            indices_mantener.append(i)
    
    # Filtrar poblaciones
    poblacion_filtrada = [poblacion[i] for i in indices_mantener]
    fitness_filtrado = [fitness_poblacion[i] for i in indices_mantener]
    
    return poblacion_filtrada, fitness_filtrado


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
    OPTIMIZACIÓN: Versión vectorizada usando NumPy para mejorar rendimiento
    
    Returns:
        List[List[int]]: Lista de frentes (cada frente es lista de índices)
    """
    n = len(poblacion)
    if n == 0:
        return []
    
    # OPTIMIZACIÓN: Convertir a array NumPy para operaciones vectorizadas
    fitness_array = np.array(fitness_poblacion)
    
    # OPTIMIZACIÓN: Calcular dominancia usando broadcasting de NumPy
    # Comparar todos los pares simultáneamente
    # fitness_array[i] >= fitness_array[j] para todos los objetivos
    # fitness_array[i] > fitness_array[j] en al menos un objetivo
    
    # Crear matrices de comparación usando broadcasting
    # Shape: (n, n, num_objetivos)
    fitness_i = fitness_array[:, None, :]  # (n, 1, num_objetivos)
    fitness_j = fitness_array[None, :, :]  # (1, n, num_objetivos)
    
    # i domina j si: i >= j en todos los objetivos Y i > j en al menos uno
    no_peor_en_todos = (fitness_i >= fitness_j).all(axis=2)  # (n, n)
    mejor_en_alguno = (fitness_i > fitness_j).any(axis=2)    # (n, n)
    i_domina_j = no_peor_en_todos & mejor_en_alguno  # (n, n)
    
    # Construir estructuras de datos para clasificación
    dominados_por = [[] for _ in range(n)]
    num_dominados = [0] * n
    
    # OPTIMIZACIÓN: Usar índices de NumPy en lugar de bucles anidados
    for i in range(n):
        # Encontrar todos los j que i domina
        dominados = np.where(i_domina_j[i, :])[0]
        for j in dominados:
            if i != j:  # Evitar auto-dominancia
                dominados_por[i].append(j)
                num_dominados[j] += 1
    
    # Construir frentes
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
    OPTIMIZACIÓN: Versión vectorizada usando NumPy para mejorar rendimiento
    
    Returns:
        List[float]: Distancias de crowding
    """
    n = len(fitness_frente)
    if n <= 2:
        return [float('inf')] * n
    
    # OPTIMIZACIÓN: Convertir a array NumPy para operaciones vectorizadas
    fitness_array = np.array(fitness_frente)
    num_objetivos = fitness_array.shape[1]
    distancias = np.zeros(n)
    
    for m in range(num_objetivos):
        # OPTIMIZACIÓN: Usar np.argsort en lugar de sorted con key
        indices_ordenados = np.argsort(fitness_array[:, m])
        
        # Los extremos tienen distancia infinita
        distancias[indices_ordenados[0]] = float('inf')
        distancias[indices_ordenados[-1]] = float('inf')
        
        # OPTIMIZACIÓN: Vectorizar cálculo de rango
        rango = fitness_array[indices_ordenados[-1], m] - fitness_array[indices_ordenados[0], m]
        
        if rango == 0:
            continue
        
        # OPTIMIZACIÓN: Vectorizar cálculo de distancias para elementos intermedios
        # Usar indexación avanzada de NumPy
        idx_intermedios = indices_ordenados[1:-1]
        idx_prev = indices_ordenados[:-2]
        idx_next = indices_ordenados[2:]
        
        # Calcular distancias normalizadas vectorizadas
        distancias_normalizadas = (fitness_array[idx_next, m] - fitness_array[idx_prev, m]) / rango
        distancias[idx_intermedios] += distancias_normalizadas
    
    return distancias.tolist()


def seleccion_nsga2(poblacion, fitness_poblacion, tamano_seleccion, epsilon_filtro=0.0):
    """
    Selección basada en frentes y crowding distance
    
    Args:
        poblacion: Lista de Chromosome
        fitness_poblacion: Lista de tuplas de fitness
        tamano_seleccion: Tamaño de población a seleccionar
        epsilon_filtro: Si > 0, aplica filtro de similitud al frente de Pareto
            (por defecto 0.0 = desactivado)
    
    Returns:
        List[Chromosome]: Población seleccionada
    """
    frentes = clasificacion_no_dominada(poblacion, fitness_poblacion)
    seleccionados = []
    
    for frente_idx in frentes:
        # Aplicar filtro al primer frente SIEMPRE si está activado (no condicional)
        # Esto previene que el frente se rellene con soluciones similares
        if len(frente_idx) > 0 and epsilon_filtro > 0 and len(seleccionados) == 0:
            frente_original = [poblacion[i] for i in frente_idx]
            fitness_frente = [fitness_poblacion[i] for i in frente_idx]
            
            # Filtrar soluciones similares del frente de Pareto (optimizado con grid espacial)
            frente_filtrado, fitness_filtrado = filtrar_soluciones_similares(
                frente_original, fitness_frente, epsilon_filtro
            )
            
            # Crear mapeo de índices filtrados a índices originales (optimizado con dict)
            genes_filtrados = {
                tuple(tuple(row) for row in sol.genes) for sol in frente_filtrado
            }
            frente_idx_filtrado = [
                idx
                for idx in frente_idx
                if tuple(tuple(row) for row in poblacion[idx].genes)
                in genes_filtrados
            ]
            
            frente_idx = frente_idx_filtrado
        
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
    
    # Encontrar el frente de cada índice de forma segura
    frente1 = None
    frente2 = None
    for i, f in enumerate(frentes):
        if idx1 in f:
            frente1 = i
        if idx2 in f:
            frente2 = i
    
    # Si algún índice no está en ningún frente, usar el último frente
    if frente1 is None:
        frente1 = len(frentes) - 1 if frentes else 0
    if frente2 is None:
        frente2 = len(frentes) - 1 if frentes else 0
    
    if frente1 != frente2:
        return poblacion[idx1] if frente1 < frente2 else poblacion[idx2]
    
    if dominancia(fitness_poblacion[idx1], fitness_poblacion[idx2]):
        return poblacion[idx1]
    else:
        return poblacion[idx2]


def nsga2(config, metodo_cruce, metodo_mutacion, 
          tamano_poblacion=100, num_generaciones=500,
          prob_cruce=0.95, prob_mutacion=0.3,
          epsilon_filtro=0.01, cada_k_filtro=30,
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
        epsilon_filtro: umbral de similitud para filtrado (por defecto 0.01 = 1%)
        cada_k_filtro: aplicar filtro cada k generaciones (por defecto 30)
        verbose: imprimir progreso
    
    Returns:
        tuple: (frente_pareto, fitness_pareto, historial)
    """
    if verbose:
        print(f"Iniciando NSGA-II: {tamano_poblacion} ind, {num_generaciones} gen")
        if epsilon_filtro > 0:
            print(
                f"Filtro de similitud: epsilon={epsilon_filtro*100:.1f}%, "
                f"cada {cada_k_filtro} generaciones"
            )
    
    poblacion = inicializar_poblacion(config, tamano_poblacion)
    historial_frentes = []
    
    # OPTIMIZACIÓN: Cache de fitness para evitar recálculos
    fitness_cache = {}
    
    # Inicializar frentes en la primera generación
    fitness_inicial = [fitness_multiobjetivo(ind, config) for ind in poblacion]
    for ind, fit in zip(poblacion, fitness_inicial):
        genes_key = tuple(tuple(row) for row in ind.genes)
        fitness_cache[genes_key] = fit
    frentes = clasificacion_no_dominada(poblacion, fitness_inicial)
    frente_size = len(frentes[0])
    
    for gen in range(num_generaciones):
        # OPTIMIZACIÓN: En generaciones avanzadas, reducir operaciones costosas
        # Después de 50% de generaciones
        es_generacion_avanzada = gen >= num_generaciones * 0.5
        # Después de 75% de generaciones
        es_generacion_muy_avanzada = gen >= num_generaciones * 0.75
        
        # OPTIMIZACIÓN: Solo evaluar fitness completo si no hay cache previo
        # En generaciones avanzadas, asumir que la mayoría de individuos no cambiaron
        fitness_poblacion = []
        poblacion_cambio = False
        for ind in poblacion:
            genes_key = tuple(tuple(row) for row in ind.genes)
            if genes_key in fitness_cache:
                fitness_poblacion.append(fitness_cache[genes_key])
            else:
                fit = fitness_multiobjetivo(ind, config)
                fitness_cache[genes_key] = fit
                fitness_poblacion.append(fit)
                poblacion_cambio = True
        
        # OPTIMIZACIÓN: Solo reclasificar si hubo cambios significativos o cada N generaciones
        # En generaciones muy avanzadas, reducir frecuencia de clasificación
        reclasificar = True
        if es_generacion_muy_avanzada:
            # Solo reclasificar cada 5 generaciones o si hubo cambios significativos
            reclasificar = (gen % 5 == 0) or poblacion_cambio or (gen == num_generaciones - 1)
        elif es_generacion_avanzada:
            # Solo reclasificar cada 3 generaciones o si hubo cambios
            reclasificar = (gen % 3 == 0) or poblacion_cambio or (gen == num_generaciones - 1)
        
        if reclasificar:
            frentes = clasificacion_no_dominada(poblacion, fitness_poblacion)
            frente_size = len(frentes[0])
        
        # Aplicar filtro de similitud cada k generaciones al frente de Pareto
        # OPTIMIZACIÓN: En generaciones avanzadas, aplicar filtro menos frecuentemente
        if es_generacion_muy_avanzada:
            frecuencia_filtro = cada_k_filtro * 3  # Cada 90 generaciones
        elif es_generacion_avanzada:
            frecuencia_filtro = cada_k_filtro * 2  # Cada 60 generaciones
        else:
            frecuencia_filtro = cada_k_filtro
        
        if epsilon_filtro > 0 and (gen + 1) % frecuencia_filtro == 0 and len(frentes[0]) > 1:
            frente_original = [poblacion[i] for i in frentes[0]]
            fitness_frente = [fitness_poblacion[i] for i in frentes[0]]
            
            frente_filtrado, fitness_filtrado = filtrar_soluciones_similares(
                frente_original, fitness_frente, epsilon_filtro
            )
            
            if len(frente_filtrado) < len(frente_original):
                if verbose:
                    eliminadas = len(frente_original) - len(frente_filtrado)
                    print(
                        f"Gen {gen+1:3d} | Filtro aplicado: {eliminadas} "
                        f"soluciones similares eliminadas "
                        f"({len(frente_original)} -> {len(frente_filtrado)})"
                    )
                
                # Crear conjunto de genes del frente filtrado para identificación rápida
                genes_filtrados = {
                    tuple(tuple(row) for row in sol.genes)
                    for sol in frente_filtrado
                }
                
                # Identificar índices del frente original que se mantienen
                indices_mantener = []
                indices_eliminar = []
                for idx in frentes[0]:
                    genes_sol = tuple(
                        tuple(row) for row in poblacion[idx].genes
                    )
                    if genes_sol in genes_filtrados:
                        indices_mantener.append(idx)
                    else:
                        indices_eliminar.append(idx)
                
                # Reemplazar soluciones eliminadas con mutaciones de las mejores del frente filtrado
                # o con soluciones del siguiente frente si existe
                num_eliminadas = len(indices_eliminar)
                if len(frentes) > 1 and len(frentes[1]) >= num_eliminadas:
                    # Usar soluciones del siguiente frente
                    for i, idx_eliminar in enumerate(indices_eliminar):
                        idx_siguiente = frentes[1][i]
                        poblacion[idx_eliminar] = poblacion[idx_siguiente].copy()
                else:
                    # Generar nuevas soluciones mediante mutación de las mejores del frente filtrado
                    for i, idx_eliminar in enumerate(indices_eliminar):
                        sol_base = frente_filtrado[i % len(frente_filtrado)]
                        nueva_sol = sol_base.copy()
                        # Aplicar mutación ligera
                        metodo_mutacion([nueva_sol], config, prob_mutacion)
                        poblacion[idx_eliminar] = nueva_sol
                
                # Actualizar cache para nuevas soluciones
                for ind in poblacion:
                    genes_key = tuple(tuple(row) for row in ind.genes)
                    if genes_key not in fitness_cache:
                        fit = fitness_multiobjetivo(ind, config)
                        fitness_cache[genes_key] = fit
                
                # Recalcular fitness y frentes después del filtrado
                fitness_poblacion = []
                for ind in poblacion:
                    genes_key = tuple(tuple(row) for row in ind.genes)
                    fitness_poblacion.append(fitness_cache[genes_key])
                frentes = clasificacion_no_dominada(poblacion, fitness_poblacion)
                frente_size = len(frentes[0])
        
        # NO guardar historial aquí - se guardará al final después de todos los filtros
        
        if verbose and (gen % 50 == 0 or gen == 0):
            print(
                f"Gen {gen:3d} | Frente Pareto: {frente_size:3d} individuos"
            )
        
        descendencia = []
        while len(descendencia) < tamano_poblacion:
            padre1 = torneo_binario_nsga2(poblacion, fitness_poblacion, frentes)
            padre2 = torneo_binario_nsga2(poblacion, fitness_poblacion, frentes)
            
            hijo1, hijo2 = metodo_cruce(padre1, padre2, config, prob_cruce)
            descendencia.extend([hijo1, hijo2])
        
        descendencia = descendencia[:tamano_poblacion]
        descendencia = metodo_mutacion(descendencia, config, prob_mutacion)
        
        poblacion_combinada = poblacion + descendencia
        
        # OPTIMIZACIÓN: Usar cache para fitness de descendencia
        fitness_combinada = []
        for ind in poblacion_combinada:
            genes_key = tuple(tuple(row) for row in ind.genes)
            if genes_key in fitness_cache:
                fitness_combinada.append(fitness_cache[genes_key])
            else:
                fit = fitness_multiobjetivo(ind, config)
                fitness_cache[genes_key] = fit
                fitness_combinada.append(fit)
        
        # Aplicar filtro durante la selección para mantener solo soluciones únicas dominantes
        poblacion = seleccion_nsga2(poblacion_combinada, fitness_combinada, tamano_poblacion, 
                                    epsilon_filtro=epsilon_filtro)
        
        # Recalcular frentes después de la selección para obtener tamaño real
        fitness_poblacion_actual = []
        for ind in poblacion:
            genes_key = tuple(tuple(row) for row in ind.genes)
            if genes_key in fitness_cache:
                fitness_poblacion_actual.append(fitness_cache[genes_key])
            else:
                fit = fitness_multiobjetivo(ind, config)
                fitness_cache[genes_key] = fit
                fitness_poblacion_actual.append(fit)
        frentes = clasificacion_no_dominada(poblacion, fitness_poblacion_actual)
        frente_size = len(frentes[0])
        
        # Aplicar filtro adicional al frente después de selección SIEMPRE
        # Esto previene que el frente se rellene con soluciones similares
        # CRÍTICO: Aplicar siempre después de cada selección para mantener frente limpio
        if epsilon_filtro > 0 and frente_size > 1:
            frente_actual = [poblacion[i] for i in frentes[0]]
            fitness_frente_actual = [fitness_poblacion_actual[i] for i in frentes[0]]
            
            frente_filtrado, fitness_filtrado = filtrar_soluciones_similares(
                frente_actual, fitness_frente_actual, epsilon_filtro
            )
            
            # CRÍTICO: Actualizar frente_size SIEMPRE con el tamaño del frente filtrado
            # incluso si no se eliminaron soluciones (para asegurar consistencia)
            frente_size_nuevo = len(frente_filtrado)
            
            if frente_size_nuevo < frente_size:
                # Actualizar el frente con las soluciones filtradas
                genes_filtrados = {
                    tuple(tuple(row) for row in sol.genes)
                    for sol in frente_filtrado
                }
                indices_frente_filtrado = []
                for idx in frentes[0]:
                    genes_sol = tuple(
                        tuple(row) for row in poblacion[idx].genes
                    )
                    if genes_sol in genes_filtrados:
                        indices_frente_filtrado.append(idx)
                
                # CRÍTICO: Actualizar frentes y frente_size con el tamaño REAL del frente filtrado
                frentes[0] = indices_frente_filtrado
                
                # Verificar que el tamaño sea correcto
                if len(frentes[0]) != frente_size_nuevo:
                    # Si no coincide, usar el tamaño del frente filtrado directamente
                    frente_size_nuevo = len(frente_filtrado)
                    # Reconstruir indices_frente_filtrado para que coincida
                    genes_a_indices = {}
                    for idx in frentes[0]:
                        genes_sol = tuple(
                            tuple(row) for row in poblacion[idx].genes
                        )
                        genes_a_indices[genes_sol] = idx
                    
                    indices_frente_filtrado = []
                    for sol in frente_filtrado:
                        genes_sol = tuple(tuple(row) for row in sol.genes)
                        if genes_sol in genes_a_indices:
                            indices_frente_filtrado.append(genes_a_indices[genes_sol])
                    
                    frentes[0] = indices_frente_filtrado
                
                frente_size = len(frentes[0])
                
                if verbose and (gen % 50 == 0 or gen < 10):
                    eliminadas_post = len(frente_actual) - len(frente_filtrado)
                    if eliminadas_post > 0:
                        print(
                            f"Gen {gen+1:3d} | Filtro post-selección: "
                            f"{eliminadas_post} soluciones eliminadas "
                            f"({len(frente_actual)} -> {len(frente_filtrado)}), "
                            f"frente_size={frente_size}"
                        )
            else:
                # Aunque no se eliminaron soluciones, asegurar que frente_size sea correcto
                frente_size = frente_size_nuevo
        
        # CRÍTICO: Guardar historial AL FINAL de cada generación, después de TODOS los filtros
        # Esto asegura que el historial refleje el tamaño REAL del frente filtrado
        # NOTA: frente_size ya está actualizado después del filtro post-selección del frente
        historial_frentes.append(frente_size)
        
        # Aplicar filtro post-selección adicional para mantener población limpia (opcional)
        # OPTIMIZACIÓN: Usar frecuencia adaptativa (igual que filtro del frente)
        aplicar_filtro_post = (epsilon_filtro > 0 and 
                              (gen + 1) % frecuencia_filtro == 0 and 
                              len(poblacion) > 80
                              )  # Solo si hay más de 80 soluciones
        
        if aplicar_filtro_post:
            # Mapear población seleccionada a fitness ya calculado (evitar recálculo)
            # Usar diccionario para búsqueda O(1) en lugar de O(n)
            genes_a_fitness = {}
            for ind, fit in zip(poblacion_combinada, fitness_combinada):
                genes_key = tuple(tuple(row) for row in ind.genes)
                genes_a_fitness[genes_key] = fit
            
            fitness_poblacion_actual = []
            for ind in poblacion:
                genes_key = tuple(tuple(row) for row in ind.genes)
                if genes_key in genes_a_fitness:
                    fitness_poblacion_actual.append(genes_a_fitness[genes_key])
                else:
                    # Solo recalcular si no está en el diccionario (caso raro)
                    fitness_poblacion_actual.append(fitness_multiobjetivo(ind, config))
            
            poblacion_filtrada, fitness_filtrado = filtrar_soluciones_similares(
                poblacion, fitness_poblacion_actual, epsilon_filtro
            )
            
            # Si el filtro eliminó soluciones, rellenar solo con soluciones realmente distintas
            if len(poblacion_filtrada) < tamano_poblacion:
                # Usar fitness ya calculado de población_combinada (no recalcular)
                candidatos = []
                genes_filtrados = {
                    tuple(tuple(row) for row in ind.genes)
                    for ind in poblacion_filtrada
                }
                
                for ind, fit in zip(poblacion_combinada, fitness_combinada):
                    genes_sol = tuple(tuple(row) for row in ind.genes)
                    if genes_sol not in genes_filtrados:
                        candidatos.append((ind, fit))
                
                # Agregar candidatos hasta completar población
                # (sin filtrar nuevamente para ahorrar tiempo)
                faltantes = tamano_poblacion - len(poblacion_filtrada)
                for i in range(min(faltantes, len(candidatos))):
                    poblacion_filtrada.append(candidatos[i][0])
                
                poblacion = poblacion_filtrada[:tamano_poblacion]
            else:
                poblacion = poblacion_filtrada[:tamano_poblacion]
                # Recalcular frentes después del filtro post-selección de población
                fitness_actual = []
                for ind in poblacion:
                    genes_key = tuple(tuple(row) for row in ind.genes)
                    fitness_actual.append(fitness_cache[genes_key])
                frentes = clasificacion_no_dominada(poblacion, fitness_actual)
                frente_size = len(frentes[0])
                
                # Aplicar filtro al frente nuevamente después del filtro de población
                if epsilon_filtro > 0 and frente_size > 1:
                    frente_actual = [poblacion[i] for i in frentes[0]]
                    fitness_frente_actual = [fitness_actual[i] for i in frentes[0]]
                    frente_filtrado, _ = filtrar_soluciones_similares(
                        frente_actual, fitness_frente_actual, epsilon_filtro
                    )
                    genes_filtrados = {
                        tuple(tuple(row) for row in sol.genes)
                        for sol in frente_filtrado
                    }
                    indices_frente_filtrado = []
                    for idx in frentes[0]:
                        genes_sol = tuple(tuple(row) for row in poblacion[idx].genes)
                        if genes_sol in genes_filtrados:
                            indices_frente_filtrado.append(idx)
                    frentes[0] = indices_frente_filtrado
                    frente_size = len(frentes[0])
    
    # Calcular fitness final usando cache
    fitness_final = []
    for ind in poblacion:
        genes_key = tuple(tuple(row) for row in ind.genes)
        fitness_final.append(fitness_cache[genes_key])
    frentes_final = clasificacion_no_dominada(poblacion, fitness_final)
    
    frente_pareto = [poblacion[i] for i in frentes_final[0]]
    fitness_pareto = [fitness_final[i] for i in frentes_final[0]]
    
    # Aplicar filtro final al frente de Pareto
    if epsilon_filtro > 0 and len(frente_pareto) > 1:
        frente_pareto, fitness_pareto = filtrar_soluciones_similares(
            frente_pareto, fitness_pareto, epsilon_filtro
        )
        if verbose:
            print(f"Filtro final aplicado. Frente final: {len(frente_pareto)} soluciones únicas")
    
    if verbose:
        print(f"Optimización completada. Frente final: {len(frente_pareto)} soluciones")
    
    return frente_pareto, fitness_pareto, historial_frentes
