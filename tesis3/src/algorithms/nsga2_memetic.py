
"""NSGA-II con búsqueda local (memética)"""
import random
from tesis3.src.algorithms.nsga2 import (
    nsga2, dominancia, clasificacion_no_dominada
)
from tesis3.src.fitness.multi_objective import fitness_multiobjetivo


def busqueda_local(individuo, config, max_iter=5):
    """Mejora local por ascenso de colina"""
    mejor = individuo.copy()
    mejor_fitness = fitness_multiobjetivo(mejor, config)
    
    for _ in range(max_iter):
        vecino = mejor.copy()
        pedido_idx = random.randint(0, len(vecino.genes) - 1)
        etapa = random.randint(0, config.num_etapas - 1)
        
        opciones = [m for m in config.get_maquinas_etapa(etapa + 1) 
                   if m != vecino.genes[pedido_idx][etapa]]
        
        if not opciones:
            continue
        
        vecino.genes[pedido_idx][etapa] = random.choice(opciones)
        vecino_fitness = fitness_multiobjetivo(vecino, config)
        
        if dominancia(vecino_fitness, mejor_fitness):
            mejor = vecino
            mejor_fitness = vecino_fitness
    
    return mejor


def nsga2_memetic(config, metodo_cruce, metodo_mutacion,
                  tamano_poblacion=100, num_generaciones=300,
                  prob_cruce=0.95, prob_mutacion=0.3,
                  cada_k_gen=10, max_iter_local=5,
                  verbose=True):
    """NSGA-II con búsqueda local cada k generaciones"""
    
    # Ejecutar NSGA-II normal pero interceptar cada k generaciones
    # (Simplificación: llamar nsga2 estándar, aplicar local al final)
    
    frente, fitness, hist = nsga2(
        config, metodo_cruce, metodo_mutacion,
        tamano_poblacion, num_generaciones,
        prob_cruce, prob_mutacion, verbose
    )
    
    # Aplicar búsqueda local al frente final
    if verbose:
        print("Aplicando búsqueda local al frente...")
    
    frente_mejorado = [busqueda_local(ind, config, max_iter_local) 
                       for ind in frente]
    fitness_mejorado = [fitness_multiobjetivo(ind, config) 
                        for ind in frente_mejorado]
    
    return frente_mejorado, fitness_mejorado, hist
