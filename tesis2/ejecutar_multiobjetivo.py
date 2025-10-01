"""
Script para ejecutar el algoritmo evolutivo multiobjetivo (NSGA-II)
con 4 objetivos y visualizar el frente de Pareto resultante
"""

from Algoritmo_evo.nsga2_multiobjetivo import algoritmo_evolutivo_multiobjetivo
from Poblacion.Fun_poblacion import inicializar_poblacion
from Cruce.funciones_cruce import *  # Asegúrate de importar tus funciones de cruce
from Mutacion.mutacion_funciones import *  # Asegúrate de importar tus funciones de mutación
from Parametros.Parametros_tot import *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time


# Configuración del experimento
configuracion = {
    'metodo_cruce': cruce_1_punto,  # Cambia según tu implementación
    'metodo_mutacion': mutacion_intercambio_por_etapa,  # Cambia según tu implementación
    'prob_cruz': 0.95,
    'prob_mut': 0.3,
    'tamano_poblacion': 50,
    'num_generaciones': 300
}

print("="*80)
print("ALGORITMO EVOLUTIVO MULTIOBJETIVO - NSGA-II (4 OBJETIVOS)")
print("Problema: Hybrid Flow Shop Scheduling")
print("="*80)
print(f"\n📋 CONFIGURACIÓN:")
print(f"   Método de cruce: {configuracion['metodo_cruce'].__name__}")
print(f"   Método de mutación: {configuracion['metodo_mutacion'].__name__}")
print(f"   Probabilidad de cruce: {configuracion['prob_cruz']}")
print(f"   Probabilidad de mutación: {configuracion['prob_mut']}")
print(f"   Tamaño de población: {configuracion['tamano_poblacion']}")
print(f"   Número de generaciones: {configuracion['num_generaciones']}")
print(f"   Número de pedidos: {num_pedidos}")
print("="*80)

# Inicializar población
print("\n🔄 Inicializando población...")
poblacion_inicial = inicializar_poblacion(
    tamano_poblacion=configuracion['tamano_poblacion'],
    maquinas_por_etapa=maquinas_por_etapa,
    num_pedidos=num_pedidos
)

# Ejecutar algoritmo
print("🚀 Ejecutando NSGA-II...\n")
inicio = time.time()

frente_pareto, fitness_pareto, historial_frentes = algoritmo_evolutivo_multiobjetivo(
    poblacion_inicial,
    None,  # NSGA-II no usa selección externa
    configuracion['metodo_cruce'],
    configuracion['metodo_mutacion'],
    prob_cruz=configuracion['prob_cruz'],
    prob_mut=configuracion['prob_mut'],
    tamano_poblacion=configuracion['tamano_poblacion'],
    num_generaciones=configuracion['num_generaciones']
)

fin = time.time()

print("="*80)
print("📊 RESULTADOS FINALES")
print("="*80)
print(f"⏱️  Tiempo de ejecución: {fin - inicio:.2f} segundos")
print(f"🎯 Soluciones en el Frente de Pareto: {len(frente_pareto)}")
print("\n" + "="*80)
print("TOP 5 SOLUCIONES DEL FRENTE DE PARETO")
print("="*80)

# Convertir fitness a métricas reales
metricas_reales = []
for obj1, obj2, obj3, obj4 in fitness_pareto:
    makespan = 1/obj1
    balance = 1/obj2 - 1
    enfriamiento = 1/obj3 - 1
    energia = 1/obj4 - 1
    metricas_reales.append((makespan, balance, enfriamiento, energia))

# Ordenar por makespan
top_indices = sorted(range(len(metricas_reales)), key=lambda i: metricas_reales[i][0])[:5]

print(f"\n{'#':<4} {'Makespan (s)':<15} {'Balance (std)':<18} {'Penaliz Enf.':<16} {'Energía (kWh)':<15}")
print("-"*80)
for rank, idx in enumerate(top_indices, 1):
    mk, bal, enf, eng = metricas_reales[idx]
    print(f"{rank:<4} {mk:<15.2f} {bal:<18.2f} {enf:<16.2f} {eng:<15.2f}")

print("\n" + "="*80)
print("📈 ESTADÍSTICAS DEL FRENTE DE PARETO")
print("="*80)

makespans = [m[0] for m in metricas_reales]
balances = [m[1] for m in metricas_reales]
enfriamientos = [m[2] for m in metricas_reales]
energias = [m[3] for m in metricas_reales]

