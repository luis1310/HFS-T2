"""NSGA-II con búsqueda local (memética)"""
import random
from tesis3.src.fitness.multi_objective import fitness_multiobjetivo
from tesis3.src.utils.population import inicializar_poblacion
from tesis3.src.algorithms.nsga2 import (
    dominancia,
    clasificacion_no_dominada,
    seleccion_nsga2,
    torneo_binario_nsga2,
    filtrar_soluciones_similares,
)


def busqueda_local(individuo, config, max_iter=5):
    """
    Mejora local por ascenso de colina en espacio multiobjetivo
    OPTIMIZADO: Early exit si no hay mejora después de varias iteraciones
    
    Args:
        individuo: Chromosome a mejorar
        config: ProblemConfig
        max_iter: Número máximo de iteraciones
    
    Returns:
        Chromosome mejorado
    """
    mejor = individuo.copy()
    mejor_fitness = fitness_multiobjetivo(mejor, config)
    
    sin_mejora = 0
    max_sin_mejora = max(1, max_iter // 3)  # Early exit más agresivo: si no mejora en 1/3 de iteraciones
    
    for iteracion in range(max_iter):
        # Generar vecino modificando una asignación aleatoria
        vecino = mejor.copy()
        pedido_idx = random.randint(0, len(vecino.genes) - 1)
        etapa = random.randint(0, config.num_etapas - 1)
        
        # Cambiar máquina en esa etapa
        maquina_actual = vecino.genes[pedido_idx][etapa]
        opciones = [m for m in config.get_maquinas_etapa(etapa + 1) 
                   if m != maquina_actual]
        
        if not opciones:
            continue
        
        vecino.genes[pedido_idx][etapa] = random.choice(opciones)
        vecino_fitness = fitness_multiobjetivo(vecino, config)
        
        # Aceptar si domina o es igual (exploración)
        if dominancia(vecino_fitness, mejor_fitness) or vecino_fitness == mejor_fitness:
            mejor = vecino
            mejor_fitness = vecino_fitness
            sin_mejora = 0  # Resetear contador
        else:
            sin_mejora += 1
            # Early exit si no hay mejora después de varias iteraciones
            if sin_mejora >= max_sin_mejora:
                break
    
    return mejor


def nsga2_memetic(config, metodo_cruce, metodo_mutacion,
                  tamano_poblacion=100, num_generaciones=300,
                  prob_cruce=0.95, prob_mutacion=0.3,
                  cada_k_gen=10, max_iter_local=5,
                  epsilon_filtro=0.01, cada_k_filtro=30,
                  verbose=True):
    """
    NSGA-II con búsqueda local aplicada cada k generaciones
    
    Args:
        config: ProblemConfig
        metodo_cruce: función de cruce
        metodo_mutacion: función de mutación
        tamano_poblacion: tamaño población
        num_generaciones: número generaciones
        prob_cruce: probabilidad cruce
        prob_mutacion: probabilidad mutación
        cada_k_gen: aplicar búsqueda local cada k generaciones
        max_iter_local: iteraciones de búsqueda local
        epsilon_filtro: umbral de similitud para filtrado (por defecto 0.01 = 1%)
        cada_k_filtro: aplicar filtro cada k generaciones (por defecto 30)
        verbose: imprimir progreso
    
    Returns:
        tuple: (frente_pareto, fitness_pareto, historial)
    """
    if verbose:
        print(f"Iniciando NSGA-II Memético: {tamano_poblacion} ind, {num_generaciones} gen")
        print(f"Búsqueda local cada {cada_k_gen} generaciones ({max_iter_local} iter)")
        if epsilon_filtro > 0:
            print(
                f"Filtro de similitud: epsilon={epsilon_filtro*100:.1f}%, "
                f"cada {cada_k_filtro} generaciones"
            )
    
    poblacion = inicializar_poblacion(config, tamano_poblacion)
    historial_frentes = []
    aplicaciones_local = 0
    
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
        
        # NO guardar historial aquí - se guardará al final después de todos los filtros
        
        # Aplicar búsqueda local cada k generaciones al frente de Pareto
        # RESPETANDO HIPERPARÁMETROS OPTIMIZADOS: cada_k_gen y max_iter_local del config
        aplicar_busqueda_local = (gen + 1) % cada_k_gen == 0
        
        if aplicar_busqueda_local:
            aplicaciones_local += 1
            
            # OPTIMIZACIÓN CRÍTICA: En generaciones avanzadas, limitar búsqueda local
            # Esto reduce significativamente el tiempo de ejecución
            indices_a_mejorar = frentes[0]
            if es_generacion_muy_avanzada and frente_size > 60:
                # En generaciones muy avanzadas, solo mejorar 60 individuos
                indices_a_mejorar = indices_a_mejorar[:60]
            elif es_generacion_avanzada and frente_size > 80:
                # En generaciones avanzadas, mejorar máximo 80 individuos
                indices_a_mejorar = indices_a_mejorar[:80]
            
            if verbose:
                print(f"Gen {gen+1:3d} | Búsqueda local al frente")
                print(
                    f"   Frente tamaño: {frente_size} ind, "
                    f"mejorando: {len(indices_a_mejorar)} ind, "
                    f"iteraciones: {max_iter_local}"
                )
            
            # Mejorar subconjunto del frente usando hiperparámetros optimizados
            for idx in indices_a_mejorar:
                individuo_original = poblacion[idx]
                poblacion[idx] = busqueda_local(
                    individuo_original,
                    config,
                    max_iter_local,  # Usar valor optimizado del config
                )
                # Actualizar cache
                genes_key_nuevo = tuple(tuple(row) for row in poblacion[idx].genes)
                if genes_key_nuevo not in fitness_cache:
                    fitness_cache[genes_key_nuevo] = fitness_multiobjetivo(poblacion[idx], config)
            
            # Recalcular fitness solo para los individuos mejorados
            fitness_actualizado = {}
            for idx in indices_a_mejorar:
                genes_key = tuple(tuple(row) for row in poblacion[idx].genes)
                if genes_key in fitness_cache:
                    fitness_actualizado[idx] = fitness_cache[genes_key]
                else:
                    fit = fitness_multiobjetivo(poblacion[idx], config)
                    fitness_cache[genes_key] = fit
                    fitness_actualizado[idx] = fit
            
            # Actualizar fitness_poblacion solo para los mejorados
            for idx, fit in fitness_actualizado.items():
                fitness_poblacion[idx] = fit
            
            # OPTIMIZACIÓN: Solo reclasificar si hubo mejoras significativas
            # En generaciones avanzadas, evitar reclasificación frecuente
            debe_reclasificar = (
                not es_generacion_avanzada
                or len(indices_a_mejorar) >= frente_size * 0.6
            )
            if debe_reclasificar:
                frentes = clasificacion_no_dominada(poblacion, fitness_poblacion)
                frente_size = len(frentes[0])
        
        # Aplicar filtro de similitud cada k_filtro generaciones al frente de Pareto
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
                
                # CORRECCIÓN: NO rellenar la población después del filtro
                # El filtro solo limpia el frente, pero la población completa
                # se mantiene. Las soluciones eliminadas del frente permanecen
                # en la población pero fuera del frente.
                # Esto permite que el algoritmo evolucione naturalmente
                # sin forzar rellenado
                
                # Actualizar el frente con las soluciones filtradas
                # Crear conjunto de genes del frente filtrado para identificación rápida
                genes_filtrados = {
                    tuple(tuple(row) for row in sol.genes)
                    for sol in frente_filtrado
                }
                
                # Reconstruir el primer frente con solo las soluciones filtradas
                # Las soluciones eliminadas permanecen en la población pero no en el frente
                indices_frente_filtrado = []
                for idx in frentes[0]:
                    genes_sol = tuple(tuple(row) for row in poblacion[idx].genes)
                    if genes_sol in genes_filtrados:
                        indices_frente_filtrado.append(idx)
                
                # Actualizar frentes con el frente filtrado
                frentes[0] = indices_frente_filtrado
                frente_size = len(frentes[0])
                
                # El historial se actualizará al final de la generación después de todos los filtros
        
        # Generar descendencia (igual que NSGA-II estándar)
        # CRÍTICO: Recalcular frentes antes de generar descendencia
        # para asegurar que los índices sean válidos después del filtro
        if not reclasificar or aplicar_busqueda_local:
            # Si no se reclasificó o se aplicó búsqueda local, recalcular frentes
            frentes = clasificacion_no_dominada(poblacion, fitness_poblacion)
            frente_size = len(frentes[0])
        
        descendencia = []
        while len(descendencia) < tamano_poblacion:
            padre1 = torneo_binario_nsga2(
                poblacion, fitness_poblacion, frentes
            )
            padre2 = torneo_binario_nsga2(
                poblacion, fitness_poblacion, frentes
            )
            
            hijo1, hijo2 = metodo_cruce(padre1, padre2, config, prob_cruce)
            descendencia.extend([hijo1, hijo2])
        
        descendencia = descendencia[:tamano_poblacion]
        descendencia = metodo_mutacion(descendencia, config, prob_mutacion)
        
        # Combinar y seleccionar
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
        poblacion = seleccion_nsga2(
            poblacion_combinada,
            fitness_combinada,
            tamano_poblacion,
            epsilon_filtro=epsilon_filtro,
        )
        
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
        frente_size_antes_filtro = frente_size
        if epsilon_filtro > 0 and frente_size > 1:
            frente_actual = [poblacion[i] for i in frentes[0]]
            fitness_frente_actual = [fitness_poblacion_actual[i] for i in frentes[0]]
            
            frente_filtrado, fitness_filtrado = filtrar_soluciones_similares(
                frente_actual, fitness_frente_actual, epsilon_filtro
            )
            
            if len(frente_filtrado) < frente_size:
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
                frente_size_nuevo = len(frentes[0])
                
                # Verificar que el tamaño sea correcto
                if frente_size_nuevo != len(frente_filtrado):
                    # Si no coincide, usar el tamaño del frente filtrado directamente
                    frente_size_nuevo = len(frente_filtrado)
                    # Reconstruir indices_frente_filtrado para que coincida
                    # Mapear soluciones filtradas a índices originales
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
                
                # Log de depuración (solo en generaciones clave)
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
                # Debug: si el filtro no eliminó nada, puede ser que realmente sean distintas
                if verbose and gen % 100 == 0:
                    print(
                        f"Gen {gen+1:3d} | Filtro post-selección: "
                        f"no se eliminaron soluciones (frente_size={frente_size})"
                    )
        
        # CRÍTICO: Guardar historial AL FINAL de cada generación, después de TODOS los filtros
        # Esto asegura que el historial refleje el tamaño REAL del frente filtrado
        # Debug: verificar que frente_size sea el correcto
        if verbose and gen % 100 == 0:
            print(
                f"Gen {gen+1:3d} | Guardando historial: frente_size={frente_size} "
                f"(antes filtro post-selección: {frente_size_antes_filtro})"
            )
        historial_frentes.append(frente_size)
        
        # OPTIMIZACIÓN: Reducir frecuencia de mensajes en generaciones avanzadas
        # NOTA: frente_size ya está actualizado después del filtro post-selección
        # CRÍTICO: Imprimir DESPUÉS del filtro post-selección para mostrar tamaño correcto
        if verbose:
            if es_generacion_muy_avanzada:
                if gen % 100 == 0 or gen == 0:
                    print(
                        f"Gen {gen:3d} | Frente Pareto: {frente_size:3d} individuos"
                    )
            elif es_generacion_avanzada:
                if gen % 75 == 0 or gen == 0:
                    print(
                        f"Gen {gen:3d} | Frente Pareto: {frente_size:3d} individuos"
                    )
            else:
                if gen % 50 == 0 or gen == 0:
                    print(
                        f"Gen {gen:3d} | Frente Pareto: {frente_size:3d} individuos"
                    )
    
    # Frente final (usar cache)
    fitness_final = []
    for ind in poblacion:
        genes_key = tuple(tuple(row) for row in ind.genes)
        if genes_key in fitness_cache:
            fitness_final.append(fitness_cache[genes_key])
        else:
            fit = fitness_multiobjetivo(ind, config)
            fitness_cache[genes_key] = fit
            fitness_final.append(fit)
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
        print(f"Búsqueda local aplicada {aplicaciones_local} veces")
        # Debug: mostrar algunos valores del historial para verificar
        if len(historial_frentes) > 0:
            print(f"Historial: primeros 10 valores: {historial_frentes[:10]}")
            print(f"Historial: últimos 10 valores: {historial_frentes[-10:]}")
            print(f"Historial: min={min(historial_frentes)}, max={max(historial_frentes)}, promedio={sum(historial_frentes)/len(historial_frentes):.1f}")
    
    return frente_pareto, fitness_pareto, historial_frentes
