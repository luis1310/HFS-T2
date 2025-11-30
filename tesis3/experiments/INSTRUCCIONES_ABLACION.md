# Instrucciones para Ejecutar el Estudio de Ablación

## Requisitos Previos

### 1. Python 3.8 o superior
Verifica que Python esté instalado:
```bash
python3 --version
# Debe mostrar Python 3.8 o superior
```

Si no está instalado:
- **Linux/Mac**: Generalmente viene preinstalado
- **Windows**: Descargar desde [python.org](https://www.python.org/downloads/)

### 2. Librerías Necesarias

El script de ablación requiere las siguientes librerías (mínimas):
- `numpy` (>=1.24.0)
- `pyyaml` (>=6.0)

**Opcional** (para visualización/paralelización, no necesarias para ablación):
- matplotlib, pandas, seaborn, tqdm, psutil

## Instalación Rápida

### Opción 1: Instalar solo lo necesario (RECOMENDADO para computadora prestada)

```bash
# Navegar a la raíz del proyecto
cd /ruta/al/proyecto/HFS-T2

# Instalar dependencias mínimas
pip3 install numpy pyyaml
```

### Opción 2: Instalar todas las dependencias del proyecto

```bash
# Navegar a la raíz del proyecto
cd /ruta/al/proyecto/HFS-T2

# Instalar todas las dependencias
pip3 install -r requirements.txt
```

### Opción 3: Usar entorno virtual (RECOMENDADO si puedes instalar)

```bash
# Crear entorno virtual
python3 -m venv venv_ablacion

# Activar entorno virtual
# En Linux/Mac:
source venv_ablacion/bin/activate
# En Windows:
venv_ablacion\Scripts\activate

# Instalar dependencias mínimas
pip install numpy pyyaml
```

## Ejecución del Script

### 1. Verificar que el archivo de configuración existe

```bash
# Verificar que existe el archivo de configuración
ls tesis3/config/config.yaml
```

### 2. Ejecutar el script de ablación

```bash
# Desde la raíz del proyecto
python3 tesis3/experiments/ablacion.py
```

### 3. Tiempo de Ejecución Estimado

- **Variantes a probar**: 11 variantes
- **Semillas por variante**: 10 semillas (configurable)
- **Total ejecuciones**: 11 × 10 = 110 ejecuciones
- **Tiempo por ejecución**: ~20-30 segundos (depende de la computadora)
- **Tiempo total estimado**: ~35-55 minutos

**Nota**: Puedes reducir el número de semillas editando el script (línea ~280):
```python
num_semillas = 5  # Cambiar de 10 a 5 para prueba rápida
```

## Estructura de Resultados

El script generará dos archivos CSV en `tesis3/results/`:

1. **`ablacion_detallado_YYYYMMDD_HHMMSS.csv`**
   - Resultados detallados por semilla
   - Columnas: variante, semilla, cruce, mutacion, tiempo, makespan, balance, energia, score_agregado, tamano_frente

2. **`ablacion_resumen_YYYYMMDD_HHMMSS.csv`**
   - Resumen por variante (promedios y desviaciones)
   - Columnas: variante, descripcion, prom_tiempo, std_tiempo, prom_score, std_score, etc.

## Solución de Problemas

### Error: "No module named 'tesis3'"
**Causa**: Python no encuentra el módulo del proyecto.

**Solución**: Ejecutar desde la raíz del proyecto:
```bash
cd /ruta/completa/al/proyecto/HFS-T2
python3 tesis3/experiments/ablacion.py
```

### Error: "No module named 'numpy'"
**Causa**: NumPy no está instalado.

**Solución**:
```bash
pip3 install numpy
```

### Error: "No module named 'yaml'"
**Causa**: PyYAML no está instalado.

**Solución**:
```bash
pip3 install pyyaml
```

### Error: "FileNotFoundError: tesis3/config/config.yaml"
**Causa**: El archivo de configuración no existe o la ruta es incorrecta.

**Solución**: Verificar que estás en la raíz del proyecto:
```bash
pwd  # Debe mostrar la ruta que contiene la carpeta 'tesis3'
ls tesis3/config/config.yaml  # Debe existir
```

### Error de permisos al instalar
**Causa**: No tienes permisos para instalar en el sistema.

**Solución**: Usar `--user` para instalar en el directorio del usuario:
```bash
pip3 install --user numpy pyyaml
```

O usar un entorno virtual (Opción 3 arriba).

## Verificación Rápida

Para verificar que todo está listo, ejecuta:

```bash
# Verificar Python
python3 --version

# Verificar librerías
python3 -c "import numpy; import yaml; print('✅ Todas las librerías están instaladas')"

# Verificar estructura del proyecto
ls tesis3/config/config.yaml && echo "✅ Archivo de configuración encontrado"
```

## Notas Importantes

1. **No requiere conexión a internet** una vez instaladas las dependencias
2. **No requiere GPU** - corre en CPU
3. **Puede interrumpirse** con Ctrl+C sin perder resultados parciales (si se implementa guardado incremental)
4. **Resultados se guardan automáticamente** al finalizar
5. **No modifica archivos** del proyecto, solo genera resultados en `tesis3/results/`

## Ejecución en Modo Prueba (Rápida)

Si quieres probar rápidamente con menos variantes o semillas, puedes editar el script:

```python
# En tesis3/experiments/ablacion.py, línea ~280
num_semillas = 3  # Reducir a 3 semillas para prueba rápida

# O comentar algunas variantes en generar_variantes()
```

Esto reducirá el tiempo de ejecución a ~10-15 minutos.

