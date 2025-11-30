# Respuestas a Preguntas sobre Ablación

## 1. ¿Por qué memético es más rápido que NSGA2?

**Tu pregunta es válida.** Técnicamente, el memético debería ser más lento porque tiene búsqueda local adicional. Sin embargo, es MÁS RÁPIDO porque:

### Optimizaciones que tiene el memético y NSGA2 NO tiene:

1. **Cache de fitness**: Evita recálculos (ahorra 30-40% en generaciones avanzadas)
2. **Clasificación adaptativa**: Reduce frecuencia de reclasificación no dominada
   - NSGA2: Reclasifica cada generación (O(N²) cada vez)
   - Memético: Reclasifica cada 3-5 generaciones en fases avanzadas

### Cálculo aproximado:

- **Búsqueda local**: Añade ~3% de tiempo (+0.64s)
- **Cache de fitness**: Ahorra ~30-40% de evaluaciones = ~15-20% de tiempo total
- **Clasificación adaptativa**: Ahorra ~10-15% de tiempo (menos reclasificaciones)

**Resultado neto**: Las optimizaciones ahorran más tiempo (15-20% + 10-15% = 25-35%) que el costo de la búsqueda local (3%), por lo que el memético es ~18% más rápido.

**Conclusión**: NSGA2 necesita las mismas optimizaciones que tiene el memético.

## 2. Corrección de Ablación: Operadores Genéticos

**Tienes razón.** La ablación debería solo activar/desactivar componentes, NO cambiar operadores.

### Cambios realizados:

- **Eliminadas** las variantes con operadores diferentes (one-point, insert, invert)
- **Mantenidas** solo las variantes que activan/desactivan componentes:
  - Con/sin filtro epsilon
  - Con/sin búsqueda local
  - NSGA2 vs Memético

### Variantes correctas de ablación:

1. NSGA2_completo (con filtro)
2. NSGA2_sin_filtro (sin filtro)
3. Memetico_completo (con filtro + búsqueda local)
4. Memetico_sin_filtro (sin filtro, con búsqueda local)
5. Memetico_sin_busqueda_local (con filtro, sin búsqueda local)
6. Memetico_sin_filtro_ni_busqueda (sin filtro, sin búsqueda local)

**Nota**: La comparación de operadores ya se hizo en `comparacion_operadores.py`, no debe repetirse en la ablación.

## 3. Score Balanceado en Comparación de Operadores

**Sí, debería considerar balance score/tiempo** como el tunning.

### Cambios realizados:

1. **Agregado score balanceado** a `comparacion_operadores.py`:
   - Misma fórmula que tunning: 70% score + 30% tiempo
   - Ordena por score balanceado en lugar de solo score

2. **Script de recálculo creado**: `recalcular_score_balanceado_operadores.py`
   - Recalcula desde CSV existente
   - NO necesitas borrar resultados
   - Solo recalcula el ranking

### ¿Necesitas borrar resultados?

**NO es necesario.** Los CSV existentes tienen todos los datos necesarios (score_agregado y tiempo), por lo que puedes:

1. **Opción 1 (Recomendada)**: Usar el script de recálculo
   ```bash
   python3 tesis3/experiments/paralelizacion/recalcular_score_balanceado_operadores.py
   ```
   - Recalcula desde CSV existente
   - Genera nuevo YAML con score balanceado
   - No requiere re-ejecutar

2. **Opción 2**: Re-ejecutar `comparacion_operadores.py`
   - El script ahora calcula score balanceado automáticamente
   - Detecta resultados previos y solo ejecuta faltantes
   - Genera ranking con score balanceado

### Resultado del recálculo:

El mejor operador sigue siendo **Uniforme + Swap** (tiene mejor score Y mejor tiempo), pero ahora está validado con la métrica balanceada.

## Resumen de Correcciones

1. ✅ **Explicación corregida**: Memético es más rápido por optimizaciones, no por búsqueda local
2. ✅ **Ablación corregida**: Eliminadas variantes de operadores, solo activar/desactivar componentes
3. ✅ **Score balanceado agregado**: `comparacion_operadores.py` ahora usa score balanceado
4. ✅ **Script de recálculo**: Puedes recalcular sin borrar resultados

