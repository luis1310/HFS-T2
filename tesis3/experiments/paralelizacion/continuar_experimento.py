import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pandas as pd
import glob
import os
from datetime import datetime

def analizar_progreso_experimento(tipo_experimento):
    """
    Analiza el progreso de un experimento y muestra qué configuraciones faltan
    
    Args:
        tipo_experimento: 'tunning', 'comparacion', o 'prueba_rapida'
    """
    print(f"="*70)
    print(f"ANALIZANDO PROGRESO - {tipo_experimento.upper()}")
    print(f"="*70)
    
    # Patrones de archivos según el tipo
    patrones = {
        'tunning': 'tesis3/results/tunning_multimetrica_parcial_*.csv',
        'comparacion': 'tesis3/results/comparacion_operadores_parcial_*.csv',
        'prueba_rapida': 'tesis3/results/prueba_rapida_parcial_*.csv'
    }
    
    if tipo_experimento not in patrones:
        print(f"❌ Tipo de experimento no válido: {tipo_experimento}")
        return
    
    patron = patrones[tipo_experimento]
    archivos = glob.glob(patron)
    
    if not archivos:
        print(f"❌ No se encontraron archivos parciales para {tipo_experimento}")
        return
    
    print(f"📁 Archivos encontrados: {len(archivos)}")
    
    # Leer todos los archivos y combinar
    dataframes = []
    for archivo in sorted(archivos):
        try:
            df = pd.read_csv(archivo)
            dataframes.append(df)
        except Exception as e:
            print(f"❌ Error leyendo {archivo}: {e}")
    
    if not dataframes:
        print(f"❌ No se pudieron leer archivos")
        return
    
    # Combinar todos los dataframes
    df_combinado = pd.concat(dataframes, ignore_index=True)
    
    # Eliminar duplicados (por si hay configuraciones repetidas)
    if tipo_experimento == 'tunning' or tipo_experimento == 'prueba_rapida':
        df_combinado = df_combinado.drop_duplicates(subset=[
            'tamano_poblacion', 'num_generaciones', 'prob_cruce', 
            'prob_mutacion', 'cada_k_gen', 'max_iter_local'
        ])
    else:
        df_combinado = df_combinado.drop_duplicates(subset=['configuracion_nombre'])
    
    print(f"\n📊 PROGRESO ACTUAL:")
    print(f"   Configuraciones completadas: {len(df_combinado)}")
    
    # Mostrar configuraciones completadas
    print(f"\n✅ CONFIGURACIONES COMPLETADAS:")
    print("-" * 80)
    
    for i, (_, row) in enumerate(df_combinado.iterrows(), 1):
        if tipo_experimento == 'tunning' or tipo_experimento == 'prueba_rapida':
            print(f"{i:2d}. Pob:{row['tamano_poblacion']} Gen:{row['num_generaciones']} "
                  f"PC:{row['prob_cruce']} PM:{row['prob_mutacion']} "
                  f"K:{row['cada_k_gen']} IL:{row['max_iter_local']} "
                  f"Score:{row['prom_score']:.4f}")
        else:
            print(f"{i:2d}. {row['configuracion_nombre']} "
                  f"Score:{row['prom_score']:.4f}")
    
    # Calcular configuraciones faltantes
    configuraciones_faltantes = calcular_configuraciones_faltantes(tipo_experimento, df_combinado)
    
    if configuraciones_faltantes:
        print(f"\n❌ CONFIGURACIONES FALTANTES: {len(configuraciones_faltantes)}")
        print("-" * 80)
        
        for i, config in enumerate(configuraciones_faltantes, 1):
            if tipo_experimento == 'tunning' or tipo_experimento == 'prueba_rapida':
                print(f"{i:2d}. Pob:{config['tamano_poblacion']} Gen:{config['num_generaciones']} "
                      f"PC:{config['prob_cruce']} PM:{config['prob_mutacion']} "
                      f"K:{config['cada_k_gen']} IL:{config['max_iter_local']}")
            else:
                print(f"{i:2d}. {config['nombre']}")
    else:
        print(f"\n🎉 ¡TODAS LAS CONFIGURACIONES ESTÁN COMPLETAS!")
    
    return df_combinado, configuraciones_faltantes

