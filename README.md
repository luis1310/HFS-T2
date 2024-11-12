# HFS-T2
Proyecto tesis 2:

## Versión 0.1:
- Definición de parametros del problema (tiempos iniciales de las maquinas, maquinas asignadas por etapa, limite de trabajo, factor de enfriamiento, tiempo de enfriamiento, rango de incrementos porcentuales)
- Definición inicial de la funcion de aptitud
- Definición inicial de la función de selección por torneo, cruce y mutación
- Definición inicial de la función que general la población
- Implementación inicial del algoritmo evolutivo.

## Versión 0.2:
- El método de mutación ahora considera las asignaciones por cada maquina
- La función que inicializa la población ahora considera las maquinas asignadas por etapa para cada individuo de la población

## Versión 0.3:
- Se crea una funcion "DEMO" para imprimir el recorrido de cada maquina así como su tiempo en cada maquina.
- Mejora en la función de "selección por torneo", ahora se pasa una lista de valores de fitness a la función
- Añadido parametro "maquinas por etapa"
- Modificado función de mutación para que trabaje con el parametro "maquinas por etapa"
- Modificado función de inicialización de población para que trabaje con el parametro "maquinas por etapa"
- Mejora en la función de algoritmo evolutivo, trabaja con los parametros añadidos.