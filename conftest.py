"""Configuración global de pytest"""
import sys
from pathlib import Path

# Añadir raíz del proyecto al path de Python
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))
