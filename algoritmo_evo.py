from Aptitud.funcion_fitness_v0_1 import *
from Cruce.cruce1_v_0_1 import *
from Mutacion.mutacion1_v0_1 import *
from Parametros.Parametros_tot import *
from Poblacion.poblacion_v0_1 import *
from Seleccion.seleccion1_v_0_1 import *

##Algoritmo evolutivo
def algoritmo_evolutivo():
    poblacion_size = 50
    num_generaciones = 100
    poblacion = inicializar_poblacion(poblacion_size, num_pedidos)

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
    print("Tiempo total:", fitness(mejor_cromosoma))

# Ejecutar el algoritmo
algoritmo_evolutivo()
