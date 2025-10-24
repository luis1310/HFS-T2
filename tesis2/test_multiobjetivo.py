# Script de prueba para comparar evaluación mono-objetivo vs multiobjetivo (4 objetivos)
# Asume que tienes el archivo fitness_multiobjetivo.py en la carpeta Aptitud/

from Aptitud.funcion_fitness import fitness
from Aptitud.funcion_fitness_multiobjetivo import fitness_multiobjetivo, fitness_multiobjetivo_demo
from Parametros.Parametros_tot import *

# Ejemplos de cromosomas para prueba
cromosoma1 = [[1, 4, 6, 10, 11], [2, 5, 8, 9, 11], [3, 5, 6, 10, 11]]
cromosoma2 = [[2, 4, 7, 10, 11], [2, 5, 7, 10, 11], [2, 4, 7, 9, 11]]
cromosoma3 = [[1, 4, 6, 10, 11], [2, 5, 8, 9, 11], [3, 5, 6, 10, 11], [2, 4, 7, 9, 11]]

print("="*80)
print("COMPARACIÓN: MONO-OBJETIVO vs MULTIOBJETIVO (4 OBJETIVOS)")
print("="*80)

# Cromosoma 1
print("\n" + "█"*80)
print("CROMOSOMA 1 (3 pedidos)")
print("█"*80)

print("\n EVALUACIÓN MONO-OBJETIVO (solo Makespan):")
fit1_mono = fitness(cromosoma1)
print(f"   Fitness: {fit1_mono:.8f}")
print(f"   Makespan: {1/fit1_mono:.2f}s")

print("\n EVALUACIÓN MULTIOBJETIVO (4 objetivos):")
obj1_mk, obj1_bal, obj1_enf, obj1_eng = fitness_multiobjetivo_demo(cromosoma1)

# Cromosoma 2
print("\n" + "█"*80)
print("CROMOSOMA 2 (3 pedidos)")
print("█"*80)

print("\n EVALUACIÓN MONO-OBJETIVO (solo Makespan):")
fit2_mono = fitness(cromosoma2)
print(f"   Fitness: {fit2_mono:.8f}")
print(f"   Makespan: {1/fit2_mono:.2f}s")

print("\n EVALUACIÓN MULTIOBJETIVO (4 objetivos):")
obj2_mk, obj2_bal, obj2_enf, obj2_eng = fitness_multiobjetivo_demo(cromosoma2)

# Cromosoma 3
print("\n" + "█"*80)
print("CROMOSOMA 3 (4 pedidos)")
print("█"*80)

print("\n EVALUACIÓN MONO-OBJETIVO (solo Makespan):")
fit3_mono = fitness(cromosoma3)
print(f"   Fitness: {fit3_mono:.8f}")
print(f"   Makespan: {1/fit3_mono:.2f}s")

print("\n EVALUACIÓN MULTIOBJETIVO (4 objetivos):")
obj3_mk, obj3_bal, obj3_enf, obj3_eng = fitness_multiobjetivo_demo(cromosoma3)

# Resumen comparativo
print("\n" + "="*80)
print("TABLA COMPARATIVA DE RESULTADOS")
print("="*80)
print(f"\n{'Cromosoma':<12} | {'Makespan':<12} | {'Balance':<12} | {'Enfriamiento':<14} | {'Energía (kWh)':<15}")
print("-"*80)
print(f"{'Cromosoma 1':<12} | {1/obj1_mk:<12.2f} | {1/obj1_bal - 1:<12.2f} | {1/obj1_enf - 1:<14.2f} | {1/obj1_eng - 1:<15.2f}")
print(f"{'Cromosoma 2':<12} | {1/obj2_mk:<12.2f} | {1/obj2_bal - 1:<12.2f} | {1/obj2_enf - 1:<14.2f} | {1/obj2_eng - 1:<15.2f}")
print(f"{'Cromosoma 3':<12} | {1/obj3_mk:<12.2f} | {1/obj3_bal - 1:<12.2f} | {1/obj3_enf - 1:<14.2f} | {1/obj3_eng - 1:<15.2f}")
print("="*80)

print("\n INTERPRETACIÓN:")
print("   - Makespan: Tiempo total de finalización (menor es mejor)")
print("   - Balance: Desviación estándar entre máquinas (menor es mejor)")
print("   - Enfriamiento: Penalización por enfriamientos (menor es mejor)")
print("   - Energía: Consumo energético total en kWh (menor es mejor)")

print("\n ANÁLISIS DE TRADE-OFFS:")
print("   Observa cómo diferentes cromosomas pueden ser mejores en objetivos específicos:")
print("   - Un cromosoma puede tener menor makespan pero mayor consumo energético")
print("   - Otro puede tener mejor balance pero más enfriamientos")
print("   - El algoritmo multiobjetivo encuentra el mejor COMPROMISO entre todos")

print("\n" + "="*80)