from Algoritmo_evo.algoritmo_evo import *
from reenumeración_de_iteraciones import *
from Algoritmo_evo.META_alg_evo import *

"""
tamano_poblacion_arr = [random.randint(49, 151) for _ in range(num_config)]
tasa_mutacion_arr = [random.uniform(0.1, 0.5) for _ in range(num_config)]
tasa_cruzamiento_arr = [random.uniform(0.5, 0.99) for _ in range(num_config)]
"""

# Aplicación del meta algoritmo v1.1

# Definir listas de funciones para cada operador
metodos_seleccion = [seleccion_por_torneo, seleccion_por_ranking, seleccion_por_ruleta]
metodos_cruzamiento = [cruce_1_punto, cruce_2_puntos]
metodos_mutacion = [mutacion_intercambio_por_etapa, mutacion_aleatoria]

# Configuraciones de hiperparametros numericos para el ejercicio

num_config = 10

tamano_poblacion_arr = [70, 210, 240, 90, 240, 170, 90, 70, 190, 180]
tasa_mutacion_arr = [
    0.4263064349527299,
    0.18709717720279678,
    0.490015123270944,
    0.19897279695150782,
    0.19710262526458855,
    0.2627083516388411,
    0.16473342809902475,
    0.11782972115214507,
    0.34694846442880817,
    0.15067767889314274,
]
tasa_cruzamiento_arr = [
    0.6201369561158429,
    0.6641427039708248,
    0.5748538522008351,
    0.8886966554183677,
    0.8070389690090312,
    0.8690387173349006,
    0.5944471136645904,
    0.8710230131356245,
    0.7575243079969969,
    0.6538401618566114,
]


# Indices:
iteraciones_mod = 1
ite_ind = 10  # 0 cuando va de 1 a 10, 10 cuando va de 11 a 20, 20 cuando va de 21 a 30, y así sucesivamente
indice_de_mod = 0
indice_de_config = 0

# Almacenar resultados
resultados = []
coleccion_mejores_resultados = []
coleccion_array_fit = []

