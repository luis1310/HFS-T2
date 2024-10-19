from Aptitud.funcion_fitness import *
from Cruce.cruce1 import *
from Mutacion.mutacion1 import *
from Parametros.Parametros_tot import *
from Poblacion.Fun_poblacion import *
from Seleccion.seleccion1 import *
# Modificacion del algortimo evolutivo
# Añadidos otros parametros
# Cambios en nombres de variables

## Algoritmo evolutivo v0.3
def algoritmo_evolutivo(poblacion, poblacion_size, tiempos_iniciales, incrementos, maquinas_por_etapa, num_generaciones, k, tasa_mutacion):
    mejor_fitness = 0
    mejor_generacion = 0
    mejor_individuo = None

    for generacion in range(num_generaciones):
        # Evaluar la aptitud de la poblacion
        fitness_values = [fitness(c, tiempos_iniciales, incrementos) for c in poblacion]
        
        # Almacenar mejor individuo (cromosoma) y su indice
        fitness_max = max(fitness_values)
        mejor_idx = fitness_values.index(fitness_max)

        # Actualizar el mejor individuo, mejor generación y mejor fitness
        if fitness_max > mejor_fitness:
            mejor_fitness = fitness_max
            mejor_generacion = generacion
            mejor_individuo = poblacion[mejor_idx]
        # Mostrar la generación y el mejor fitness de la misma 
        print(f"Generación {generacion + 1}: Mejor fitness = {fitness_max:.16f}")

        # Seleccionar padres usando la seleccion por torneo
        poblacion = seleccion_por_torneo(poblacion, k)

        #Crear nueva población por cruce y mutación
        poblacion = cruce(poblacion)
        poblacion = mutacion(poblacion, maquinas_por_etapa, tasa_mutacion)

    
    print(f"\nMejor fitness encontrado en la generación {mejor_generacion + 1}: {mejor_fitness:.16f}")
    print(f"Mejor tiempo encontrado en la generación {mejor_generacion + 1}: {1/mejor_fitness:.16f}")
    print(f"Mejor orden de pedidos: {mejor_individuo}")
    
    return mejor_individuo, mejor_fitness, mejor_generacion

