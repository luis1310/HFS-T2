# Análisis de Costos y Oportunidades de Vectorización

## Corrección: Impacto del Filtro Epsilon

### Análisis Corregido

**Memético:**
- Sin filtro: 27.08s (score: 2.6116)
- Con filtro: 30.88s (score: 2.6034)
- **Impacto tiempo: +14.0%** (el filtro AÑADE tiempo)
- Impacto score: -0.31% (el filtro mejora calidad del frente)

**NSGA2:**
- Sin filtro: 25.45s (score: 2.6089)
- Con filtro: 26.55s (score: 2.6029)
- **Impacto tiempo: +4.3%** (el filtro AÑADE tiempo)
- Impacto score: -0.23% (el filtro mejora calidad del frente)

### Conclusión

El filtro epsilon **AÑADE tiempo** (~4-14%) pero mejora la calidad del frente de Pareto. Es un trade-off entre tiempo de ejecución y calidad de las soluciones.

---

## Operaciones Más Costosas

### 1. Evaluación de Fitness (`fitness_multiobjetivo`)

**Características:**
- **Frecuencia:** 100 individuos × 400 generaciones = **40,000 evaluaciones**
- **Complejidad:** O(pedidos × etapas × máquinas)
- **Tiempo estimado:** ~40-50% del tiempo total

**Operaciones principales:**
- Cálculo de tiempos de procesamiento por pedido
- Verificación de enfriamiento
- Cálculo de balance de carga (desviación estándar)
- Cálculo de consumo energético

**Oportunidades de optimización:**
- Vectorizar cálculos de tiempos con NumPy
- Pre-calcular rangos y constantes fuera de bucles
- Usar operaciones vectorizadas para `disponibilidad_maquinas`
- Optimizar cálculos de energía con arrays NumPy

---

### 2. Clasificación No Dominada (`clasificacion_no_dominada`)

**Características:**
- **Frecuencia:** ~400 generaciones (con optimización adaptativa)
- **Complejidad:** O(n²) comparaciones de dominancia
- **Tiempo estimado:** ~20-30% del tiempo total

**Código actual:**
```python
for i in range(n):
    for j in range(i + 1, n):
        if dominancia(fitness_poblacion[i], fitness_poblacion[j]):
            # ...
```

**Oportunidades de vectorización:**
- Convertir `fitness_poblacion` a array NumPy
- Usar broadcasting para comparar todos los pares simultáneamente
- Reducir complejidad de O(n²) a O(n log n) con ordenamiento inteligente

**Optimización propuesta:**
```python
import numpy as np

fitness_array = np.array(fitness_poblacion)
# Broadcasting: comparar todos los pares a la vez
# dominancia_matrix = (fitness_array[:, None, :] >= fitness_array[None, :, :]).all(axis=2)
# mejor_en_alguno = (fitness_array[:, None, :] > fitness_array[None, :, :]).any(axis=2)
```

**Ahorro estimado:** 30-50% del tiempo de clasificación

---

### 3. Filtro Epsilon (`filtrar_soluciones_similares`)

**Características:**
- **Frecuencia:** ~13 veces (cada 30 generaciones)
- **Complejidad:** O(n²) en peor caso, ~O(n) con grid espacial
- **Tiempo estimado:** ~10-15% del tiempo total

**Código actual (operaciones costosas):**
```python
# Conversión de fitness a métricas (list comprehension)
metricas = [convertir_fitness_a_metricas(f) for f in fitness_poblacion]
makespans = [m[0] for m in metricas]
balances = [m[1] for m in metricas]
energias = [m[2] for m in metricas]

# Normalización repetida
for i, (mk, bal, eng) in enumerate(metricas):
    mk_norm = (mk - min(makespans)) / rango_mk if rango_mk > 0 else 0
    # ...
```

**Oportunidades de vectorización:**
- Vectorizar conversión de fitness a métricas
- Vectorizar cálculos de distancias normalizadas
- Usar NumPy para operaciones de grid