archivo_csv = "resultados_META_algoritmo.csv"
archivo_salida = "resultados_META_algoritmo_renumerado.csv"


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
                "Configuracion",
                "Metodo_Seleccion",
                "Metodo_Cruce",
                "Metodo_Mutacion",
                "Mejor_Fitness",
                "Mejor_generacion",
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
            # Población para mejora de hiperparametros textuales
            poblacion = inicializar_poblacion(
                tamano_poblacion, maquinas_por_etapa, num_pedidos
            )
            print(
                "\n\n################################################################################"
            )
            print(
                f"Modelo {indice_de_mod +1}: ({seleccion.__name__}, {cruce.__name__}, {mutacion.__name__})"
            )
            print(
                "################################################################################"
            )
            for iteracion in range(iteraciones_mod):
                coleccion_mejores_resultados.clear()
                coleccion_array_fit.clear()
                print(
                    "\n#####################################################################"
                )
                print(
                    f"########################## Iteración {iteracion + 1 + ite_ind} ##############################"
                )
                print(
                    "#####################################################################\n"
                )
                for indice_de_config in range(num_config):
                    print("*********************")
                    print(f"Configuración {indice_de_config+1}:")
                    print("*********************")
                    print(
                        f"Tam_Poblacion = {tamano_poblacion_arr[indice_de_config]}\nTasa mutacion = {tasa_mutacion_arr[indice_de_config]}\nTasa cruza = {tasa_cruzamiento_arr[indice_de_config]}"
                    )
                    # Configuración para el modelo:
                    tam_poblacion = tamano_poblacion_arr[indice_de_config]
                    prob_mut = tasa_mutacion_arr[indice_de_config]
                    prob_cruz = tasa_cruzamiento_arr[indice_de_config]
                    resultados = []

                    # Ejecutar e l algoritmo evolutivo
                    inicio = time.time()
                    # Ejecutar el algoritmo genético con elitismo
                    (
                        mejor_individuo,
                        mejor_fitness,
                        mejor_generacion,
                        mejores_fitness_por_generacion,
                        mejores_20p_fit,
                    ) = meta_algoritmo_evolutivo(
                        poblacion,
                        seleccion,
                        cruce,
                        mutacion,
                        prob_cruz,
                        prob_mut,
                        tam_poblacion,
                    )
                    coleccion_mejores_resultados.append(mejores_fitness_por_generacion)
                    coleccion_array_fit.append(mejores_20p_fit)
                    fin = time.time()
                    print("Tiempo de ejecución: ", fin - inicio, "\n\n")

                    resultados.append(
                        [
                            iteracion + 1 + ite_ind,
                            indice_de_config + 1,
                            seleccion.__name__,
                            cruce.__name__,
                            mutacion.__name__,
                            mejor_fitness,
                            mejor_generacion,
                        ]
                    )
                    # Guardar los resultados de cada ejecución en el CSV
                    guardar_datos_csv(resultados)
                # Grafica de evolucion de fitness de las 1 configuraciones:
                plt.figure(figsize=(8, 9))
                for conf, evolucion_fitness in enumerate(coleccion_mejores_resultados):
                    plt.plot(evolucion_fitness, label=f"Configuración {conf + 1}")
                plt.xlabel("Generación")
                plt.ylabel("Fitness")
                plt.title(
                    f"Evolución del Fitness por Configuracion\nModelo {indice_de_mod +1}:\n{seleccion.__name__}, {cruce.__name__}, {mutacion.__name__}\nIteración: {iteracion+1+ite_ind}"
                )
                plt.legend(fontsize="x-large")
                # Guardar el gráfico
                nombre_grafico = f"graf_config/modelo{indice_de_mod +1}/META_ALG_{seleccion.__name__}_{cruce.__name__}_{mutacion.__name__}_iteracion{iteracion+1+ite_ind}.png"
                plt.savefig(nombre_grafico)
                print(f"Gráfico de evolucion de fitness guardado: {nombre_grafico}")

                # Grafica de los promedios de los fitness de cada iteracion
                promedios = [np.mean(arr) for arr in coleccion_array_fit]
                eje_x = [
                    f"Configuracion {i+1}" for i in range(len(coleccion_array_fit))
                ]
                # Graficar la dispersión
                plt.figure(figsize=(10, 12))
                plt.scatter(eje_x, promedios, color="blue", label="Promedios")
                plt.plot(eje_x, promedios, linestyle="--", color="gray", alpha=0.5)

                # Añadir etiquetas a cada punto
                for i, promedio in enumerate(promedios):
                    plt.text(
                        i,
                        promedio,
                        f"{promedio:.8f}",
                        ha="center",
                        va="bottom",
                        fontsize=8,
                        color="black",
                    )

                plt.title(
                    f"Promedios de las configuraciones\nIteracion {iteracion+1+ite_ind}\nModelo {indice_de_mod +1}: {seleccion.__name__}, {cruce.__name__}, {mutacion.__name__}"
                )
                plt.xlabel("Configuraciones")
                plt.ylabel("Promedios de fitness")
                plt.xticks(rotation=45)
                plt.grid(True, linestyle="--", alpha=0.6)
                plt.legend()
                plt.tight_layout()
                # Guardar el gráfico
                nombre_grafico2 = f"graf_config/modelo{indice_de_mod +1}/Prom_META_ALG_{seleccion.__name__}_{cruce.__name__}_{mutacion.__name__}_iteracion{iteracion+1+ite_ind}.png"
                plt.savefig(nombre_grafico2)
                print(
                    f"Gráfico de evolucion de fitness guardado: {nombre_grafico2}\n\n"
                )

            print("\n\n")

            indice_de_mod += 1
            # """
