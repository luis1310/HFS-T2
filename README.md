# Actualizacion de HFS - T2 a HFS-T3
Proyecto de tesis 3 (taller de investigación)
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