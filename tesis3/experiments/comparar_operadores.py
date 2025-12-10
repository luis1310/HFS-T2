"""Compara diferentes combinaciones de operadores - EN STANDBY TEMPORAL - se puede eliminar"""
"""Compara diferentes combinaciones de operadores"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tesis3.src.core.problem import ProblemConfig
from tesis3.src.algorithms.nsga2 import nsga2
from tesis3.src.operators.crossover import aplicar_cruce
from tesis3.src.operators.mutation import aplicar_mutacion
import time
import csv


def ejecutar_configuracion(config, metodo_cruce, metodo_mutacion, nombre, semillas=5):
    """Ejecuta una configuración con múltiples semillas"""
    resultados = []
    
    print(f"\nEjecutando: {nombre}")
    print("-" * 60)
    
    for semilla in range(semillas):
        def cruce_wrapper(p1, p2, cfg, prob):
            return aplicar_cruce(p1, p2, cfg, metodo=metodo_cruce, prob_cruce=prob)
        
        def mutacion_wrapper(pob, cfg, prob):
            return aplicar_mutacion(pob, cfg, metodo=metodo_mutacion, tasa_mut=prob)
        
        inicio = time.time()
        frente, fitness, _ = nsga2(
            config=config,
            metodo_cruce=cruce_wrapper,
            metodo_mutacion=mutacion_wrapper,
            tamano_poblacion=50,
            num_generaciones=100,
            prob_cruce=0.95,
            prob_mutacion=0.3,
            verbose=False
        )
        tiempo = time.time() - inicio
        
        metricas = [(1/f[0], 1/f[1]-1, 1/f[2]-1, 1/f[3]-1) for f in fitness]
        mejor_makespan = min(m[0] for m in metricas)
        
        resultados.append({
            'semilla': semilla,
            'mejor_makespan': mejor_makespan,
            'tamano_frente': len(frente),
            'tiempo': tiempo
        })
        
        print(f"  Semilla {semilla}: Makespan={mejor_makespan:.2f}, "
              f"Frente={len(frente)}, Tiempo={tiempo:.2f}s")
    
    return resultados


def main():
    print("="*60)
    print("COMPARACIÓN DE OPERADORES NSGA-II")
    print("="*60)
    
    config = ProblemConfig.from_yaml("tesis3/config/config.yaml")
    
    configuraciones = [
        ('uniforme', 'swap', 'Uniforme + Swap'),
        ('uniforme', 'insert', 'Uniforme + Insert'),
        ('uniforme', 'invert', 'Uniforme + Invert'),
        ('un_punto', 'swap', '1-Punto + Swap'),
        ('un_punto', 'insert', '1-Punto + Insert'),
        ('un_punto', 'invert', '1-Punto + Invert'),
    ]
    
    todos_resultados = []
    
    for cruce, mutacion, nombre in configuraciones:
        resultados = ejecutar_configuracion(config, cruce, mutacion, nombre, semillas=5)
        
        for r in resultados:
            r['configuracion'] = nombre
            r['cruce'] = cruce
            r['mutacion'] = mutacion
            todos_resultados.append(r)
    
    # Asegurar que el directorio existe
    os.makedirs('tesis3/results', exist_ok=True)
    
    with open('tesis3/results/comparacion_operadores.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'configuracion', 'cruce', 'mutacion', 'semilla',
            'mejor_makespan', 'tamano_frente', 'tiempo'
        ])
        writer.writeheader()
        writer.writerows(todos_resultados)
    
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    
    for cruce, mutacion, nombre in configuraciones:
        config_resultados = [r for r in todos_resultados if r['configuracion'] == nombre]
        makespans = [r['mejor_makespan'] for r in config_resultados]
        tiempos = [r['tiempo'] for r in config_resultados]
        
        print(f"\n{nombre}:")
        print(f"  Makespan promedio: {sum(makespans)/len(makespans):.2f}")
        print(f"  Makespan mejor: {min(makespans):.2f}")
        print(f"  Tiempo promedio: {sum(tiempos)/len(tiempos):.2f}s")
    
    print("\nResultados guardados en: tesis3/results/comparacion_operadores.csv")


if __name__ == "__main__":
    import os
    os.makedirs('tesis3/results', exist_ok=True)
    main()
