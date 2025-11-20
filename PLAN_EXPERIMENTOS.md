# Plan de Experimentos para Tesis

## Objetivo General

Determinar la **configuración óptima** del algoritmo NSGA-II memético para el problema de programación en líneas de ensamblaje multiobjetivo.

## Orden de Ejecución de Experimentos

### Resumen de Paralelización por Fase

| Fase | Script | Paralelizado | Detecta Núcleos | Usa Todos los Núcleos |
|------|--------|--------------|-----------------|----------------------|
| 1 | `prueba_rapida.py` | SÍ | NO (usa fijo 6) | NO |
| 2 | `comparacion_operadores.py` | SÍ | SÍ (menú interactivo) | SÍ (opcional: 24/32) |
| 3 | `tunning_multimetrica.py` | SÍ | SÍ (menú interactivo) | SÍ (opcional: 24/32) |
| 4 | `ejecutar_memetico.py` | SÍ | SÍ (menú interactivo) | SÍ (opcional: 24/32) |
| 5 | `visualizar_frente_memetico.py` | NO | NO | NO (no necesita) |
| 5 | `analizar_mejores_soluciones.py` | NO | NO | NO (no necesita) |

**Nota sobre Fase 4 y 5:**
- Fase 4 (`ejecutar_memetico.py`): AHORA PARALELIZADO con 30 semillas (60 ejecuciones totales)
- Fase 5 (visualizaciones): NO necesita paralelización (solo 1 ejecución cada uno)

### **FASE 1: Verificación y Pruebas Rápidas**

**Objetivo**: Verificar que todo funciona correctamente antes de ejecutar experimentos largos.

#### 1.1 Prueba Rápida de Paralelización
```bash
python3 tesis3/experiments/paralelizacion/prueba_rapida.py
```
**¿Qué hace?**
- Prueba rápida con 3 configuraciones × 4 semillas = 12 ejecuciones
- Verifica que la paralelización funciona correctamente
- Tiempo estimado: ~5-10 minutos

**Paralelización:**
- SÍ está paralelizado
- Usa 6 núcleos fijos (no detecta automáticamente todos los núcleos)
- Usa ProcessPoolExecutor para paralelización real

**Resultados:**
- `tesis3/results/prueba_rapida_parcial_*.csv`

---

### **FASE 2: Comparación de Operadores**

**Objetivo**: Encontrar la **mejor combinación de operadores** (cruce + mutación) antes del tunning.

#### 2.1 Comparación de Operadores (Paralelizado)
```bash
python3 tesis3/experiments/paralelizacion/comparacion_operadores.py
```
**¿Qué hace?**
- Compara 6 combinaciones de operadores:
  - Cruce: Uniforme, 1-Punto
  - Mutación: Swap, Insert, Invert
- 30 semillas por combinación = 180 ejecuciones totales
- Tiempo estimado: ~3-4 horas (con 32 núcleos)

**Paralelización:**
- SÍ está paralelizado
- SÍ detecta núcleos automáticamente (24 físicos / 32 lógicos)
- Menú interactivo para seleccionar cuántos núcleos usar
- Usa ProcessPoolExecutor para paralelización real
- Recomendado: usar 32 núcleos lógicos para máximo rendimiento

**Resultados:**
- `tesis3/results/comparacion_operadores_real_*.csv`
- `tesis3/results/mejor_configuracion_operadores_*.yaml` - **GUARDAR ESTE**
- `tesis3/results/comparacion_operadores_parcial_*.csv`

**Acción después:**
- Identificar mejor combinación (menor score agregado)
- Anotar: mejor_cruce = ?, mejor_mutacion = ?

---

### **FASE 3: Tunning Multiobjetivo**

**Objetivo**: Encontrar la **mejor configuración de hiperparámetros** usando la mejor combinación de operadores.

**IMPORTANTE**: Antes de ejecutar, modificar `tunning_multimetrica.py` para usar la mejor combinación de operadores encontrada en la Fase 2.

