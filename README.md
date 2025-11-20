# Actualizacion de HFS - T2 a HFS-T3
Proyecto de tesis 3 (taller de investigación)

## Version 1.1.3b:
- **Lectura de operadores desde `config.yaml`**:
  - **Archivo modificado**: `tesis3/config/config.yaml` actualizado con nueva sección `algorithm.operators`.
  - **Nueva sección**: `algorithm.operators` con campos `cruce` y `mutacion` para centralizar configuración de operadores.
    - Valores por defecto: `cruce: 'uniforme'`, `mutacion: 'invert'`
    - Opciones de cruce: `uniforme`, `pmx`, `un_punto`, `dos_puntos`
    - Opciones de mutación: `invert`, `swap`, `scramble`, `insert`
  - **Scripts actualizados**:
    - `ejecutar_memetico.py`: Elimina operadores hardcodeados, lee `cruce` y `mutacion` desde config.yaml, funciones dinámicas.
    - `visualizar_frente_memetico.py`: Elimina operadores hardcodeados, lee `cruce` y `mutacion` desde config.yaml, funciones dinámicas.
  - Ambos scripts ahora imprimen operadores utilizados en mensajes de inicio para trazabilidad.
  - Consistencia total entre fases experimentales en uso de operadores.

- **Flujo de trabajo mejorado**:
  - Fase 2 (Comparación Operadores) → genera YAML → actualizar operadores en config.yaml manualmente.
  - Fase 3 (Tunning) → lee operadores desde config.yaml → genera YAML → actualizar hiperparámetros en config.yaml manualmente.
  - Fases 4 y 5 → leen TODO automáticamente desde config.yaml (operadores + hiperparámetros) sin modificar código.
  - **Beneficios**: Sin modificación de código Python entre fases, trazabilidad completa, reproducibilidad mejorada.

- **Documentación del flujo completo actualizada**:
  - `PLAN_EXPERIMENTOS.md`: Diagrama de flujo completo con puntos de actualización de config.yaml claramente marcados.
  - Instrucciones paso a paso para actualizar config.yaml entre fases con ejemplos concretos.
  - Muestra contenido de archivos YAML generados y cómo extraer valores para copiar a config.yaml.
  - Lista completa de operadores disponibles en cada categoría.

- **Resumen de archivos modificados**:
  - `tesis3/config/config.yaml`: Nueva sección `algorithm.operators`.
  - `tesis3/experiments/ejecutar_memetico.py`: Lectura dinámica de operadores.
  - `tesis3/experiments/visualizar_frente_memetico.py`: Lectura dinámica de operadores.
  - `PLAN_EXPERIMENTOS.md`: Flujo completo con instrucciones detalladas.

## Version 1.1.3:
- **Normalización de score agregado mejorada**:
  - Valores de referencia ahora se leen desde `config.yaml` en lugar de estar hardcodeados.
  - Agregada sección `experiments.valores_referencia` en `config.yaml` (makespan: 2000, balance: 300, energia: 700).
  - Actualización automática en todos los scripts de paralelización: `tunning_multimetrica.py`, `comparacion_operadores.py`, `prueba_rapida.py`, `ejecutar_memetico.py`.
  - Valores proporcionales al número de pedidos (50 min/pedido, 7.5 min/pedido, 17.5 kWh/pedido) para facilitar escalamiento.

- **Paralelización completa de `ejecutar_memetico.py`**:
  - Actualizado de 5 semillas secuenciales a 30 semillas con paralelización real.
  - Implementación de `ProcessPoolExecutor` con detección automática de núcleos del sistema.
  - Menú interactivo para seleccionar entre núcleos físicos, lógicos, modo seguro o personalizado.
  - Detección y continuación desde resultados previos.
  - Guardado de resultados parciales durante ejecución.
  - Generación de 3 archivos de salida: parcial, final y resumen en YAML.
  - Lee hiperparámetros desde `config.yaml`: Población, generaciones, probabilidades de cruce/mutación, parámetros meméticos.
  - Reducción de tiempo estimado de ~10-15 min a ~2-3 min (con 32 núcleos).

- **Corrección de objetivos multiobjetivo**:
  - Corrección en `ejecutar_memetico.py`: cambiado de 4 objetivos a 3 objetivos (makespan, balance, energía).
  - Enfriamiento no es un objetivo separado, afecta al makespan.
  - Consistencia en todos los scripts de paralelización con 3 objetivos.

- **Guardado de mejores configuraciones en YAML**:
  - `tunning_multimetrica.py`: Guarda automáticamente `mejor_configuracion_tunning_TIMESTAMP.yaml`.
  - `comparacion_operadores.py`: Guarda automáticamente `mejor_configuracion_operadores_TIMESTAMP.yaml`.
  - `ejecutar_memetico.py`: Guarda `comparacion_memetica_resumen_TIMESTAMP.yaml`.
  - Formato YAML con configuración completa y métricas promedio con desviaciones estándar.