def calcular_configuraciones_faltantes(tipo_experimento, df_completadas):
    """Calcula qué configuraciones faltan por completar"""
    
    if tipo_experimento == 'tunning':
        # Espacio de búsqueda del tunning
        espacio_busqueda = {
            'tamano_poblacion': [100, 200],
            'num_generaciones': [400, 600],
            'prob_cruce': [0.8, 0.9],
            'prob_mutacion': [0.1, 0.15],
            'cada_k_gen': [5, 10],
            'max_iter_local': [3, 5]
        }
        
        # Generar todas las combinaciones posibles
        from itertools import product
        todas_combinaciones = []
        for combo in product(*espacio_busqueda.values()):
            config = dict(zip(espacio_busqueda.keys(), combo))
            todas_combinaciones.append(config)
        
        # Encontrar las que faltan
        configuraciones_faltantes = []
        for config in todas_combinaciones:
            existe = False
            for _, row in df_completadas.iterrows():
                if (row['tamano_poblacion'] == config['tamano_poblacion'] and
                    row['num_generaciones'] == config['num_generaciones'] and
                    row['prob_cruce'] == config['prob_cruce'] and
                    row['prob_mutacion'] == config['prob_mutacion'] and
                    row['cada_k_gen'] == config['cada_k_gen'] and
                    row['max_iter_local'] == config['max_iter_local']):
                    existe = True
                    break
            
            if not existe:
                configuraciones_faltantes.append(config)
    
    elif tipo_experimento == 'comparacion':
        # Configuraciones de operadores
        configuraciones_operadores = [
            {'cruce': 'uniforme', 'mutacion': 'swap', 'nombre': 'Uniforme + Swap'},
            {'cruce': 'uniforme', 'mutacion': 'insert', 'nombre': 'Uniforme + Insert'},
            {'cruce': 'uniforme', 'mutacion': 'invert', 'nombre': 'Uniforme + Invert'},
            {'cruce': 'un_punto', 'mutacion': 'swap', 'nombre': '1-Punto + Swap'},
            {'cruce': 'un_punto', 'mutacion': 'insert', 'nombre': '1-Punto + Insert'},
            {'cruce': 'un_punto', 'mutacion': 'invert', 'nombre': '1-Punto + Invert'},
        ]
        
        configuraciones_faltantes = []
        for config in configuraciones_operadores:
            existe = False
            for _, row in df_completadas.iterrows():
                if row['configuracion_nombre'] == config['nombre']:
                    existe = True
                    break
            
            if not existe:
                configuraciones_faltantes.append(config)
    
    elif tipo_experimento == 'prueba_rapida':
        # Configuraciones de prueba rápida
        configuraciones_prueba = [
            {'tamano_poblacion': 100, 'num_generaciones': 400, 'prob_cruce': 0.8, 'prob_mutacion': 0.1, 'cada_k_gen': 5, 'max_iter_local': 3},
            {'tamano_poblacion': 200, 'num_generaciones': 600, 'prob_cruce': 0.9, 'prob_mutacion': 0.15, 'cada_k_gen': 10, 'max_iter_local': 5},
            {'tamano_poblacion': 150, 'num_generaciones': 500, 'prob_cruce': 0.85, 'prob_mutacion': 0.125, 'cada_k_gen': 7, 'max_iter_local': 4}
        ]
        
        configuraciones_faltantes = []
        for config in configuraciones_prueba:
            existe = False
            for _, row in df_completadas.iterrows():
                if (row['tamano_poblacion'] == config['tamano_poblacion'] and
                    row['num_generaciones'] == config['num_generaciones'] and
                    row['prob_cruce'] == config['prob_cruce'] and
                    row['prob_mutacion'] == config['prob_mutacion'] and
                    row['cada_k_gen'] == config['cada_k_gen'] and
                    row['max_iter_local'] == config['max_iter_local']):
                    existe = True
                    break
            
            if not existe:
                configuraciones_faltantes.append(config)
    
    return configuraciones_faltantes

def main():
    print("🔍 ANALIZADOR DE PROGRESO DE EXPERIMENTOS")
    print("="*70)
    
    print("\nTipos de experimentos disponibles:")
    print("1. tunning - Tunning multimétrica")
    print("2. comparacion - Comparación de operadores") 
    print("3. prueba_rapida - Prueba rápida")
    
    while True:
        try:
            opcion = input("\nSeleccione el tipo de experimento (1-3): ").strip()
            if opcion == "1":
                tipo = "tunning"
                break
            elif opcion == "2":
                tipo = "comparacion"
                break
            elif opcion == "3":
                tipo = "prueba_rapida"
                break
            else:
                print("❌ Opción inválida. Ingrese 1, 2 o 3.")
        except KeyboardInterrupt:
            print("\n\n❌ Operación cancelada")
            return
    
    # Analizar progreso
    df_completadas, configuraciones_faltantes = analizar_progreso_experimento(tipo)
    
    if configuraciones_faltantes:
        print(f"\n💡 RECOMENDACIONES:")
        print(f"   1. Ejecuta el script original para completar las configuraciones faltantes")
        print(f"   2. Los resultados se guardarán con timestamp único")
        print(f"   3. Usa 'unir_resultados_parciales.py' para combinar todos los resultados")
    else:
        print(f"\n🎉 ¡EXPERIMENTO COMPLETO!")
        print(f"   Puedes usar 'unir_resultados_parciales.py' para crear el archivo final")

if __name__ == "__main__":
    main()
