from Aptitud.funcion_fitness import *
from Cruce.cruce_funciones import *
from Mutacion.mutacion1 import *
from Parametros.Parametros_tot import *
from Poblacion.Fun_poblacion import *
from Seleccion.seleccion_funciones import *
""""
# Modificacion del algortimo evolutivo (v0.4)
- Añadidos otros parametros
- Cambios en nombres de variables
# Modificación del algoritmo evolutivo (v0.5)
- Añadida la libreria copy para realizar copia profunda y garantizar que el mejor individuo sea guardado
de esta forma se busca que el mejor fitness encontrado sea del mejor individuo
# Modificación del algoritmo evolutivo (v0.6)
- Ahora la función tambien retorna los mejores fitness por generación para plotearlos en una grafica
# Modificación del algoritmo evolutivo (v0.7)
- Correccion del proceso de seleccion y cruzamiento
- Mejora y limpieza del codigo
"""
# Algoritmo evolutivo v0.6
def algoritmo_evolutivo(poblacion, tamano_poblacion=tamano_poblacion,num_generaciones=num_generaciones, prop_elitismo=prop_elitismo):
    mejor_fitness = 0
    mejor_generacion = 0
    mejor_individuo = None
    num_elite= int(tamano_poblacion * prop_elitismo)
    mejores_fitness_por_generacion = []


    for generacion in range(num_generaciones):
        nueva_poblacion = []
        # Evaluar la aptitud de la poblacion
        fitness_values = [fitness(c) for c in poblacion]
        
        # Almacenar mejor individuo (cromosoma) y su indice
        fitness_max = max(fitness_values)
        mejor_idx = fitness_values.index(fitness_max)

        # Almacenar peor individuo, fitness promedio por generación y mejores resultados por generación
        fitness_min = min(fitness_values)
        fitness_promedio = sum(fitness_values) / len(fitness_values)
        mejores_fitness_por_generacion.append(fitness_max)  # Almacena el mejor fitness de esta generación

        # Guardar una copia profunda del mejor individuo
        individuo_actual = copy.deepcopy(poblacion[mejor_idx])  # Copia profunda del mejor individuo

         # Rastreo de cambios en el mejor individuo
        if mejor_individuo:
            fitness_mejor_guardado = fitness(mejor_individuo)
            print(f"Generación {generacion}: Fitness del mejor guardado = {fitness_mejor_guardado:.16f}")

        # Actualizar el mejor individuo, mejor generación y mejor fitness
        if fitness_max > mejor_fitness:
            mejor_fitness = fitness_max
            mejor_generacion = generacion
            mejor_individuo = copy.deepcopy(individuo_actual)  # Copia profunda del mejor individuo correctamente
        # Mostrar la generación y el mejor fitness de la misma 
        print(f"Generación {generacion + 1}: Mejor fitness = {fitness_max:.16f}, Fitness promedio = {fitness_promedio:.16f}, Peor fitness = {fitness_min:.16f}")

        # Modificación: se añade una proporción de elitismo
        # Guardar mejores resultados (Elitismo)
        elite = [copy.deepcopy(poblacion[i]) for i in sorted(range(len(fitness_values)), key=lambda x: fitness_values[x], reverse=True)[:num_elite]]

        ################################## Modificacion v0.7 ##################################
        ### Seleccion y cruzamiento ###
        while len(nueva_poblacion) < tamano_poblacion:
            #padre1, padre2 = seleccion_por_ranking(poblacion, fitness_values)
            #padre1, padre2 = seleccion_por_ruleta(poblacion, fitness_values)
            #padre1, padre2 = seleccion_por_truncamiento(poblacion, fitness_values, 0.5)
            padre1, padre2 = seleccion_por_torneo(poblacion, fitness_values)
            hijo1, hijo2 = cruce(padre1, padre2)
            nueva_poblacion.append(hijo1)
            nueva_poblacion.append(hijo2)
        poblacion = nueva_poblacion
        ################################## Modificacion v0.7 ##################################

        # Generación de una nueva población por mutación
        poblacion = mutacion1(poblacion)

        # Añadir resultados guardados (Elite) a la lista:
        poblacion[:num_elite] = elite
    
    print(f"\nMejor fitness encontrado en la generación {mejor_generacion + 1}: {mejor_fitness:.16f}")
    print(f"Mejor tiempo encontrado en la generación {mejor_generacion + 1}: {1/mejor_fitness:.16f}")
    print(f"Mejor orden de pedidos: {mejor_individuo}")
    
    return mejor_individuo, mejor_fitness, mejor_generacion+1, mejores_fitness_por_generacion

