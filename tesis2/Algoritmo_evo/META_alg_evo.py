from Aptitud.funcion_fitness import *
from Cruce.cruce_funciones import *
from Mutacion.mutacion_funciones import *
from Parametros.Parametros_tot import *
from Poblacion.Fun_poblacion import *
from Seleccion.seleccion_funciones import *

""""
# Modificacion del algortimo evolutivo (v1.1)
- Modificación en los parametros que utiliza la funcion
"""


# META Algoritmo evolutivo v1.1
def meta_algoritmo_evolutivo(
    poblacion,
    seleccion_pad,
    cruza_ind,
    mutacion_pob,
    prob_cruz,
    prob_mut,
    tamano_poblacion,
    num_generaciones=num_generaciones,
    prop_elitismo=prop_elitismo
):
    mejor_fitness = 0
    mejor_generacion = 0
    mejor_individuo = None
    num_elite = int(tamano_poblacion * prop_elitismo)
    mejores_fitness_por_generacion = []
    mejores_20p_fit = []

    for generacion in range(num_generaciones):
        nueva_poblacion = []
        # Evaluar la aptitud de la poblacion
        fitness_values = [fitness(c) for c in poblacion]

        # Almacenar mejor individuo (cromosoma) y su indice
        fitness_max = max(fitness_values)
        mejor_idx = fitness_values.index(fitness_max)

        # Almacenar mejores resultados por generación
        mejores_fitness_por_generacion.append(
            fitness_max
        )  # Almacena el mejor fitness de esta generación

        # Guardar una copia profunda del mejor individuo
        individuo_actual = copy.deepcopy(
            poblacion[mejor_idx]
        )  # Copia profunda del mejor individuo

        # Actualizar el mejor individuo, mejor generación y mejor fitness
        if fitness_max > mejor_fitness:
            mejor_fitness = fitness_max
            mejor_generacion = generacion
            mejor_individuo = copy.deepcopy(
                individuo_actual
            )  # Copia profunda del mejor individuo correctamente

        # Modificación: se añade una proporción de elitismo
        # Guardar mejores resultados (Elitismo)
        elite = [
            copy.deepcopy(poblacion[i])
            for i in sorted(
                range(len(fitness_values)),
                key=lambda x: fitness_values[x],
                reverse=True,
            )[:num_elite]
        ]

        ### Seleccion y cruzamiento ###
        while len(nueva_poblacion) < tamano_poblacion:
            padre1, padre2 = seleccion_pad(poblacion, fitness_values)
            hijo1, hijo2 = cruza_ind(padre1, padre2, prob_cruz)
            nueva_poblacion.append(hijo1)
            nueva_poblacion.append(hijo2)
        poblacion = nueva_poblacion

        # Generación de una nueva población por mutación
        poblacion = mutacion_pob(poblacion, prob_mut)

        # Añadir resultados guardados (Elite) a la lista:
        poblacion[:num_elite] = elite
    print(f"Mejor tiempo encontrado: {1/mejor_fitness:.16f}")
    mejores_20p_fit = mejores_fitness_por_generacion[int(0.8*num_generaciones):]

    return (
        mejor_individuo,
        mejor_fitness,
        mejor_generacion + 1,
        mejores_fitness_por_generacion,
        mejores_20p_fit,
    )