- **Prevención de errores de directorio**:
  - Agregado `os.makedirs('tesis3/results', exist_ok=True)` en todos los scripts que escriben archivos.
  - Scripts afectados: `tunning_multimetrica.py`, `comparacion_operadores.py`, `prueba_rapida.py`, `unir_resultados_parciales.py`, `comparar_operadores.py`, `comparar_operadores_corregido.py`, `analizar_mejores_soluciones.py`, `visualizar_frente_memetico.py`, `ejecutar_memetico.py`.

- **Reproducibilidad mejorada**:
  - Agregado `random.seed(semilla)` junto a `np.random.seed(semilla)` en funciones de ejecución.
  - Garantiza reproducibilidad completa usando ambos generadores de números aleatorios (Python estándar y NumPy).

- **Documentación del informe de tesis actualizada**:
  - Capítulo 3: Agregada sección completa "Métrica de Comparación: Score Agregado".
  - Justificación matemática formal de valores de referencia como métrica ordinal.
  - Demostración de invarianza del orden relativo bajo transformaciones de escala.
  - Referencias bibliográficas de respaldo (Deb et al., Zitzler et al.).
  - Explicación de selección de valores conservadores proporcionales al tamaño del problema.

- **Optimización de archivos parciales**:
  - Cambio de múltiples archivos CSV parciales con timestamp a un solo archivo sobreescrito.
  - Scripts afectados: `tunning_multimetrica.py`, `comparacion_operadores.py`, `prueba_rapida.py`, `ejecutar_memetico.py`.
  - Reduce drásticamente el número de archivos generados (de cientos a 1 por script).
  - Mejora la continuación de experimentos interrumpidos.

- **Plan de experimentos completo**:
  - Documento `PLAN_EXPERIMENTOS.md` con 5 fases de experimentación.
  - Tabla de paralelización por fase con información de núcleos y tiempos estimados.
  - Instrucciones detalladas para cada script (objetivo, comandos, resultados esperados).
  - Gestión de interrupciones y reanudación de experimentos.
  - Flujo actualizado: Fase 3 (tunning) → actualizar config.yaml → Fase 4 (memético) → Fase 5 (visualización).

## Version 1.1.2e:
- Pipeline de CI habilitado con GitHub Actions (`.github/workflows/ci.yml`):
  - Lint estricto: flake8 (algorithms/operators), black e isort.
  - Tests con timeout (`pytest-timeout`).
  - Gates de cobertura por paquete: `core/` y `operators/` con umbral ≥85%.
  - Aislamiento de cobertura en CI vía `-o addopts=` y `.coveragerc_ci`.
- Configuración de estilo y cobertura:
  - `.flake8` (largo de línea 100, reglas compatibles con black).
  - `.coveragerc_ci` para medir solo `tesis3/src/core` y `tesis3/src/operators`.
- Tests mínimos añadidos para factibilidad de operadores (cruce y mutación) y validaciones de cromosomas/población.
- Corrección del operador `invert` stage-aware (inversión dentro de una sola etapa, preservando validez).
- Documentación actualizada:
  - Sección “CI (checks mínimos como gates)” en `tesis3/README.md`.
  - Diagrama del pipeline del algoritmo en la tesis (Capítulo 3) y ajuste de complejidad.
## Version 1.1.2d:
- Se añade configuración para pruebas con pytest, incluyendo archivos de configuración y un script de instalación.
- Se implementa un nuevo script para comparar el rendimiento de NSGA-II estándar y memético, y se actualiza el README para reflejar los cambios en la estructura de pruebas.

## Version 1.1.2c:
- Se añaden nuevos scripts para realizar análisis y comparaciones de operadores en el algoritmo NSGA-II, incluyendo la ejecución de la mejor configuración encontrada (temporalmente) y un diagnóstico de la población inicial.
- Se implementan funciones para evaluar el rendimiento de diferentes combinaciones de operadores y se guardan los resultados en archivos CSV para su posterior análisis.

## Version 1.1.2b:
- Implementación del algoritmo NSGA-II para optimización multiobjetivo, incluyendo funciones de cruce y mutación específicas para un enfoque stage-aware.
- Se añade un script para ejecutar el algoritmo y se implementan funciones de evaluación de fitness para cuatro objetivos: makespan, balance, enfriamientos y energía. (Actualizado de la versión anterior)
- Se inicializa la población de manera aleatoria y se organiza el código en módulos para mejorar la estructura del proyecto.

## Version 1.1.2a:
- Refactorización en rama tesis3-dev
- Puesta a punto del repositorio, esquema de datos, tests mínimos y CI.

