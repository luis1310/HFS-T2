#!/usr/bin/env python3
"""Prueba de continuación automática - Solo detecta, no ejecuta"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tesis3.src.core.problem import ProblemConfig
import glob
import csv
from itertools import product

def detectar_resultados_previos():
    """Detecta y carga resultados de ejecuciones previas"""
    print("🔍 Detectando resultados previos...")
    
    # Buscar archivos parciales
    archivos_parciales = glob.glob('tesis3/results/tunning_multimetrica_parcial_*.csv')
    archivos_finales = glob.glob('tesis3/results/tunning_multimetrica_real_*.csv')
    
    print(f"   Archivos parciales encontrados: {len(archivos_parciales)}")
    print(f"   Archivos finales encontrados: {len(archivos_finales)}")
    
    # Cargar todos los resultados previos
    configuraciones_completas_previas = set()
    
    # Cargar desde archivos parciales
    for archivo in archivos_parciales:
        try:
            with open(archivo, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convertir a formato interno
                    configuracion = {
                        'tamano_poblacion': int(row['tamano_poblacion']),
                        'num_generaciones': int(row['num_generaciones']),
                        'prob_cruce': float(row['prob_cruce']),
                        'prob_mutacion': float(row['prob_mutacion']),
                        'cada_k_gen': int(row['cada_k_gen']),
                        'max_iter_local': int(row['max_iter_local'])
                    }
                    config_key = tuple(sorted(configuracion.items()))
                    configuraciones_completas_previas.add(config_key)
                    print(f"   ✅ Configuración completa detectada: {configuracion}")
        except Exception as e:
            print(f"   ⚠️ Error leyendo {archivo}: {e}")
    
    # Cargar desde archivos finales
    for archivo in archivos_finales:
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
                    configuraciones_completas_previas.add(config_key)
        except Exception as e:
            print(f"   ⚠️ Error leyendo {archivo}: {e}")
    
    print(f"   📊 Total configuraciones completas previas: {len(configuraciones_completas_previas)}")
    return configuraciones_completas_previas

def main():
    print("="*70)
    print("PRUEBA DE CONTINUACIÓN AUTOMÁTICA")
    print("="*70)
    
    # Definir espacio de búsqueda
    espacio_busqueda = {
        'tamano_poblacion': [100, 200],
        'num_generaciones': [400, 600],
        'prob_cruce': [0.8, 0.9],
        'prob_mutacion': [0.1, 0.15],
        'cada_k_gen': [5, 10],
        'max_iter_local': [3, 5]
    }
    
    # Generar todas las combinaciones
    combinaciones = list(product(*espacio_busqueda.values()))
    combinaciones = [dict(zip(espacio_busqueda.keys(), combo)) for combo in combinaciones]
    
    print(f"Total de combinaciones: {len(combinaciones)}")
    
    # Detectar resultados previos
    configuraciones_completas_previas = detectar_resultados_previos()
    
    # Filtrar configuraciones que ya están completas
    combinaciones_faltantes = []
    for combo in combinaciones:
        config_key = tuple(sorted(combo.items()))
        if config_key not in configuraciones_completas_previas:
            combinaciones_faltantes.append(combo)
    
    print(f"\n📊 RESUMEN:")
    print(f"   Configuraciones totales: {len(combinaciones)}")
    print(f"   Configuraciones completas previas: {len(configuraciones_completas_previas)}")
    print(f"   Configuraciones faltantes: {len(combinaciones_faltantes)}")
    
    if len(combinaciones_faltantes) == 0:
        print("\n🎉 ¡Todas las configuraciones ya están completas!")
        print("   No hay trabajo pendiente.")
        return
    
    print(f"\n⏳ Configuraciones que se ejecutarían:")
    for i, config in enumerate(combinaciones_faltantes[:10], 1):
        print(f"   {i}. Pob:{config['tamano_poblacion']} Gen:{config['num_generaciones']} "
              f"PC:{config['prob_cruce']:.1f} PM:{config['prob_mutacion']:.2f} "
              f"K:{config['cada_k_gen']} IL:{config['max_iter_local']}")
    
    if len(combinaciones_faltantes) > 10:
        print(f"   ... y {len(combinaciones_faltantes) - 10} más")
    
    print(f"\n⏰ Tiempo estimado: {len(combinaciones_faltantes) * 30 * 2 / 6 / 60:.1f} horas")
    print(f"📝 Total de ejecuciones: {len(combinaciones_faltantes) * 30}")
    
    print("\n" + "="*70)
    print("✅ EL SCRIPT DETECTARÍA AUTOMÁTICAMENTE ESTE ESTADO")
    print("="*70)

if __name__ == "__main__":
    main()
