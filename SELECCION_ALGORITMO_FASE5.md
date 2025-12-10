# Selección de Algoritmo para Fase 5 (Visualizaciones)

## ¿Cómo se Selecciona entre Estándar y Memético?

Los scripts de visualización (`visualizar_frente_memetico.py` y `analizar_mejores_soluciones.py`) **automáticamente** determinan qué versión usar basándose en los resultados de la Fase 4.

### Proceso de Selección

1. **Busca el archivo de resumen más reciente**: `comparacion_memetica_resumen_*.yaml`
2. **Lee la recomendación**: Campo `version_recomendada` en `comparacion`
3. **Ejecuta el algoritmo correspondiente**:
   - Si `version_recomendada == 'memetico'` → Usa `nsga2_memetic()`
   - Si `version_recomendada == 'estandar'` → Usa `nsga2()`

### Código de Selección

```python
# En visualizar_frente_memetico.py y analizar_mejores_soluciones.py
archivos_resumen = glob.glob('tesis3/results/comparacion_memetica_resumen_*.yaml')
archivo_mas_reciente = sorted(archivos_resumen)[-1]

with open(archivo_mas_reciente, 'r') as f:
    resumen = yaml.safe_load(f)
    version_recomendada = resumen['comparacion']['version_recomendada']

if version_recomendada == 'memetico':
    frente_pareto, fitness_pareto, historial = nsga2_memetic(...)
else:
    frente_pareto, fitness_pareto, historial = nsga2(...)
```

## Score Balanceado (Nuevo)

A partir de ahora, la recomendación se basa en **score balanceado** que considera:
- **70% score agregado** (calidad de soluciones)
- **30% tiempo de ejecución** (eficiencia)

### Cálculo del Score Balanceado

1. **Normalizar** score y tiempo a [0, 1] donde 0 = mejor, 1 = peor
2. **Combinar** con pesos: `score_balanceado = 0.7 * score_norm + 0.3 * tiempo_norm`
3. **Comparar**: Menor score balanceado = mejor

### Ejemplo con Resultados Actuales

**Estándar:**
- Score agregado: 2.6047
- Tiempo: 16.78s
- Score balanceado: ~0.35

**Memético:**
- Score agregado: 2.6034 (mejor)
- Tiempo: 20.31s (más lento)
- Score balanceado: ~0.65

**Conclusión**: Si score balanceado del memético es mayor, el **estándar sería recomendado** porque el overhead de tiempo no justifica la pequeña mejora en calidad.

## ¿Cuál es Recomendable?

### Con Resultados Actuales (sin score balanceado)

- **Memético**: Mejor score (0.05% mejor) pero 21% más lento
- **Recomendación actual**: Memético (solo considera score)

### Con Score Balanceado (nuevo criterio)

La recomendación cambiará a considerar el balance calidad/tiempo. Si el overhead es alto y la mejora pequeña, el estándar puede ser recomendado.

## Cómo Cambiar Manualmente

Si quieres forzar el uso de una versión específica:

### Opción 1: Modificar el YAML

Editar `tesis3/results/comparacion_memetica_resumen_*.yaml`:
```yaml
comparacion:
  version_recomendada: estandar  # o 'memetico'
```

### Opción 2: Modificar el Script

En `visualizar_frente_memetico.py` o `analizar_mejores_soluciones.py`, cambiar:
```python
usar_memetico = True   # Forzar memético
# o
usar_memetico = False  # Forzar estándar
```

## Próximos Pasos

1. **Re-ejecutar Fase 4** con el código actualizado para obtener score balanceado
2. **Verificar recomendación** en el YAML generado
3. **Ejecutar Fase 5** - Los scripts usarán automáticamente la versión recomendada