#### 3.1 Tunning Multiobjetivo (Paralelizado)
```bash
python3 tesis3/experiments/paralelizacion/tunning_multimetrica.py
```
**¿Qué hace?**
- Evalúa 324 configuraciones (actualmente configurado):
  - `tamano_poblacion`: [100, 150, 200] (3)
  - `num_generaciones`: [400, 500, 600] (3)
  - `prob_cruce`: [0.7, 0.8, 0.9] (3)
  - `prob_mutacion`: [0.1, 0.125, 0.15] (3)
  - `cada_k_gen`: [5, 10] (2)
  - `max_iter_local`: [3, 5] (2)
- 30 semillas por configuración = 9,720 ejecuciones totales
- Tiempo estimado: ~22-30 horas (con 32 núcleos)

**Paralelización:**
- SÍ está paralelizado
- SÍ detecta núcleos automáticamente (24 físicos / 32 lógicos)
- Menú interactivo para seleccionar cuántos núcleos usar
- Usa ProcessPoolExecutor para paralelización real
- Recomendado: usar 32 núcleos lógicos para máximo rendimiento

**Resultados:**
- `tesis3/results/tunning_multimetrica_real_*.csv`
- `tesis3/results/mejor_configuracion_tunning_*.yaml` - **GUARDAR ESTE**
- `tesis3/results/tunning_multimetrica_parcial_*.csv` (guardados automáticamente durante ejecución)

**Acción después:**
- Identificar mejor configuración de hiperparámetros
- Guardar archivo YAML con mejor configuración

---

### **FASE 4: Comparación Estándar vs Memético**

**Objetivo**: Verificar que la versión **memética** mejora los resultados respecto a la estándar usando la configuración optimizada.

**IMPORTANTE**: Este script ahora lee los parámetros del `config.yaml`. Después de completar la Fase 3, debes actualizar el `config.yaml` con los mejores parámetros encontrados en el tunning.

#### 4.1 Comparación NSGA-II Estándar vs Memético
```bash
python3 tesis3/experiments/ejecutar_memetico.py
```
**¿Qué hace?**
- Compara NSGA-II estándar vs NSGA-II memético
- 30 semillas por versión = 60 ejecuciones totales
- Lee parámetros desde config.yaml (población, generaciones, prob_cruce, etc.)
- Tiempo estimado: Variable según parámetros del config.yaml
  - Con params optimizados típicos (150 pop, 500 gen): ~10-15 minutos (con 32 núcleos)
  - Con params por defecto (200 pop, 1000 gen): ~30-40 minutos

**Paralelización:**
- SÍ está paralelizado (actualizado)
- SÍ detecta núcleos automáticamente (24 físicos / 32 lógicos)
- Menú interactivo para seleccionar cuántos núcleos usar
- Usa ProcessPoolExecutor para paralelización real
- Recomendado: usar 32 núcleos lógicos para máximo rendimiento
- Detecta y continúa desde resultados previos

**Resultados:**
- `tesis3/results/comparacion_memetica_parcial_*.csv` - Resultados parciales durante la ejecución
- `tesis3/results/comparacion_memetica_final_*.csv` - Resultado consolidado final
- `tesis3/results/comparacion_memetica_resumen_*.yaml` - Resumen estadístico
- Análisis estadístico de mejoras

**Acción después:**
- Verificar que la versión memética es mejor (o no)
- Documentar mejoras estadísticas

---

### **FASE 5: Análisis y Visualizaciones Finales**

**Objetivo**: Generar visualizaciones y análisis de los resultados finales usando la **mejor configuración encontrada**.

**IMPORTANTE**: Antes de ejecutar, actualizar `config.yaml` con la mejor configuración encontrada en la Fase 3.

#### 5.1 Visualización del Frente de Pareto
```bash
python3 tesis3/experiments/visualizar_frente_memetico.py
```
**¿Qué hace?**
- Ejecuta NSGA-II memético con la mejor configuración
- Genera visualizaciones 2D y 3D del frente de Pareto
- Tiempo estimado: ~2-3 minutos

**Paralelización:**
- NO está paralelizado (no necesita)
- Ejecuta NSGA-II UNA sola vez (una ejecución)
- No tiene sentido paralelizar porque solo genera gráficos de una ejecución
- El tiempo es muy corto (2-3 minutos)

**Resultados:**
- `tesis3/results/frente_pareto_memetico_3d.png`
- `tesis3/results/frente_pareto_memetico_2d.png`
- `tesis3/results/evolucion_frente_memetico.png`
- `tesis3/results/frente_pareto_memetico.csv`

