from Algoritmo_evo.algoritmo_evo import *
from Algoritmo_evo.META_alg_evo import *

eleg = 0  # Algoritmo Genetico elegido
alg_geneticos = [
    [  # AG 1
        seleccion_por_ranking,
        cruce_1_punto,
        mutacion_intercambio_por_etapa,
        0.5748538522008351,  # prob cruza
        0.490015123270944,  # prob mutacion
        240,  # tamaño población
    ],
    [  # AG 2
        seleccion_por_ruleta,
        cruce_2_puntos,
        mutacion_intercambio_por_etapa,
        0.6201369561158429,  # prob cruza
        0.4263064349527299,  # prob mutacion
        70,  # tamaño población
    ],
    [  # AG 3
        seleccion_por_ranking,
        cruce_1_punto,
        mutacion_intercambio_por_etapa,
        0.8690387173349006,  # prob cruza
        0.2627083516388411,  # prob mutacion
        170,  # tamaño población
    ],
    [  # AG 4
        seleccion_por_torneo,
        cruce_2_puntos,
        mutacion_aleatoria,
        0.6641427039708248,  # prob cruza
        0.18709717720279678,  # prob mutacion
        210,  # tamaño población
    ],
    [  # AG 5
        seleccion_por_torneo,
        cruce_1_punto,
        mutacion_intercambio_por_etapa,
        0.5748538522008351,  # prob cruza
        0.490015123270944,  # prob mutacion
        240,  # tamaño población
    ],
    [  # AG 6
        seleccion_por_ranking,
        cruce_2_puntos,
        mutacion_intercambio_por_etapa,
        0.8710230131356245,  # prob cruza
        0.11782972115214507,  # prob mutacion
        70,  # tamaño población
    ],
    [  # AG 7
        seleccion_por_ruleta,
        cruce_1_punto,
        mutacion_intercambio_por_etapa,
        0.6538401618566114,  # prob cruza
        0.15067767889314274,  # prob mutacion
        180,  # tamaño población
    ],
    [  # AG 8
        seleccion_por_torneo,
        cruce_1_punto,
        mutacion_aleatoria,
        0.8070389690090312,  # prob cruza
        0.19710262526458855,  # prob mutacion
        240,  # tamaño población
    ],
    [  # AG 9
        seleccion_por_ranking,
        cruce_1_punto,
        mutacion_intercambio_por_etapa,
        0.7575243079969969,  # prob cruza
        0.34694846442880817,  # prob mutacion
        190,  # tamaño población
    ],
    [  # AG 10
        seleccion_por_ruleta,
        cruce_1_punto,
        mutacion_intercambio_por_etapa,
        0.5748538522008351,  # prob cruza
        0.490015123270944,  # prob mutacion
        240,  # tamaño población
    ],
]

poblacion = inicializar_poblacion(240, maquinas_por_etapa, num_pedidos)

print("Modelo:\n")
print("Método de selección:", alg_geneticos[eleg][0].__name__)
print("Método de cruza:", alg_geneticos[eleg][1].__name__)
print("Método de mutación:", alg_geneticos[eleg][2].__name__)
print("Probabilidad de cruza:", alg_geneticos[eleg][3])
print("Probabilidad de mutación:",alg_geneticos[eleg][4])
print("Tamaño de población:",alg_geneticos[eleg][5])
# Ejecutar el algoritmo
inicio = time.time()

(
    mejor_individuo,
    mejor_fitness,
    mejor_generacion,
    mejores_fitness_por_generacion,
    mejores_20p_fit,
) = meta_algoritmo_evolutivo(
    poblacion,
    alg_geneticos[eleg][0],
    alg_geneticos[eleg][1],
    alg_geneticos[eleg][2],
    prob_cruz=alg_geneticos[eleg][3],
    prob_mut=alg_geneticos[eleg][4],
    tamano_poblacion=alg_geneticos[eleg][5],
)
fin = time.time()
print(
    f"\nMejor fitness encontrado: {mejor_fitness:.16f}"
)
print(
    f"Mejor generación {mejor_generacion + 1}: {1/mejor_fitness:.16f}"
)
print(f"Mejor orden de pedidos: {mejor_individuo}")
print("\n########################################################\n")
print("Tiempo de ejecución: ")
print(fin - inicio)


# Cálculo de mejores tiempos por generacion
generacion = [i for i in range(num_generaciones)]
mejores_tiempos = [
    1 / fitness if fitness != 0 else 0 for fitness in mejores_fitness_por_generacion
]

# Crear subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Primer gráfico: Evolución del Fitness por Generación
ax1.plot(generacion, mejores_fitness_por_generacion, label="Fitness")
ax1.set_title("Evolución del Fitness por Generación")
ax1.set_xlabel("Generaciones")
ax1.set_ylabel("Fitness")
ax1.legend()

# Segundo gráfico: Valores de 1 / Fitnessl
ax2.plot(generacion, mejores_tiempos, label="MakeSpan", color="orange")
ax2.set_title("Evolucion del MakeSpan por Generación")
ax2.set_xlabel("Generaciones")
ax2.set_ylabel("MakeSpan")
ax2.legend()

# Mostrar los gráficos
plt.tight_layout()
plt.show()