print(f"\n🔹 MAKESPAN:")
print(f"   Mínimo: {min(makespans):.2f}s")
print(f"   Máximo: {max(makespans):.2f}s")
print(f"   Promedio: {np.mean(makespans):.2f}s")
print(f"   Desviación: {np.std(makespans):.2f}s")

print(f"\n🔹 BALANCE DE CARGA:")
print(f"   Mínimo: {min(balances):.2f}s")
print(f"   Máximo: {max(balances):.2f}s")
print(f"   Promedio: {np.mean(balances):.2f}s")

print(f"\n🔹 PENALIZACIÓN POR ENFRIAMIENTO:")
print(f"   Mínimo: {min(enfriamientos):.2f}")
print(f"   Máximo: {max(enfriamientos):.2f}")
print(f"   Promedio: {np.mean(enfriamientos):.2f}")

print(f"\n🔹 CONSUMO ENERGÉTICO:")
print(f"   Mínimo: {min(energias):.2f} kWh")
print(f"   Máximo: {max(energias):.2f} kWh")
print(f"   Promedio: {np.mean(energias):.2f} kWh")

# ===== VISUALIZACIONES =====

# 1. Gráficos del Frente de Pareto
fig = plt.figure(figsize=(16, 12))

# Subplot 1: Makespan vs Balance vs Enfriamiento (3D)
ax1 = fig.add_subplot(331, projection='3d')
scatter1 = ax1.scatter(makespans, balances, enfriamientos, c=energias, 
                       cmap='viridis', marker='o', s=50, alpha=0.6)
ax1.set_xlabel('Makespan (s)', fontsize=9)
ax1.set_ylabel('Balance (Desv. Std)', fontsize=9)
ax1.set_zlabel('Penalización Enfriamiento', fontsize=9)
ax1.set_title('Frente Pareto 3D (color=Energía)', fontsize=10, fontweight='bold')
plt.colorbar(scatter1, ax=ax1, label='Energía (kWh)', shrink=0.5)

# Subplot 2: Makespan vs Balance
ax2 = fig.add_subplot(332)
ax2.scatter(makespans, balances, c='green', marker='o', s=50, alpha=0.6)
ax2.set_xlabel('Makespan (s)', fontsize=9)
ax2.set_ylabel('Balance (Desv. Std)', fontsize=9)
ax2.set_title('Makespan vs Balance', fontsize=10, fontweight='bold')
ax2.grid(True, alpha=0.3)

# Subplot 3: Makespan vs Enfriamiento
ax3 = fig.add_subplot(333)
ax3.scatter(makespans, enfriamientos, c='red', marker='o', s=50, alpha=0.6)
ax3.set_xlabel('Makespan (s)', fontsize=9)
ax3.set_ylabel('Penalización Enfriamiento', fontsize=9)
ax3.set_title('Makespan vs Enfriamiento', fontsize=10, fontweight='bold')
ax3.grid(True, alpha=0.3)

# Subplot 4: Makespan vs Energía
ax4 = fig.add_subplot(334)
ax4.scatter(makespans, energias, c='orange', marker='o', s=50, alpha=0.6)
ax4.set_xlabel('Makespan (s)', fontsize=9)
ax4.set_ylabel('Energía (kWh)', fontsize=9)
ax4.set_title('Makespan vs Consumo Energético', fontsize=10, fontweight='bold')
ax4.grid(True, alpha=0.3)

# Subplot 5: Balance vs Enfriamiento
ax5 = fig.add_subplot(335)
ax5.scatter(balances, enfriamientos, c='purple', marker='o', s=50, alpha=0.6)
ax5.set_xlabel('Balance (Desv. Std)', fontsize=9)
ax5.set_ylabel('Penalización Enfriamiento', fontsize=9)
ax5.set_title('Balance vs Enfriamiento', fontsize=10, fontweight='bold')
ax5.grid(True, alpha=0.3)

# Subplot 6: Balance vs Energía
ax6 = fig.add_subplot(336)
ax6.scatter(balances, energias, c='brown', marker='o', s=50, alpha=0.6)
ax6.set_xlabel('Balance (Desv. Std)', fontsize=9)
ax6.set_ylabel('Energía (kWh)', fontsize=9)
ax6.set_title('Balance vs Consumo Energético', fontsize=10, fontweight='bold')
ax6.grid(True, alpha=0.3)