#### 5.2 Análisis de Mejores Soluciones
```bash
python3 tesis3/experiments/analizar_mejores_soluciones.py
```
**¿Qué hace?**
- Identifica las 3 mejores soluciones del frente de Pareto
- Genera gráficos comparativos
- Tiempo estimado: ~2-3 minutos

**Paralelización:**
- NO está paralelizado (no necesita)
- Ejecuta NSGA-II UNA sola vez (una ejecución)
- No tiene sentido paralelizar porque solo analiza soluciones de una ejecución
- El tiempo es muy corto (2-3 minutos)

**Resultados:**
- `tesis3/results/mejores_soluciones_pareto.png`
- `tesis3/results/mejores_soluciones.csv`

---

## Resumen del Flujo Completo

```
1. PRUEBA RÁPIDA
   └─> Verificar que todo funciona

2. COMPARACIÓN DE OPERADORES
   └─> Encontrar mejor combinación (cruce + mutación)
   └─> Guardar: mejor_configuracion_operadores_*.yaml
   └─> ACTUALIZAR config.yaml sección "operators" con mejores operadores

3. TUNNING MULTIOBJETIVO
   └─> Lee operadores desde config.yaml (actualizados en Fase 2)
   └─> Encontrar mejor configuración de hiperparámetros
   └─> Guardar: mejor_configuracion_tunning_*.yaml
   └─> ACTUALIZAR config.yaml sección "nsga2" y "memetic" con mejores hiperparámetros

4. COMPARACIÓN ESTÁNDAR VS MEMÉTICO
   └─> Lee TODO desde config.yaml (operadores + hiperparámetros)
   └─> Verificar que versión memética es mejor con config óptima
   └─> Guardar: comparacion_memetica_resumen_*.yaml

5. VISUALIZACIONES FINALES
   └─> Lee TODO desde config.yaml (operadores + hiperparámetros)
   └─> Generar gráficos del frente de Pareto
   └─> Análisis de mejores soluciones
```

## Notas Importantes

### Antes de Ejecutar Tunning (Fase 3):

1. **Modificar `tunning_multimetrica.py`** para usar la mejor combinación de operadores:
   ```python
   # Líneas 28-32 de tunning_multimetrica.py
   def cruce(p1, p2, cfg, prob):
       return aplicar_cruce(p1, p2, cfg, metodo='MEJOR_CRUCE_AQUI', prob_cruce=prob)
   
   def mutacion(pob, cfg, prob):
       return aplicar_mutacion(pob, cfg, metodo='MEJOR_MUTACION_AQUI', tasa_mut=prob)
   ```

2. **Verificar espacio de búsqueda** (actualmente 324 configuraciones):
   - Puede aumentar según tu sistema (tienes 24/32 núcleos)
   - Ver archivo `AUMENTAR_CONFIGURACIONES.md`

### Antes de Tunning (Fase 3):

**ACTUALIZAR OPERADORES en `config.yaml`** con los mejores encontrados:

1. Abre el archivo: `tesis3/results/mejor_configuracion_operadores_TIMESTAMP.yaml`
   
   Verás algo como:
   ```yaml
   configuracion:
     cruce: 'pmx'
     mutacion: 'swap'
   metricas_promedio:
     score_agregado: 1.234
     ...
   ```

2. Copia los valores de `cruce` y `mutacion`

3. Actualiza `tesis3/config/config.yaml` en la sección `algorithm.operators`:
   ```yaml
   algorithm:
     operators:
       cruce: 'pmx'       # Copiado del mejor_configuracion_operadores_*.yaml
       mutacion: 'swap'   # Copiado del mejor_configuracion_operadores_*.yaml
   ```
   
   Operadores disponibles:
   - Cruce: `uniforme`, `pmx`, `un_punto`, `dos_puntos`
   - Mutación: `invert`, `swap`, `scramble`, `insert`

### Antes de Comparación Estándar vs Memético (Fase 4) y Visualizaciones (Fase 5):

**ACTUALIZAR HIPERPARÁMETROS en `config.yaml`** con los mejores del tunning:

