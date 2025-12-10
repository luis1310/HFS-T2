"""Utilidades para gestionar semillas de experimentos de forma centralizada"""
import yaml
from pathlib import Path
from typing import List


def cargar_semillas(tipo: str = "estandar") -> List[int]:
    """
    Carga las semillas desde el archivo de configuración centralizado.
    
    Args:
        tipo: Tipo de semillas a cargar. Opciones:
            - "estandar": 30 semillas (0-29) para experimentos completos
            - "prueba_rapida": 4 semillas (0-3) para pruebas rápidas
            - "personalizadas": Semillas personalizadas (si están definidas)
    
    Returns:
        Lista de semillas (enteros)
    
    Raises:
        FileNotFoundError: Si no se encuentra el archivo de configuración
        KeyError: Si el tipo de semillas no existe
    """
    # Ruta al archivo de configuración de semillas
    config_path = Path(__file__).parent.parent.parent / "config" / "semillas.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de semillas en: {config_path}\n"
            f"Por favor, asegúrate de que existe el archivo tesis3/config/semillas.yaml"
        )
    
    # Cargar configuración
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    if 'semillas' not in config:
        raise KeyError("El archivo de semillas no contiene la sección 'semillas'")
    
    if tipo not in config['semillas']:
        raise KeyError(
            f"Tipo de semillas '{tipo}' no encontrado. "
            f"Tipos disponibles: {list(config['semillas'].keys())}"
        )
    
    semillas = config['semillas'][tipo]
    
    # Validar que sean enteros
    if not all(isinstance(s, int) for s in semillas):
        raise ValueError("Todas las semillas deben ser números enteros")
    
    # Ordenar y eliminar duplicados manteniendo el orden
    semillas_unicas = []
    for s in semillas:
        if s not in semillas_unicas:
            semillas_unicas.append(s)
    
    return semillas_unicas


def generar_semillas_estandar(num_semillas: int = 30) -> List[int]:
    """
    Genera semillas estándar (0 a num_semillas-1).
    Útil para mantener compatibilidad con el código anterior.
    
    Args:
        num_semillas: Número de semillas a generar
    
    Returns:
        Lista de semillas [0, 1, 2, ..., num_semillas-1]
    """
    return list(range(num_semillas))


def guardar_semillas(semillas: List[int], tipo: str = "estandar"):
    """
    Guarda semillas en el archivo de configuración.
    
    Args:
        semillas: Lista de semillas a guardar
        tipo: Tipo de semillas (estandar, prueba_rapida, personalizadas)
    
    Raises:
        FileNotFoundError: Si no se encuentra el archivo de configuración
    """
    config_path = Path(__file__).parent.parent.parent / "config" / "semillas.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de semillas en: {config_path}\n"
            f"Por favor, crea primero el archivo tesis3/config/semillas.yaml"
        )
    
    # Cargar configuración existente
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f) or {}
    
    if 'semillas' not in config:
        config['semillas'] = {}
    
    # Actualizar semillas
    config['semillas'][tipo] = semillas
    
    # Guardar
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def verificar_semillas_archivo(archivo_csv: str, semillas_esperadas: List[int]) -> dict:
    """
    Verifica qué semillas están presentes en un archivo CSV de resultados.
    
    Args:
        archivo_csv: Ruta al archivo CSV
        semillas_esperadas: Lista de semillas que se esperan
    
    Returns:
        Dict con:
            - 'semillas_encontradas': Lista de semillas encontradas
            - 'semillas_faltantes': Lista de semillas faltantes
            - 'completo': True si todas las semillas están presentes
    """
    import csv
    
    semillas_encontradas = set()
    
    try:
        with open(archivo_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'semilla' in row:
                    semillas_encontradas.add(int(row['semilla']))
    except FileNotFoundError:
        return {
            'semillas_encontradas': [],
            'semillas_faltantes': semillas_esperadas,
            'completo': False
        }
    
    semillas_esperadas_set = set(semillas_esperadas)
    semillas_faltantes = sorted(list(semillas_esperadas_set - semillas_encontradas))
    
    return {
        'semillas_encontradas': sorted(list(semillas_encontradas)),
        'semillas_faltantes': semillas_faltantes,
        'completo': len(semillas_faltantes) == 0
    }

