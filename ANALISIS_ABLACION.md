# Análisis de Resultados de Ablación

## Resumen de Resultados

### Configuración Actual (Baseline)
- **Memético Completo**: 21.08s, score 2.6034
- **Operadores**: Cruce uniforme + Mutación swap
- **Componentes activos**: Filtro epsilon + Búsqueda local + Cache + Optimizaciones

### Impacto de Componentes

#### 1. Filtro Epsilon
- **Sin filtro**: 21.57s (+2.3% tiempo), score 2.6116 (+0.3% peor)
- **Conclusión**: **MANTENER** - El filtro mejora la calidad con poco costo

#### 2. Búsqueda Local
- **Sin búsqueda**: 21.72s (+3.0% tiempo), score 2.6029 (-0.0% casi igual)
- **Conclusión**: **MARGINAL** - Impacto mínimo en calidad, pequeño overhead

#### 3. Operadores Genéticos
- **Uniforme + Swap** (actual): 21.08s, score 2.6034
- **NSGA2 + Invert**: 29.32s (+39% tiempo), score 2.6016 (-0.07% mejor)
- **Conclusión**: **MANTENER** - Uniforme+Swap es mejor balance tiempo/calidad

## Implicaciones para el Código

### ¿Se Requieren Cambios?

**NO se requieren cambios urgentes** en el código. Los resultados validan que:

1. **La configuración actual es óptima** para el balance tiempo/calidad
2. **El filtro epsilon es útil** y debe mantenerse
3. **Los operadores actuales (uniforme + swap) son adecuados**
4. **La búsqueda local tiene impacto marginal** pero puede mantenerse para robustez

### Posibles Optimizaciones Futuras (Opcionales)

Si se prioriza velocidad sobre calidad mínima:
- Considerar desactivar búsqueda local (ahorra 3% tiempo, impacto mínimo en calidad)
- Mantener filtro epsilon (mejora calidad con poco costo)

## Posición en el Plan de Experimentos

### La Ablación como Fase 6: Validación Científica

La ablación debería ser una **FASE 6** que se ejecuta **DESPUÉS** de tener la configuración final:

```
FASE 1: Prueba Rápida
FASE 2: Comparación de Operadores
FASE 3: Tunning Multiobjetivo
FASE 4: Comparación Estándar vs Memético
FASE 5: Visualizaciones Finales
FASE 6: Estudio de Ablación ← NUEVA FASE
```

### ¿Por qué después de la Fase 5?

1. **Validación científica**: Confirma que cada componente es necesario
2. **Justificación del diseño**: Demuestra rigor metodológico
3. **No cambia la configuración**: Solo valida y explica
4. **Análisis complementario**: Proporciona insights adicionales

### Propósito de la Fase 6

- **Validar** que cada componente del algoritmo es necesario
- **Justificar** científicamente el diseño del algoritmo
- **Documentar** el impacto de cada componente
- **Proporcionar** evidencia para el informe de tesis

## Flujo Actualizado

```
FASE 1-5: Configuración y Resultados Finales
  ↓
FASE 6: Estudio de Ablación
  ↓
  → Genera: ablacion_resumen_*.csv
  → Genera: ablacion_detallado_*.csv
  ↓
  → ACCIÓN: Documentar resultados en Cap4/Cap5
  → ACCIÓN: Justificar diseño del algoritmo
  ↓
FIN
```

## Recomendaciones

1. **Mantener configuración actual**: No requiere cambios
2. **Documentar ablación en Cap4**: Agregar sección de validación
3. **Usar resultados para justificación**: En Cap3 (metodología) y Cap4 (resultados)
4. **Considerar como Fase 6**: Agregar al PLAN_EXPERIMENTOS.md