1. Abre el archivo: `tesis3/results/mejor_configuracion_tunning_TIMESTAMP.yaml`
   
   Verás algo como:
   ```yaml
   configuracion:
     tamano_poblacion: 150
     num_generaciones: 500
     prob_cruce: 0.85
     prob_mutacion: 0.125
     cada_k_gen: 10
     max_iter_local: 5
   metricas_promedio:
     score_agregado: 0.987
     ...
   ```

2. Copia todos los valores de `configuracion`

3. Actualiza `tesis3/config/config.yaml`:
   ```yaml
   algorithm:
     nsga2:
       tamano_poblacion: 150       # Del tunning
       num_generaciones: 500       # Del tunning
       prob_cruce: 0.85            # Del tunning
       prob_mutacion: 0.125        # Del tunning
     memetic:
       cada_k_generaciones: 10     # Del tunning (cada_k_gen)
       max_iteraciones_local: 5    # Del tunning (max_iter_local)
   ```

NOTA: Los operadores ya deberían estar configurados desde la Fase 2.

## Archivos de Resultados a Guardar

Después de completar todas las fases, asegúrate de tener:

1. `mejor_configuracion_operadores_*.yaml` (Fase 2)
2. `mejor_configuracion_tunning_*.yaml` (Fase 3)
3. `tunning_multimetrica_real_*.csv` (Fase 3 - resultados completos)
4. `comparacion_operadores_real_*.csv` (Fase 2 - resultados completos)
5. `comparacion_memetica.csv` (Fase 4)
6. `frente_pareto_memetico_*.png` (Fase 5 - visualizaciones)
7. `mejores_soluciones_*.png` y `.csv` (Fase 5)

## Tiempo Total Estimado

Con tu sistema (32 núcleos, 125 GB RAM):

| Fase | Tiempo Estimado |
|------|----------------|
| 1. Prueba Rápida | ~5-10 minutos |
| 2. Comparación Operadores | ~3-4 horas |
| 3. Tunning Multiobjetivo | ~22-30 horas |
| 4. Comparación Estándar vs Memético | ~10-15 minutos |
| 5. Visualizaciones | ~5-10 minutos |
| **TOTAL** | **~25-35 horas** |

## Resumen del Flujo Completo de Configuración

```
INICIO
  ↓
FASE 1: Prueba Rápida (verificar paralelización)
  ↓
FASE 2: Comparación de Operadores
  ↓
  → Genera: mejor_configuracion_operadores_*.yaml
  ↓
  → ACCIÓN: Copiar operadores al config.yaml (sección algorithm.operators)
  ↓
FASE 3: Tunning Multiobjetivo
  ↓  (Lee operadores desde config.yaml)
  → Genera: mejor_configuracion_tunning_*.yaml
  ↓
  → ACCIÓN: Copiar hiperparámetros al config.yaml (secciones algorithm.nsga2 y algorithm.memetic)
  ↓
FASE 4: Comparación Estándar vs Memético
  ↓  (Lee TODO desde config.yaml: operadores + hiperparámetros)
  → Genera: comparacion_memetica_resumen_*.yaml
  ↓
FASE 5: Visualizaciones
  ↓  (Lee TODO desde config.yaml: operadores + hiperparámetros)
  → Genera: gráficos PNG y CSV de análisis
  ↓
FIN
```

**IMPORTANTE**: El `config.yaml` se actualiza MANUALMENTE dos veces:
1. Después de Fase 2: Actualizar operadores
2. Después de Fase 3: Actualizar hiperparámetros

## Continuación de Experimentos

Si interrumpes alguna fase:
- Los scripts detectan automáticamente resultados previos
- Solo ejecutan configuraciones faltantes
- Puedes reanudar en cualquier momento

## Comandos Rápidos por Fase

```bash
# FASE 1
python3 tesis3/experiments/paralelizacion/prueba_rapida.py

# FASE 2
python3 tesis3/experiments/paralelizacion/comparacion_operadores.py

# FASE 3 (más larga)
python3 tesis3/experiments/paralelizacion/tunning_multimetrica.py

# FASE 4
python3 tesis3/experiments/ejecutar_memetico.py

# FASE 5
python3 tesis3/experiments/visualizar_frente_memetico.py
python3 tesis3/experiments/analizar_mejores_soluciones.py
```

