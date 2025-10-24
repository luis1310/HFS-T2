"""Compara operadores mostrando TODOS los objetivos correctamente (3 objetivos)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tesis3.src.core.problem import ProblemConfig
from tesis3.src.algorithms.nsga2 import nsga2
from tesis3.src.operators.crossover import aplicar_cruce
from tesis3.src.operators.mutation import aplicar_mutacion
import time
import csv
import numpy as np

config = ProblemConfig.from_yaml("tesis3/config/config.yaml")

def ejecutar_configuracion(metodo_cruce, metodo_mutacion, nombre, semillas=5):
    resultados = []
    
    print(f"\n{'='*70}")
    print(f"Ejecutando: {nombre}")
    print(f"{'='*70}")
    
    for semilla in range(semillas):
        def cruce_wrapper(p1, p2, cfg, prob):
            return aplicar_cruce(p1, p2, cfg, metodo=metodo_cruce, prob_cruce=prob)
        
        def mutacion_wrapper(pob, cfg, prob):
            return aplicar_mutacion(pob, cfg, metodo=metodo_mutacion, tasa_mut=prob)
        
        inicio = time.time()
        frente, fitness, _ = nsga2(
            config, cruce_wrapper, mutacion_wrapper,
            tamano_poblacion=50,
            num_generaciones=100,
            prob_cruce=0.95,
            prob_mutacion=0.3,
            verbose=False
        )
        tiempo = time.time() - inicio
        
        # Convertir TODOS los objetivos
        metricas = [(1/f[0], 1/f[1]-1, 1/f[2]-1) for f in fitness]
        
        # Extraer cada objetivo
        makespans = [m[0] for m in metricas]
        balances = [m[1] for m in metricas]
        energias = [m[2] for m in metricas]
        
        resultados.append({
            'semilla': semilla,
            'mejor_makespan': min(makespans),
            'promedio_makespan': np.mean(makespans),
            'mejor_balance': min(balances),
            'promedio_balance': np.mean(balances),
            'mejor_energia': min(energias),
            'promedio_energia': np.mean(energias),
            'tamano_frente': len(frente),
            'tiempo': tiempo
        })
        
        print(f"  Sem {semilla}: MK={min(makespans):7.2f} | "
              f"Bal={np.mean(balances):6.2f} | "
              f"Eng={np.mean(energias):6.2f}")
    
    return resultados

def main():
    print("="*70)
    print("COMPARACIÓN MULTIOBJETIVO DE OPERADORES (3 OBJETIVOS)")
    print("="*70)
    
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
        resultados = ejecutar_configuracion(cruce, mutacion, nombre, semillas=5)
        
        for r in resultados:
            r['configuracion'] = nombre
            r['cruce'] = cruce
            r['mutacion'] = mutacion
            todos_resultados.append(r)
    
    # Guardar CSV completo
    with open('tesis3/results/comparacion_operadores_completa.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'configuracion', 'cruce', 'mutacion', 'semilla',
            'mejor_makespan', 'promedio_makespan',
            'mejor_balance', 'promedio_balance',
            'mejor_energia', 'promedio_energia',
            'tamano_frente', 'tiempo'
        ])
        writer.writeheader()
        writer.writerows(todos_resultados)
    
    # ============================================================
    # TABLA RESUMEN
    # ============================================================
    print("\n" + "="*70)
    print("RESUMEN COMPARATIVO (Promedios de 5 semillas)")
    print("="*70)
    print(f"\n{'Operador':<20} {'Makespan':<10} {'Balance':<10} {'Energía':<10}")
    print("-"*60)
    
    ranking_datos = []
    for cruce, mutacion, nombre in configuraciones:
        config_resultados = [r for r in todos_resultados if r['configuracion'] == nombre]
        
        prom_mk = np.mean([r['promedio_makespan'] for r in config_resultados])
        prom_bal = np.mean([r['promedio_balance'] for r in config_resultados])
        prom_eng = np.mean([r['promedio_energia'] for r in config_resultados])
        
        ranking_datos.append((nombre, prom_mk, prom_bal, prom_eng))
        
        print(f"{nombre:<20} {prom_mk:<10.2f} {prom_bal:<10.2f} {prom_eng:<10.2f}")
    
    # ============================================================
    # ANÁLISIS DETALLADO POR OBJETIVO
    # ============================================================
    print("\n" + "="*70)
    print("ANÁLISIS POR OBJETIVO")
    print("="*70)
    
    # Ranking por makespan
    ranking_mk = sorted(ranking_datos, key=lambda x: x[1])
    print("\nRanking por Makespan (menor es mejor):")
    for i, (nombre, mk, _, _) in enumerate(ranking_mk[:3], 1):
        posicion = f"{i}."
        print(f"  {posicion} {nombre:<20} {mk:.2f}s")
    
    # Ranking por balance
    ranking_bal = sorted(ranking_datos, key=lambda x: x[2])
    print("\nRanking por Balance (menor es mejor):")
    for i, (nombre, _, bal, _) in enumerate(ranking_bal[:3], 1):
        posicion = f"{i}."
        print(f"  {posicion} {nombre:<20} {bal:.2f}")
    
    # Ranking por energía
    ranking_eng = sorted(ranking_datos, key=lambda x: x[3])
    print("\nRanking por Energía (menor es mejor):")
    for i, (nombre, _, _, eng) in enumerate(ranking_eng[:3], 1):
        posicion = f"{i}."
        print(f"  {posicion} {nombre:<20} {eng:.2f} kWh")
    
    # ============================================================
    # MÉTRICA AGREGADA NORMALIZADA
    # ============================================================
    print("\n" + "="*70)
    print("MÉTRICA AGREGADA NORMALIZADA")
    print("="*70)
    
    # Encontrar valores máximos para normalización
    max_mk = max([mk for _, mk, _, _ in ranking_datos])
    max_bal = max([bal for _, _, bal, _ in ranking_datos])
    max_eng = max([eng for _, _, _, eng in ranking_datos])
    
    print(f"Valores máximos para normalización:")
    print(f"   Makespan: {max_mk:.2f}s")
    print(f"   Balance:  {max_bal:.2f}")
    print(f"   Energía:  {max_eng:.2f} kWh")
    
    # Calcular métrica agregada normalizada
    metricas_agregadas = []
    for nombre, mk, bal, eng in ranking_datos:
        # Normalizar (menor es mejor, por eso dividimos por el máximo)
        mk_norm = mk / max_mk
        bal_norm = bal / max_bal
        eng_norm = eng / max_eng
        
        # Métrica agregada (menor es mejor)
        score_agregado = mk_norm + bal_norm + eng_norm
        metricas_agregadas.append((nombre, score_agregado, mk, bal, eng))
    
    # Ordenar por score agregado (menor es mejor)
    metricas_agregadas.sort(key=lambda x: x[1])
    
    print(f"\n{'Operador':<20} {'Score':<10} {'MK':<10} {'Balance':<10} {'Energía':<10}")
    print("-"*70)
    for nombre, score, mk, bal, eng in metricas_agregadas:
        print(f"{nombre:<20} {score:<10.4f} {mk:<10.2f} {bal:<10.2f} {eng:<10.2f}")
    
    mejor_operador_agregado = metricas_agregadas[0][0]
    mejor_score = metricas_agregadas[0][1]
    
    print(f"\nMEJOR OPERADOR (métrica agregada):")
    print(f"   {mejor_operador_agregado}")
    print(f"   Score normalizado: {mejor_score:.4f}")
    
    # ============================================================
    # VERIFICAR DOMINANCIA
    # ============================================================
    print("\n" + "="*70)
    print("ANÁLISIS DE DOMINANCIA")
    print("="*70)
    
    # Encontrar el que domina en más objetivos
    puntos_por_operador = {}
    for nombre, mk, bal, eng in ranking_datos:
        puntos = 0
        # Punto por cada objetivo donde es el mejor
        if mk == ranking_mk[0][1]:
            puntos += 1
        if bal == ranking_bal[0][2]:
            puntos += 1
        if eng == ranking_eng[0][3]:
            puntos += 1
        puntos_por_operador[nombre] = puntos
    
    mejor_operador = max(puntos_por_operador, key=puntos_por_operador.get)
    puntos_mejor = puntos_por_operador[mejor_operador]
    
    print(f"\nOPERADOR DOMINANTE:")
    print(f"   {mejor_operador}")
    print(f"   Mejor en {puntos_mejor}/3 objetivos")
    
    if puntos_mejor == 3:
        print("\n   DOMINA COMPLETAMENTE (mejor en todos los objetivos)")
    elif puntos_mejor >= 2:
        print("\n   DOMINA FUERTEMENTE (mejor en mayoría de objetivos)")
    else:
        print("\n   No hay dominancia clara (trade-offs entre objetivos)")
    
    print("\n" + "="*70)
    print("�� Resultados guardados: tesis3/results/comparacion_operadores_completa.csv")
    print("="*70)

if __name__ == "__main__":
    import os
    os.makedirs('tesis3/results', exist_ok=True)
    main()