# Subplot 7: Enfriamiento vs Energía
ax7 = fig.add_subplot(337)
ax7.scatter(enfriamientos, energias, c='teal', marker='o', s=50, alpha=0.6)
ax7.set_xlabel('Penalización Enfriamiento', fontsize=9)
ax7.set_ylabel('Energía (kWh)', fontsize=9)
ax7.set_title('Enfriamiento vs Consumo Energético', fontsize=10, fontweight='bold')
ax7.grid(True, alpha=0.3)

# Subplot 8: Diagrama de cajas de todos los objetivos
ax8 = fig.add_subplot(338)
datos_normalizados = [
    (np.array(makespans) - min(makespans)) / (max(makespans) - min(makespans)),
    (np.array(balances) - min(balances)) / (max(balances) - min(balances)) if max(balances) > min(balances) else np.array(balances),
    (np.array(enfriamientos) - min(enfriamientos)) / (max(enfriamientos) - min(enfriamientos)) if max(enfriamientos) > min(enfriamientos) else np.array(enfriamientos),
    (np.array(energias) - min(energias)) / (max(energias) - min(energias))
]
ax8.boxplot(datos_normalizados, labels=['Makespan', 'Balance', 'Enfriamiento', 'Energía'])
ax8.set_ylabel('Valores Normalizados', fontsize=9)
ax8.set_title('Distribución de Objetivos (Normalizado)', fontsize=10, fontweight='bold')
ax8.grid(True, alpha=0.3, axis='y')

# Subplot 9: Correlación entre objetivos
ax9 = fig.add_subplot(339)
correlacion = np.corrcoef([makespans, balances, enfriamientos, energias])
im = ax9.imshow(correlacion, cmap='coolwarm', vmin=-1, vmax=1)
ax9.set_xticks(range(4))
ax9.set_yticks(range(4))
ax9.set_xticklabels(['MK', 'Bal', 'Enf', 'Eng'], fontsize=9)
ax9.set_yticklabels(['MK', 'Bal', 'Enf', 'Eng'], fontsize=9)
ax9.set_title('Matriz de Correlación', fontsize=10, fontweight='bold')
for i in range(4):
    for j in range(4):
        text = ax9.text(j, i, f'{correlacion[i, j]:.2f}',
                       ha="center", va="center", color="black", fontsize=8)
plt.colorbar(im, ax=ax9, shrink=0.8)

plt.tight_layout()
plt.savefig('frente_pareto_4_objetivos.png', dpi=300, bbox_inches='tight')
print(f"\n💾 Gráfico guardado: frente_pareto_4_objetivos.png")

# 2. Evolución del tamaño del Frente de Pareto
fig2, ax10 = plt.subplots(figsize=(12, 6))
generaciones = list(range(1, len(historial_frentes) + 1))
ax10.plot(generaciones, historial_frentes, color='darkblue', linewidth=2)
ax10.fill_between(generaciones, historial_frentes, alpha=0.3, color='lightblue')
ax10.set_xlabel('Generación', fontsize=12)
ax10.set_ylabel('Tamaño del Frente de Pareto', fontsize=12)
ax10.set_title('Evolución del Frente de Pareto', fontsize=14, fontweight='bold')
ax10.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('evolucion_frente_pareto_4obj.png', dpi=300, bbox_inches='tight')
print(f"💾 Gráfico guardado: evolucion_frente_pareto_4obj.png")

plt.show()

# Guardar resultados en archivo CSV
print("\n💾 Guardando resultados en CSV...")
import csv

with open('resultados_multiobjetivo_4obj.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Indice', 'Makespan', 'Balance', 'Penalizacion_Enfriamiento', 'Energia_kWh',
                     'Fitness_Makespan', 'Fitness_Balance', 'Fitness_Enfriamiento', 'Fitness_Energia'])
    
    for i, ((mk, bal, enf, eng), (f1, f2, f3, f4)) in enumerate(zip(metricas_reales, fitness_pareto)):
        writer.writerow([i+1, f"{mk:.4f}", f"{bal:.4f}", f"{enf:.4f}", f"{eng:.4f}",
                        f"{f1:.8f}", f"{f2:.8f}", f"{f3:.8f}", f"{f4:.8f}"])

print("✅ Resultados guardados en: resultados_multiobjetivo_4obj.csv")

