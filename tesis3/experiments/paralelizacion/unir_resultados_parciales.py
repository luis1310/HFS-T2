import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pandas as pd
import glob
import os
from datetime import datetime

def unir_archivos_parciales(tipo_experimento):
    """
    Une archivos parciales de un tipo de experimento específico
    
    Args:
        tipo_experimento: 'tunning', 'comparacion', o 'prueba_rapida'
    """
    print(f"="*70)
    print(f"UNIENDO RESULTADOS PARCIALES - {tipo_experimento.upper()}")
    print(f"="*70)
    
    # Patrones de archivos según el tipo
    patrones = {
        'tunning': 'tesis3/results/tunning_multimetrica_parcial_*.csv',
        'comparacion': 'tesis3/results/comparacion_operadores_parcial_*.csv',
        'prueba_rapida': 'tesis3/results/prueba_rapida_parcial_*.csv'
    }
    
    if tipo_experimento not in patrones:
        print(f"❌ Tipo de experimento no válido: {tipo_experimento}")
        print(f"Tipos válidos: {list(patrones.keys())}")
        return
    
    patron = patrones[tipo_experimento]
    archivos = glob.glob(patron)
    
    if not archivos:
        print(f"❌ No se encontraron archivos parciales para {tipo_experimento}")
        print(f"Patrón buscado: {patron}")
        return
    
    print(f"📁 Archivos encontrados: {len(archivos)}")
    for archivo in sorted(archivos):
        print(f"   - {os.path.basename(archivo)}")
    
    # Leer y combinar todos los archivos
    dataframes = []
    configuraciones_vistas = set()
    
    for archivo in sorted(archivos):
        print(f"\n📖 Leyendo: {os.path.basename(archivo)}")
        try:
            df = pd.read_csv(archivo)
            print(f"   Configuraciones en archivo: {len(df)}")
            
            # Identificar configuraciones únicas
            if tipo_experimento == 'tunning' or tipo_experimento == 'prueba_rapida':
                # Para tunning y prueba_rapida: usar combinación de hiperparámetros
                df['config_key'] = df.apply(lambda row: 
                    f"{row['tamano_poblacion']}-{row['num_generaciones']}-{row['prob_cruce']}-{row['prob_mutacion']}-{row['cada_k_gen']}-{row['max_iter_local']}", 
                    axis=1)
            else:
                # Para comparacion: usar nombre de configuración
                df['config_key'] = df['configuracion_nombre']
            
            # Filtrar configuraciones que no hemos visto antes
            nuevas_configs = df[~df['config_key'].isin(configuraciones_vistas)]
            
            if len(nuevas_configs) > 0:
                print(f"   ✅ Nuevas configuraciones: {len(nuevas_configs)}")
                dataframes.append(nuevas_configs)
                
                # Agregar a configuraciones vistas
                configuraciones_vistas.update(nuevas_configs['config_key'].tolist())
            else:
                print(f"   ⚠️  No hay configuraciones nuevas (ya procesadas)")
                
        except Exception as e:
            print(f"   ❌ Error leyendo archivo: {e}")
            continue
    
    if not dataframes:
        print(f"\n❌ No hay configuraciones nuevas para combinar")
        return
    
    # Combinar todos los dataframes
    df_final = pd.concat(dataframes, ignore_index=True)
    
    # Ordenar por score (menor es mejor)
    if 'prom_score' in df_final.columns:
        df_final = df_final.sort_values('prom_score')
    
    print(f"\n📊 RESUMEN DE COMBINACIÓN:")
    print(f"   Total configuraciones únicas: {len(df_final)}")
    print(f"   Archivos procesados: {len(dataframes)}")
    
    # Asegurar que el directorio existe
    os.makedirs('tesis3/results', exist_ok=True)
    
    # Guardar archivo combinado
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archivo_final = f'tesis3/results/{tipo_experimento}_combinado_{timestamp}.csv'
    
    df_final.to_csv(archivo_final, index=False)
    print(f"\n💾 Archivo combinado guardado: {archivo_final}")
    
    # Mostrar mejores configuraciones
    print(f"\n🏆 TOP 5 MEJORES CONFIGURACIONES:")
    print("-" * 80)
    
    top_5 = df_final.head(5)
    for i, (_, row) in enumerate(top_5.iterrows(), 1):
        if tipo_experimento == 'tunning' or tipo_experimento == 'prueba_rapida':
            print(f"{i}. Pob:{row['tamano_poblacion']} Gen:{row['num_generaciones']} "
                  f"PC:{row['prob_cruce']} PM:{row['prob_mutacion']} "
                  f"K:{row['cada_k_gen']} IL:{row['max_iter_local']} "
                  f"Score:{row['prom_score']:.4f}")
        else:
            print(f"{i}. {row['configuracion_nombre']} "
                  f"Score:{row['prom_score']:.4f}")
    
    print(f"\n✅ Combinación completada exitosamente!")
    return archivo_final

def main():
    print("🔧 HERRAMIENTA PARA COMBINAR RESULTADOS PARCIALES")
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
    
    # Ejecutar combinación
    archivo_resultado = unir_archivos_parciales(tipo)
    
    if archivo_resultado:
        print(f"\n🎉 ¡Proceso completado!")
        print(f"📁 Archivo final: {archivo_resultado}")
        print(f"💡 Puedes usar este archivo para análisis o continuar el experimento")

if __name__ == "__main__":
    main()
