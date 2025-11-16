"""NSGA-II con búsqueda local (memética)"""
import random
from tesis3.src.fitness.multi_objective import fitness_multiobjetivo
from tesis3.src.utils.population import inicializar_poblacion
from tesis3.src.algorithms.nsga2 import (
    dominancia,
    clasificacion_no_dominada,
    seleccion_nsga2,
    torneo_binario_nsga2,
)


def busqueda_local(individuo, config, max_iter=5):
    """
    Mejora local por ascenso de colina en espacio multiobjetivo
    
    Args:
        individuo: Chromosome a mejorar
        config: ProblemConfig
        max_iter: Número máximo de iteraciones
    
    Returns:
        Chromosome mejorado
    """
    mejor = individuo.copy()
    mejor_fitness = fitness_multiobjetivo(mejor, config)
    
    for _ in range(max_iter):
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
    
    return mejor


def nsga2_memetic(config, metodo_cruce, metodo_mutacion,
                  tamano_poblacion=100, num_generaciones=300,
                  prob_cruce=0.95, prob_mutacion=0.3,
                  cada_k_gen=10, max_iter_local=5,
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
        verbose: imprimir progreso
    
    Returns:
        tuple: (frente_pareto, fitness_pareto, historial)
    """
    if verbose:
        print(f"Iniciando NSGA-II Memético: {tamano_poblacion} ind, {num_generaciones} gen")
        print(f"Búsqueda local cada {cada_k_gen} generaciones ({max_iter_local} iter)")
    
    poblacion = inicializar_poblacion(config, tamano_poblacion)
    historial_frentes = []
    aplicaciones_local = 0
    
    for gen in range(num_generaciones):
        # Evaluar fitness
        fitness_poblacion = [
            fitness_multiobjetivo(ind, config)
            for ind in poblacion
        ]
        frentes = clasificacion_no_dominada(poblacion, fitness_poblacion)
        historial_frentes.append(len(frentes[0]))
        
        # Aplicar búsqueda local cada k generaciones al frente de Pareto
        if (gen + 1) % cada_k_gen == 0:
            aplicaciones_local += 1
            if verbose:
                print(f"Gen {gen+1:3d} | Búsqueda local al frente")
                print(f"   Frente tamaño: {len(frentes[0])} ind")
            
            # Mejorar individuos del primer frente
            for idx in frentes[0]:
                poblacion[idx] = busqueda_local(
                    poblacion[idx],
                    config,
                    max_iter_local,
                )
            
            # Recalcular fitness después de búsqueda local
            fitness_poblacion = [
                fitness_multiobjetivo(ind, config)
                for ind in poblacion
            ]
            frentes = clasificacion_no_dominada(poblacion, fitness_poblacion)
        
        if verbose and (gen % 50 == 0 or gen == 0):
            print(f"Gen {gen:3d} | Frente Pareto: {len(frentes[0]):3d} individuos")
        
        # Generar descendencia (igual que NSGA-II estándar)
        descendencia = []
        while len(descendencia) < tamano_poblacion:
            padre1 = torneo_binario_nsga2(poblacion, fitness_poblacion, frentes)
            padre2 = torneo_binario_nsga2(poblacion, fitness_poblacion, frentes)
            
            hijo1, hijo2 = metodo_cruce(padre1, padre2, config, prob_cruce)
            descendencia.extend([hijo1, hijo2])
        
        descendencia = descendencia[:tamano_poblacion]
        descendencia = metodo_mutacion(descendencia, config, prob_mutacion)
        
        # Combinar y seleccionar
        poblacion_combinada = poblacion + descendencia
        fitness_combinada = [
            fitness_multiobjetivo(ind, config)
            for ind in poblacion_combinada
        ]
        poblacion = seleccion_nsga2(poblacion_combinada, fitness_combinada, tamano_poblacion)
    
    # Frente final
    fitness_final = [
        fitness_multiobjetivo(ind, config)
        for ind in poblacion
    ]
    frentes_final = clasificacion_no_dominada(poblacion, fitness_final)
    
    frente_pareto = [poblacion[i] for i in frentes_final[0]]
    fitness_pareto = [fitness_final[i] for i in frentes_final[0]]
    
    if verbose:
        print(f"Optimización completada. Frente final: {len(frente_pareto)} soluciones")
        print(f"Búsqueda local aplicada {aplicaciones_local} veces")
    
    return frente_pareto, fitness_pareto, historial_frentes
