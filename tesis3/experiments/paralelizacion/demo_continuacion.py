#!/usr/bin/env python3
"""Demo de continuación automática de experimentos"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import glob
import csv

def analizar_estado_actual():
    """Analiza el estado actual de los experimentos"""
    print("="*70)
    print("ANÁLISIS DEL ESTADO ACTUAL DE EXPERIMENTOS")
    print("="*70)
    
    # Buscar archivos de resultados
    archivos_parciales = glob.glob('tesis3/results/tunning_multimetrica_parcial_*.csv')
    archivos_finales = glob.glob('tesis3/results/tunning_multimetrica_real_*.csv')
    
    print(f"📁 Archivos encontrados:")
    print(f"   Archivos parciales: {len(archivos_parciales)}")
    print(f"   Archivos finales: {len(archivos_finales)}")
    
    # Analizar configuraciones completas
    configuraciones_completas = set()
    
    for archivo in archivos_parciales + archivos_finales:
        try:
            with open(archivo, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    configuracion = {
                        'tamano_poblacion': int(row['tamano_poblacion']),
                        'num_generaciones': int(row['num_generaciones']),
                        'prob_cruce': float(row['prob_cruce']),
                        'prob_mutacion': float(row['prob_mutacion']),
                        'cada_k_gen': int(row['cada_k_gen']),
                        'max_iter_local': int(row['max_iter_local'])
                    }
                    config_key = tuple(sorted(configuracion.items()))
                    configuraciones_completas.add(config_key)
        except Exception as e:
            print(f"   ⚠️ Error leyendo {archivo}: {e}")
    
    print(f"\n📊 RESUMEN:")
    print(f"   Configuraciones completas: {len(configuraciones_completas)}")
    
    # Mostrar algunas configuraciones completas
    if configuraciones_completas:
        print(f"\n✅ Configuraciones completas encontradas:")
        for i, config_key in enumerate(list(configuraciones_completas)[:5], 1):
            config = dict(config_key)
            print(f"   {i}. Pob:{config['tamano_poblacion']} Gen:{config['num_generaciones']} "
                  f"PC:{config['prob_cruce']:.1f} PM:{config['prob_mutacion']:.2f} "
                  f"K:{config['cada_k_gen']} IL:{config['max_iter_local']}")
        
        if len(configuraciones_completas) > 5:
            print(f"   ... y {len(configuraciones_completas) - 5} más")
    
    # Calcular configuraciones faltantes
    espacio_busqueda = {
        'tamano_poblacion': [100, 200],
        'num_generaciones': [400, 600],
        'prob_cruce': [0.8, 0.9],
        'prob_mutacion': [0.1, 0.15],
        'cada_k_gen': [5, 10],
        'max_iter_local': [3, 5]
    }
    
    from itertools import product
    combinaciones_totales = list(product(*espacio_busqueda.values()))
    combinaciones_totales = [dict(zip(espacio_busqueda.keys(), combo)) for combo in combinaciones_totales]
    
    configuraciones_faltantes = []
    for combo in combinaciones_totales:
        config_key = tuple(sorted(combo.items()))
        if config_key not in configuraciones_completas:
            configuraciones_faltantes.append(combo)
    
    print(f"\n📈 PROGRESO:")
    print(f"   Total configuraciones: {len(combinaciones_totales)}")
    print(f"   Completadas: {len(configuraciones_completas)}")
    print(f"   Faltantes: {len(configuraciones_faltantes)}")
    print(f"   Progreso: {len(configuraciones_completas)/len(combinaciones_totales)*100:.1f}%")
    
    if configuraciones_faltantes:
        print(f"\n⏳ Configuraciones faltantes (primeras 5):")
        for i, config in enumerate(configuraciones_faltantes[:5], 1):
            print(f"   {i}. Pob:{config['tamano_poblacion']} Gen:{config['num_generaciones']} "
                  f"PC:{config['prob_cruce']:.1f} PM:{config['prob_mutacion']:.2f} "
                  f"K:{config['cada_k_gen']} IL:{config['max_iter_local']}")
        
        if len(configuraciones_faltantes) > 5:
            print(f"   ... y {len(configuraciones_faltantes) - 5} más")
    
    return len(configuraciones_completas), len(configuraciones_faltantes)

def main():
    print("🔍 DEMO: Continuación automática de experimentos")
    print()
    
    # Analizar estado actual
    completadas, faltantes = analizar_estado_actual()
    
    print("\n" + "="*70)
    print("¿QUÉ PASA AL EJECUTAR tunning_multimetrica.py?")
    print("="*70)
    
    if faltantes == 0:
        print("🎉 ¡Todas las configuraciones ya están completas!")
        print("   El script detectará esto y terminará inmediatamente.")
        print("   No se ejecutará ningún trabajo adicional.")
    else:
        print(f"✅ El script detectará automáticamente:")
        print(f"   - {completadas} configuraciones ya completas")
        print(f"   - {faltantes} configuraciones faltantes")
        print(f"   - Solo ejecutará las {faltantes} configuraciones faltantes")
        print(f"   - Tiempo estimado: {faltantes * 30 * 2 / 6 / 60:.1f} horas")
    
    print("\n🚀 VENTAJAS DE LA CONTINUACIÓN AUTOMÁTICA:")
    print("   ✅ No duplica trabajo ya realizado")
    print("   ✅ Continúa exactamente donde se quedó")
    print("   ✅ Combina resultados automáticamente")
    print("   ✅ Guarda con timestamp único")
    print("   ✅ Detecta configuraciones completas")
    
    print("\n💡 CÓMO USAR:")
    print("   1. Ejecutar: python3 tesis3/experiments/paralelizacion/tunning_multimetrica.py")
    print("   2. Seleccionar núcleos")
    print("   3. El script detectará automáticamente el progreso")
    print("   4. Solo ejecutará las configuraciones faltantes")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
