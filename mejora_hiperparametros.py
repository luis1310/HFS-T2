from Algoritmo_evo.algoritmo_evo import *
from reenumeración_de_iteraciones import *

# Definir listas de funciones para cada operador
metodos_seleccion = [seleccion_por_torneo, seleccion_por_ranking, seleccion_por_ruleta]
# metodos_seleccion = [seleccion_por_ruleta]
metodos_cruzamiento = [cruce_1_punto, cruce_2_puntos]
# metodos_cruzamiento = [cruce_1_punto, cruce_2_puntos]
metodos_mutacion = [mutacion_intercambio_por_etapa, mutacion_aleatoria]
# metodos_mutacion = [mutacion_intercambio_por_etapa, mutacion_aleatoria]

iteraciones_mod = 100

indice_de_mod = 0

# Almacenar resultados
resultados = []

archivo_csv = "resultados_algoritmo.csv"
archivo_salida = "resultados_algoritmo_renumerado.csv"


# Verificar si el archivo existe y, si no, crearlo con el encabezado
try:
    with open(archivo_csv, "r") as f:
        pass  # Si el archivo existe, no hace nada
except FileNotFoundError:
    with open(archivo_csv, "w", newline="") as f:
        escritor_csv = csv.writer(f)
        escritor_csv.writerow(
            [
                "Iteracion",
                "Metodo_Seleccion",
                "Metodo_Cruce",
                "Metodo_Mutacion",
                "Mejor_Fitness",
            ]
        )


def guardar_datos_csv(datos):
    with open(archivo_csv, "a", newline="") as f:
        escritor_csv = csv.writer(f)
        escritor_csv.writerows(datos)  # Añadir datos al final del archivo


# Ejecutar todas las combinaciones posibles
# Bucle para cada combinación de métodos
for seleccion in metodos_seleccion:
    for cruce in metodos_cruzamiento:
        for mutacion in metodos_mutacion:
            # Crear datos de cada modelo

            print(
                f"Modelo {indice_de_mod +1}: {seleccion.__name__}, {cruce.__name__}, {mutacion.__name__}"
            )
            for iteracion in range(iteraciones_mod):
                resultados = []
                print(
                    f"########################## Iteración {iteracion + 1} ##############################"
                )
                # Ejecutar e l algoritmo evolutivo
                inicio = time.time()
                # Ejecutar el algoritmo genético con elitismo
                (
                    mejor_individuo,
                    mejor_fitness,
                    mejor_generacion,
                    mejores_fitness_por_generacion,
                ) = algoritmo_evolutivo(poblacion_init, tamano_poblacion)
                fin = time.time()
                print("Tiempo de ejecución: ", fin - inicio)
                print(
                    "#####################################################################"
                )
                resultados.append(
                    [
                        iteracion + 1,
                        seleccion.__name__,
                        cruce.__name__,
                        mutacion.__name__,
                        mejor_fitness,
                    ]
                )
                # Guardar los resultados de cada ejecución en el CSV
                guardar_datos_csv(resultados)
            print("\n\n")

            indice_de_mod += 1

            # """
renumerar_iteraciones(archivo_csv, archivo_salida)
indice_de_mod = 0