print("\n" + "="*80)
print("🎉 PROCESO COMPLETADO")
print("="*80)
print("\n📝 PRÓXIMOS PASOS:")
print("   1. Analizar el frente de Pareto para identificar soluciones de compromiso")
print("   2. Seleccionar una solución según preferencias del decisor")
print("   3. Analizar correlaciones entre objetivos en la matriz")
print("   4. Comparar con el enfoque mono-objetivo anterior")
print("   5. Realizar análisis de sensibilidad con diferentes configuraciones")
print("="*80 + "\n")

print("="*80)
print("ALGORITMO EVOLUTIVO MULTIOBJETIVO - NSGA-II")
print("Problema: Hybrid Flow Shop Scheduling")
print("="*80)
print(f"\n📋 CONFIGURACIÓN:")
print(f"   Método de cruce: {configuracion['metodo_cruce'].__name__}")
print(f"   Método de mutación: {configuracion['metodo_mutacion'].__name__}")
print(f"   Probabilidad de cruce: {configuracion['prob_cruz']}")
print(f"   Probabilidad de mutación: {configuracion['prob_mut']}")
print(f"   Tamaño de población: {configuracion['tamano_poblacion']}")
print(f"   Número de generaciones: {configuracion['num_generaciones']}")
print(f"   Número de pedidos: {num_pedidos}")
print("="*80)

# Inicializar población
print("\n🔄 Inicializando población...")
poblacion_inicial = inicializar_poblacion(
    tamano_poblacion=configuracion['tamano_poblacion'],
    maquinas_por_etapa=maquinas_por_etapa,
    num_pedidos=num_pedidos
)

# Ejecutar algoritmo
print("🚀 Ejecutando NSGA-II...\n")
inicio = time.time()

frente_pareto, fitness_pareto, historial_frentes = algoritmo_evolutivo_multiobjetivo(
    poblacion_inicial,
    None,  # NSGA-II no usa selección externa
    configuracion['metodo_cruce'],
    configuracion['metodo_mutacion'],
    prob_cruz=configuracion['prob_cruz'],
    prob_mut=configuracion['prob_mut'],
    tamano_poblacion=configuracion['tamano_poblacion'],
    num_generaciones=configuracion['num_generaciones']
)

fin = time.time()

print("="*80)
print("📊 RESULTADOS FINALES")
print("="*80)
print(f"⏱️  Tiempo de ejecución: {fin - inicio:.2f} segundos")
print(f"🎯 Soluciones en el Frente de Pareto: {len(frente_pareto)}")
print("\n" + "="*80)
print("TOP 5 SOLUCIONES DEL FRENTE DE PARETO")
print("="*80)

# Convertir fitness a métricas reales
metricas_reales = []
for obj1, obj2, obj3 in fitness_pareto:
    makespan = 1/obj1
    balance = 1/obj2 - 1
    enfriamiento = 1/obj3 - 1
    metricas_reales.append((makespan, balance, enfriamiento))

# Ordenar por makespan
top_indices = sorted(range(len(metricas_reales)), key=lambda i: metricas_reales[i][0])[:5]

print(f"\n{'#':<4} {'Makespan (s)':<15} {'Balance (std)':<18} {'Penalización Enf.':<20}")
print("-"*80)
for rank, idx in enumerate(top_indices, 1):
    mk, bal, enf = metricas_reales[idx]
    print(f"{rank:<4} {mk:<15.2f} {bal:<18.2f} {enf:<20.2f}")

print("\n" + "="*80)
print("📈 ESTADÍSTICAS DEL FRENTE DE PARETO")
print("="*80)

makespans = [m[0] for m in metricas_reales]
balances = [m[1] for m in metricas_reales]
enfriamientos = [m[2] for m in metricas_reales]

print(f"\n🔹 MAKESPAN:")
print(f"   Mínimo: {min(makespans):.2f}s")
print(f"   Máximo: {max(makespans):.2f}s")
print(f"   Promedio: {np.mean(makespans):.2f}s")
print(f"   Desviación: {np.std(makespans):.2f}s")

print(f"\n🔹 BALANCE DE CARGA:")
print(f"   Mínimo: {min(balances):.2f}s")
print(f"   Máximo: {max(balances):.2f}s")
print(f"   Promedio: {np.mean(balances):.2f}s")

