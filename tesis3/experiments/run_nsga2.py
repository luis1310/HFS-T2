
"""Script para ejecutar NSGA-II"""
import sys
from pathlib import Path
import yaml

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
    
    # Cargar configuración de algoritmo
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path) as f:
        full_config = yaml.safe_load(f)
    
    alg_config = full_config['algorithm']['nsga2']
    exp_config = full_config['experiments']
    
    print(f"\nConfiguración del problema:")
    print(f"  Pedidos: {config.num_pedidos}")
    print(f"  Máquinas: {config.num_maquinas}")
    print(f"  Etapas: {config.num_etapas}")
    
    print(f"\nConfiguración del algoritmo:")
    print(f"  Población: {alg_config['tamano_poblacion']}")
    print(f"  Generaciones: {alg_config['num_generaciones']}")
    print(f"  Prob. cruce: {alg_config['prob_cruce']}")
    print(f"  Prob. mutación: {alg_config['prob_mutacion']}")
    
    def cruce_wrapper(p1, p2, cfg, prob):
        return aplicar_cruce(p1, p2, cfg, metodo='uniforme', prob_cruce=prob)
    
    def mutacion_wrapper(pob, cfg, prob):
        return aplicar_mutacion(pob, cfg, metodo='insert', tasa_mut=prob)
    
    inicio = time.time()
    
    frente_pareto, fitness_pareto, historial = nsga2(
        config=config,
        metodo_cruce=cruce_wrapper,
        metodo_mutacion=mutacion_wrapper,
        tamano_poblacion=alg_config['tamano_poblacion'],
        num_generaciones=alg_config['num_generaciones'],
        prob_cruce=alg_config['prob_cruce'],
        prob_mutacion=alg_config['prob_mutacion'],
        verbose=True
    )
    
    fin = time.time()
    
    print("\n" + "="*60)
    print("RESULTADOS")
    print("="*60)
    print(f"Tiempo de ejecución: {fin - inicio:.2f}s")
    print(f"Soluciones en frente de Pareto: {len(frente_pareto)}")
    print(f"Porcentaje del frente: {len(frente_pareto)/alg_config['tamano_poblacion']*100:.1f}%")
    
    print("\nTop 5 soluciones por makespan:")
    metricas = [(1/f[0], 1/f[1]-1, 1/f[2]-1, 1/f[3]-1) for f in fitness_pareto]
    top5 = sorted(enumerate(metricas), key=lambda x: x[1][0])[:5]
    
    print(f"{'#':<3} {'Makespan':<12} {'Balance':<12} {'Enfr.':<10} {'Energía':<12}")
    print("-"*60)
    for rank, (idx, (mk, bal, enf, eng)) in enumerate(top5, 1):
        print(f"{rank:<3} {mk:<12.2f} {bal:<12.2f} {enf:<10.2f} {eng:<12.2f}")
    
    print("\nDiversidad del frente:")
    makespans = [m[0] for m in metricas]
    print(f"  Makespan min: {min(makespans):.2f}s")
    print(f"  Makespan max: {max(makespans):.2f}s")
    print(f"  Rango: {max(makespans) - min(makespans):.2f}s")


if __name__ == "__main__":
    main()
