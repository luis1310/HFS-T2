
"""Script para ejecutar NSGA-II"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tesis3.src.core.problem import ProblemConfig
from tesis3.src.algorithms.nsga2 import nsga2
from tesis3.src.operators.crossover import aplicar_cruce
from tesis3.src.operators.mutation import aplicar_mutacion
import time


def main():
    print("="*60)
    print("NSGA-II - Optimización Multiobjetivo HFS")
    print("="*60)
    
    config = ProblemConfig.from_yaml("tesis3/config/config.yaml")
    
    print(f"\nConfiguración:")
    print(f"  Pedidos: {config.num_pedidos}")
    print(f"  Máquinas: {config.num_maquinas}")
    print(f"  Etapas: {config.num_etapas}")
    
    def cruce_wrapper(p1, p2, cfg, prob):
        return aplicar_cruce(p1, p2, cfg, metodo='uniforme', prob_cruce=prob)
    
    def mutacion_wrapper(pob, cfg, prob):
        return aplicar_mutacion(pob, cfg, metodo='swap', tasa_mut=prob)
    
    inicio = time.time()
    
    frente_pareto, fitness_pareto, historial = nsga2(
        config=config,
        metodo_cruce=cruce_wrapper,
        metodo_mutacion=mutacion_wrapper,
        tamano_poblacion=50,
        num_generaciones=100,
        prob_cruce=0.95,
        prob_mutacion=0.3,
        verbose=True
    )
    
    fin = time.time()
    
    print("\n" + "="*60)
    print("RESULTADOS")
    print("="*60)
    print(f"Tiempo de ejecución: {fin - inicio:.2f}s")
    print(f"Soluciones en frente de Pareto: {len(frente_pareto)}")
    
    print("\nTop 5 soluciones por makespan:")
    metricas = [(1/f[0], 1/f[1]-1, 1/f[2]-1, 1/f[3]-1) for f in fitness_pareto]
    top5 = sorted(enumerate(metricas), key=lambda x: x[1][0])[:5]
    
    print(f"{'#':<3} {'Makespan':<12} {'Balance':<12} {'Enfr.':<10} {'Energía':<12}")
    print("-"*60)
    for rank, (idx, (mk, bal, enf, eng)) in enumerate(top5, 1):
        print(f"{rank:<3} {mk:<12.2f} {bal:<12.2f} {enf:<10.2f} {eng:<12.2f}")


if __name__ == "__main__":
    main()