## Version 1.1.1:
- Implementación del algoritmo evolutivo multiobjetivo NSGA-II con 4 objetivos: Makespan, Balance de carga, Minimización de enfriamientos y Consumo energético. (ETAPA INICIAL)
- Se añaden scripts para ejecutar el algoritmo y realizar pruebas comparativas entre enfoques mono-objetivo y multiobjetivo. (Comparativa entre HFS-T2 y HFST-T3)
- Se incluyen funciones de evaluación de fitness y parámetros energéticos necesarios para el cálculo. (Modificación del archivo de parametros)
- Además, se generan visualizaciones del frente de Pareto y se guardan resultados en archivos CSV.

# HFS-T2
Proyecto tesis 2:

## Versión 0.1:
- Definición de parametros del problema (tiempos iniciales de las maquinas, maquinas asignadas por etapa, limite de trabajo, factor de enfriamiento, tiempo de enfriamiento, rango de incrementos porcentuales)
- Definición inicial de la funcion de aptitud
- Definición inicial de la función de selección por torneo, cruce y mutación
- Definición inicial de la función que general la población
- Implementación inicial del algoritmo evolutivo.

## Versión 0.2:
- Implementación de la librería tiem para medir el tiempo de ejecución del algoritmo.
- El método de mutación ahora considera las asignaciones por cada maquina
- La función que inicializa la población ahora considera las maquinas asignadas por etapa para cada individuo de la población

## Versión 0.3:
- Se crea una funcion "DEMO" para imprimir el recorrido de cada maquina así como su tiempo en cada maquina.
- Mejora en la función de "selección por torneo", ahora se pasa una lista de valores de fitness a la función
- Añadido parametro "maquinas por etapa"
- Modificado función de mutación para que trabaje con el parametro "maquinas por etapa"
- Modificado función de inicialización de población para que trabaje con el parametro "maquinas por etapa"
- Mejora en la función de algoritmo evolutivo, trabaja con los parametros añadidos.
- Se crea un array de valores de incrementos para comparación de resultados.

## Versión 0.4:
- Mejora en la función de mutación: la mutación se realiza en cada bucle del pedido.
- Mejora en la función del algoritmo evolutivo: Se guarda un porcentaje de los mejores individuos de la generación y se reinsertan en la nueva población de la generación siguiente
- Error encontrado: El mejor fitness encontrado no coincide con el fitness del mejor individuo encontrado.

## Versión 0.5:
- Implementación de la librería copy: Por medio de la copia profunda se busca el mantener si o si el mejor individuo y de esta forma solucionar el error previamente encontrado.
- La función del algoritmo evolutivo se modifica para usar la librería copy para realziar copias profundas
- Se añade verificación de coincidencia del mejor fitness encontrado y del fitness del mejor individuo encontrado

## Versión 0.6:
- Añadida función para plotear una grafica con la evolución del fitness
- Añadidos nuevos metodos de selección (ranking y ruleta)
- Añadido nuevo metodo de cruzamiento (cruzamiento en 2 puntos)

## Versión 0.7:
- Cruzamiento: Se modifica los metodos de cruzamiento para que solo tomen los padres
- Seleccion: Modificación y corrección de las funciones de selección para que solo tomen
- Correccion del proceso de seleccion y cruzamiento en la función del algoritmo evolutivo
- Mejora y limpieza del codigo

## Versión 0.8:
- Ahora la funcion de cruce añade el hijo/padre que tenga mejor fitness
- Modificación de la función de mutación, muta a una maquina de un pedido a otra distinta (de haber una disponible)
- Ahora la funcion, que genera la población, solo genera individuos unicos al trabajar con conjuntos y tuplas

## Versión 0.9:
- Añadida nueva funcion de mutacion (Mutación aleatoria por etapas)
- Modifcacion de la funcion de cruce en 1 punto: Ahora la funcion de cruce toma los dos mejores individuos entre los padres y los hijos producto del cruzamiento

### v0.9.1:
- Actualización de funcion de cruce en 2 puntos
- Añadidas librerias pandas y csv (para guardar posteriormente los resultados de las iteraciones en un archivo csv)

### v0.9.2:
- Formateo de los archivos (se uso Black formatter para que el código se vea mas presentable)
- Se añadió una población inicial de prueba con parámetros numéricos preestablecidos que se usaran para las ejecuciones posteriores de cada modelo posible y recopilación de información de los mismos.

## Versión 1.0:
- Añadidas funciones para recopilar información (meta algoritmo), añadida función que grafica los modelos y cada una de sus confiuraciones y los guarda en una carpeta por cada modelo.

## Versión 1.1 en adelante:
- Se añade más datos para los modelos del algoritmo evolutivo.