from Aptitud.funcion_fitness import *
from Cruce.cruce1 import *
from Mutacion.mutacion1 import *
from Parametros.Parametros_tot import *
from Poblacion.Fun_poblacion import *
from Seleccion.seleccion1 import *

##Algoritmo evolutivo v0.2
def algoritmo_evolutivo(num_generaciones, poblacion, incrementos, tiempos_iniciales):

    for generacion in range(num_generaciones):
        # Evaluar la aptitud de la poblacion
        aptitudes = [fitness(c, tiempos_iniciales, incrementos) for c in poblacion]

        # Seleccionar padres usando la seleccion por torneo
        padres = seleccion_por_torneo(poblacion)

        #Crear nueva población por cruce y mutación
        nueva_poblacion = []
        for i in range(0, len(padres), 2):
            padre1, padre2 = padres[i], padres[i+1]
            hijo1, hijo2 = cruce(padre1, padre2)
            nueva_poblacion.append(mutacion(hijo1))
            nueva_poblacion.append(mutacion(hijo2))
        
        # Actualizar la poblacion
        poblacion = nueva_poblacion
    
    # Encontrar el mejor individuo (cromosoma) de la poblacion (el de mayor aptitud)
    mejor_cromosoma = max(poblacion, key=lambda cromosoma: fitness(cromosoma, tiempos_iniciales, incrementos))

    # Calcular el tiempo del mejor individuo
    tiempo_total = 1/fitness (mejor_cromosoma, tiempos_iniciales, incrementos)

    print("Mejor orden de pedidos:", mejor_cromosoma)
    print("Tiempo total:", tiempo_total)