**Optimización propuesta:**
```python
import numpy as np

# Vectorizar conversión
fitness_array = np.array(fitness_poblacion)
makespans = 1 / fitness_array[:, 0]
balances = 1 / fitness_array[:, 1] - 1
energias = 1 / fitness_array[:, 2] - 1

# Vectorizar normalización
makespans_norm = (makespans - makespans.min()) / (makespans.max() - makespans.min())
# ...
```

**Ahorro estimado:** 20-40% del tiempo de filtrado

---

### 4. Distancia Crowding (`distancia_crowding`)

**Características:**
- **Frecuencia:** ~400 generaciones (en selección)
- **Complejidad:** O(m × n log n) donde m=objetivos, n=tamaño frente
- **Tiempo estimado:** ~5-10% del tiempo total

**Código actual:**
```python
for m in range(num_objetivos):
    indices_ordenados = sorted(range(n), key=lambda i: fitness_frente[i][m])
    # ...
```

**Oportunidades de vectorización:**
- Usar `np.argsort` en lugar de `sorted` con key
- Vectorizar cálculos de distancias

**Optimización propuesta:**
```python
import numpy as np

fitness_array = np.array(fitness_frente)
for m in range(num_objetivos):
    indices_ordenados = np.argsort(fitness_array[:, m])
    # Vectorizar cálculos de distancias
    # ...
```

**Ahorro estimado:** 15-30% del tiempo de crowding

---

### 5. Operadores Genéticos (cruce, mutación)

**Características:**
- **Frecuencia:** 100 individuos × 400 generaciones = **40,000 operaciones**
- **Complejidad:** O(longitud_cromosoma)
- **Tiempo estimado:** ~5-10% del tiempo total

**Oportunidades:**
- Las operaciones con listas ya son relativamente eficientes
- Considerar usar NumPy arrays para genes si es posible (requiere refactorización)

---

## Resumen de Oportunidades de Vectorización

### Prioridad Alta

1. **Vectorizar Clasificación No Dominada**
   - Ahorro estimado: 30-50% del tiempo de clasificación
   - Impacto total: ~6-15% del tiempo total

2. **Vectorizar Filtro Epsilon**
   - Ahorro estimado: 20-40% del tiempo de filtrado
   - Impacto total: ~2-6% del tiempo total

3. **Vectorizar Distancia Crowding**
   - Ahorro estimado: 15-30% del tiempo de crowding
   - Impacto total: ~1-3% del tiempo total

### Prioridad Media

4. **Optimizar Fitness Multiobjetivo**
   - Ahorro estimado: 10-20% del tiempo de fitness
   - Impacto total: ~4-10% del tiempo total

---

## Impacto Esperado Total

### Escenario 1: Con todas las optimizaciones + filtro activo

- **Tiempo actual:** ~26.55s (NSGA2 completo)
- **Ahorro estimado:** 20-35%
- **Tiempo optimizado:** ~17-21s

### Escenario 2: Con todas las optimizaciones + filtro desactivado

- **Tiempo actual:** ~25.45s (NSGA2 sin filtro)
- **Ahorro adicional:** ~4% (por desactivar filtro)
- **Ahorro total:** 24-39%
- **Tiempo optimizado:** ~16-20s

### Escenario 3: Para alcanzar <10s

Para alcanzar el objetivo de <10s, aún se necesitaría:
- Reducir hiperparámetros (población/generaciones)
- O aceptar tiempos ~16-20s como óptimo balance calidad/tiempo

---

## Recomendaciones

1. **Implementar vectorizaciones de prioridad alta primero:**
   - Clasificación no dominada (mayor impacto)
   - Filtro epsilon (impacto medio-alto)
   - Distancia crowding (impacto medio)

2. **Evaluar trade-off del filtro epsilon:**
   - Si la calidad del frente es crítica: mantener filtro
   - Si el tiempo es crítico: desactivar filtro (ahorro ~4%)

3. **Considerar optimizaciones de fitness solo si:**
   - Las otras optimizaciones no son suficientes
   - Se requiere un ahorro adicional del 10-20%

4. **Para alcanzar <10s:**
   - Primero aplicar todas las vectorizaciones
   - Luego evaluar si es necesario reducir hiperparámetros
   - Considerar si <10s es realista sin sacrificar calidad significativa

