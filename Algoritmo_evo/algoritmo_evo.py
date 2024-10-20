from Aptitud.funcion_fitness import *
from Cruce.cruce1 import *
from Mutacion.mutacion1 import *
from Parametros.Parametros_tot import *
from Poblacion.Fun_poblacion import *
from Seleccion.seleccion1 import *
# Modificacion del algortimo evolutivo (v.04)
# Añadidos otros parametros
# Cambios en nombres de variables
# Modificación del algoritmo evolutiv (v0.5)
# Añadida la libreria copy para realizar copia profunda y garantizar que el mejor individuo sea guardado
# de esta forma se busca que el mejor fitness encontrado sea del mejor individuo
# Algoritmo evolutivo v0.4
def algoritmo_evolutivo(poblacion, tamano_poblacion, tiempos_iniciales, incrementos, maquinas_por_etapa, num_generaciones, k, tasa_mutacion, prop_elitismo):
    mejor_fitness = 0
    mejor_generacion = 0
    mejor_individuo = None
    num_elite= int(tamano_poblacion * prop_elitismo)
    mejores_fitness_por_generacion = []


    for generacion in range(num_generaciones):
        # Evaluar la aptitud de la poblacion
        fitness_values = [fitness(c, tiempos_iniciales, incrementos) for c in poblacion]
        
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
            fitness_mejor_guardado = fitness(mejor_individuo, tiempos_iniciales, incrementos)
            print(f"Generación {generacion}: Fitness del mejor guardado = {fitness_mejor_guardado:.16f}")

        # Actualizar el mejor individuo, mejor generación y mejor fitness
        if fitness_max > mejor_fitness:
            mejor_fitness = fitness_max
            mejor_generacion = generacion
            mejor_individuo = copy.deepcopy(individuo_actual)  # Copia profunda del mejor individuo correctamente
        # Mostrar la generación y el mejor fitness de la misma 
        print(f"Generación {generacion + 1}: Mejor fitness = {fitness_max:.16f}")

        # Modificación: se añade una proporción de elitismo
        # Guardar mejores resultados (Elitismo)
        elite = [copy.deepcopy(poblacion[i]) for i in sorted(range(len(fitness_values)), key=lambda x: fitness_values[x], reverse=True)[:num_elite]]

        # Seleccionar padres usando la seleccion por torneo
        poblacion = seleccion_por_torneo(poblacion, fitness_values, k)

        # Crear nueva población por cruce y mutación
        poblacion = cruce(poblacion)
        poblacion = mutacion1(poblacion, maquinas_por_etapa, tasa_mutacion)

        # Añadir resultados guardados (Elite) a la lista:
        poblacion[:num_elite] = elite
    
    # Verificación final
    fitness_mejor_individuo = fitness(mejor_individuo, tiempos_iniciales, incrementos)
    print(f"Mejor fitness encontrado: {mejor_fitness:.16f}")
    print(f"Fitness del mejor individuo: {fitness_mejor_individuo:.16f}")

    if mejor_fitness != fitness_mejor_individuo:
        print("¡Advertencia! El mejor fitness encontrado y el fitness del mejor individuo no coinciden.")
    else:
        print("El mejor fitness encontrado y el fitness del mejor individuo coinciden correctamente.")

    
    print(f"\nMejor fitness encontrado en la generación {mejor_generacion + 1}: {mejor_fitness:.16f}")
    print(f"Mejor tiempo encontrado en la generación {mejor_generacion + 1}: {1/mejor_fitness:.16f}")
    print(f"Mejor orden de pedidos: {mejor_individuo}")
    
    return mejor_individuo, mejor_fitness, mejor_generacion

