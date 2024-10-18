from Aptitud.funcion_fitness_v0_1 import *
from Cruce.cruce1_v_0_1 import *
from Mutacion.mutacion1_v0_1 import *
from Parametros.Parametros_tot import *
from Poblacion.poblacion_v0_1 import *
from Seleccion.seleccion1_v_0_1 import *

##Algoritmo evolutivo
def algoritmo_evolutivo(num_generaciones, poblacion):

    for generacion in range(num_generaciones):
        aptitudes = [fitness(c) for c in poblacion]
        padres = seleccion_por_torneo(poblacion)

        nueva_poblacion = []
        for i in range(0, len(padres), 2):
            padre1, padre2 = padres[i], padres[i+1]
            hijo1, hijo2 = cruce(padre1, padre2)
            nueva_poblacion.append(mutacion(hijo1))
            nueva_poblacion.append(mutacion(hijo2))

        poblacion = nueva_poblacion

    mejor_cromosoma = max(poblacion, key=fitness)
    print("Mejor orden de pedidos:", mejor_cromosoma)
    print("Tiempo del mejor orden de pedidos:", fitness(mejor_cromosoma))