print(f"\n🔹 PENALIZACIÓN POR ENFRIAMIENTO:")
print(f"   Mínimo: {min(enfriamientos):.2f}")
print(f"   Máximo: {max(enfriamientos):.2f}")
print(f"   Promedio: {np.mean(enfriamientos):.2f}")

# ===== VISUALIZACIONES =====

# 1. Gráfico 3D del Frente de Pareto
fig = plt.figure(figsize=(14, 10))

# Subplot 1: Frente de Pareto 3D
ax1 = fig.add_subplot(221, projection='3d')
ax1.scatter(makespans, balances, enfriamientos, c='blue', marker='o', s=50, alpha=0.6)
ax1.set_xlabel('Makespan (s)', fontsize=10)
ax1.set_ylabel('Balance (Desv. Std)', fontsize=10)
ax1.set_zlabel('Penalización Enfriamiento', fontsize=10)
ax1.set_title('Frente de Pareto 3D', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)

# Subplot 2: Makespan vs Balance
ax2 = fig.add_subplot(222)
ax2.scatter(makespans, balances, c='green', marker='o', s=50, alpha=0.6)
ax2.set_xlabel('Makespan (s)', fontsize=10)
ax2.set_ylabel('Balance (Desv. Std)', fontsize=10)
ax2.set_title('Makespan vs Balance de Carga', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)

# Subplot 3: Makespan vs Enfriamiento
ax3 = fig.add_subplot(223)
ax3.scatter(makespans, enfriamientos, c='red', marker='o', s=50, alpha=0.6)
ax3.set_xlabel('Makespan (s)', fontsize=10)
ax3.set_ylabel('Penalización Enfriamiento', fontsize=10)
ax3.set_title('Makespan vs Enfriamiento', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3)

# Subplot 4: Balance vs Enfriamiento
ax4 = fig.add_subplot(224)
ax4.scatter(balances, enfriamientos, c='purple', marker='o', s=50, alpha=0.6)
ax4.set_xlabel('Balance (Desv. Std)', fontsize=10)
ax4.set_ylabel('Penalización Enfriamiento', fontsize=10)
ax4.set_title('Balance vs Enfriamiento', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('frente_pareto_multiobjetivo.png', dpi=300, bbox_inches='tight')
print(f"\n💾 Gráfico guardado: frente_pareto_multiobjetivo.png")

# 2. Evolución del tamaño del Frente de Pareto
fig2, ax5 = plt.subplots(figsize=(12, 6))
generaciones = list(range(1, len(historial_frentes) + 1))
ax5.plot(generaciones, historial_frentes, color='darkblue', linewidth=2)
ax5.fill_between(generaciones, historial_frentes, alpha=0.3, color='lightblue')
ax5.set_xlabel('Generación', fontsize=12)
ax5.set_ylabel('Tamaño del Frente de Pareto', fontsize=12)
ax5.set_title('Evolución del Frente de Pareto', fontsize=14, fontweight='bold')
ax5.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('evolucion_frente_pareto.png', dpi=300, bbox_inches='tight')
print(f"💾 Gráfico guardado: evolucion_frente_pareto.png")

plt.show()

# Guardar resultados en archivo CSV
print("\n💾 Guardando resultados en CSV...")
import csv

with open('resultados_multiobjetivo.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Indice', 'Makespan', 'Balance', 'Penalizacion_Enfriamiento', 
                     'Fitness_Makespan', 'Fitness_Balance', 'Fitness_Enfriamiento'])
    
    for i, ((mk, bal, enf), (f1, f2, f3)) in enumerate(zip(metricas_reales, fitness_pareto)):
        writer.writerow([i+1, f"{mk:.4f}", f"{bal:.4f}", f"{enf:.4f}", 
                        f"{f1:.8f}", f"{f2:.8f}", f"{f3:.8f}"])

print("✅ Resultados guardados en: resultados_multiobjetivo.csv")

print("\n" + "="*80)
print("🎉 PROCESO COMPLETADO")
print("="*80)
print("\n📝 PRÓXIMOS PASOS:")
print("   1. Analizar el frente de Pareto para identificar soluciones de compromiso")
print("   2. Seleccionar una solución según preferencias del decisor")
print("   3. Comparar con el enfoque mono-objetivo anterior")
print("   4. Realizar análisis de sensibilidad con diferentes configuraciones")
print("="*80 + "\n")