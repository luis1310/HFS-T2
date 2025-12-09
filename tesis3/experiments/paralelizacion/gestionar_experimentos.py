#!/usr/bin/env python3
"""
Script maestro para gestionar experimentos parciales
Permite analizar progreso, combinar resultados y continuar experimentos
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import os
import glob
from datetime import datetime

def mostrar_menu():
    """Muestra el menú principal"""
    print("="*70)
    print("🔧 GESTOR DE EXPERIMENTOS PARCIALES")
    print("="*70)
    print()
    print("1. 📊 Analizar progreso de experimento")
    print("2. 🔗 Combinar archivos parciales")
    print("3. 📁 Listar archivos de resultados")
    print("4. 🗑️  Limpiar archivos antiguos")
    print("5. ❌ Salir")
    print()

def analizar_progreso():
    """Ejecuta el analizador de progreso"""
    print("🔍 Ejecutando analizador de progreso...")
    os.system("python3 tesis3/experiments/paralelizacion/continuar_experimento.py")

def combinar_resultados():
    """Ejecuta el combinador de resultados"""
    print("🔗 Ejecutando combinador de resultados...")
    os.system("python3 tesis3/experiments/paralelizacion/unir_resultados_parciales.py")

def listar_archivos():
    """Lista todos los archivos de resultados"""
    print("📁 ARCHIVOS DE RESULTADOS:")
    print("-" * 50)
    
    # Buscar archivos parciales
    archivos_parciales = glob.glob("tesis3/results/*_parcial_*.csv")
    archivos_finales = glob.glob("tesis3/results/*_real_*.csv")
    archivos_combinados = glob.glob("tesis3/results/*_combinado_*.csv")
    
    if archivos_parciales:
        print(f"\n📄 Archivos parciales ({len(archivos_parciales)}):")
        for archivo in sorted(archivos_parciales):
            nombre = os.path.basename(archivo)
            tamaño = os.path.getsize(archivo)
            fecha = datetime.fromtimestamp(os.path.getmtime(archivo))
            print(f"   {nombre} ({tamaño} bytes) - {fecha.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if archivos_finales:
        print(f"\n📄 Archivos finales ({len(archivos_finales)}):")
        for archivo in sorted(archivos_finales):
            nombre = os.path.basename(archivo)
            tamaño = os.path.getsize(archivo)
            fecha = datetime.fromtimestamp(os.path.getmtime(archivo))
            print(f"   {nombre} ({tamaño} bytes) - {fecha.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if archivos_combinados:
        print(f"\n📄 Archivos combinados ({len(archivos_combinados)}):")
        for archivo in sorted(archivos_combinados):
            nombre = os.path.basename(archivo)
            tamaño = os.path.getsize(archivo)
            fecha = datetime.fromtimestamp(os.path.getmtime(archivo))
            print(f"   {nombre} ({tamaño} bytes) - {fecha.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not archivos_parciales and not archivos_finales and not archivos_combinados:
        print("❌ No se encontraron archivos de resultados")

def limpiar_archivos():
    """Limpia archivos antiguos con confirmación"""
    print("🗑️  LIMPIEZA DE ARCHIVOS ANTIGUOS")
    print("-" * 50)
    
    # Buscar archivos parciales
    archivos_parciales = glob.glob("tesis3/results/*_parcial_*.csv")
    
    if not archivos_parciales:
        print("❌ No hay archivos parciales para limpiar")
        return
    
    print(f"📁 Archivos parciales encontrados: {len(archivos_parciales)}")
    print("\nArchivos que se eliminarán:")
    for archivo in sorted(archivos_parciales):
        nombre = os.path.basename(archivo)
        tamaño = os.path.getsize(archivo)
        fecha = datetime.fromtimestamp(os.path.getmtime(archivo))
        print(f"   {nombre} ({tamaño} bytes) - {fecha.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n⚠️  ADVERTENCIA: Se eliminarán {len(archivos_parciales)} archivos parciales")
    print("   Los archivos finales y combinados NO se eliminarán")
    
    confirmar = input("\n¿Continuar con la limpieza? (s/n): ").lower()
    if confirmar == 's':
        eliminados = 0
        for archivo in archivos_parciales:
            try:
                os.remove(archivo)
                eliminados += 1
                print(f"   ✅ Eliminado: {os.path.basename(archivo)}")
            except Exception as e:
                print(f"   ❌ Error eliminando {os.path.basename(archivo)}: {e}")
        
        print(f"\n🎉 Limpieza completada: {eliminados} archivos eliminados")
    else:
        print("❌ Limpieza cancelada")

def main():
    """Función principal"""
    while True:
        mostrar_menu()
        
        try:
            opcion = input("Seleccione una opción (1-5): ").strip()
            
            if opcion == "1":
                analizar_progreso()
            elif opcion == "2":
                combinar_resultados()
            elif opcion == "3":
                listar_archivos()
            elif opcion == "4":
                limpiar_archivos()
            elif opcion == "5":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida. Ingrese 1-5.")
            
            input("\nPresione Enter para continuar...")
            print("\n" + "="*70 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()
