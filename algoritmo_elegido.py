from Algoritmo_evo.algoritmo_evo import *
from Algoritmo_evo.META_alg_evo import *

poblacion = inicializar_poblacion(240, maquinas_por_etapa, num_pedidos)
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
    seleccion_por_ranking,
    cruce_1_punto,
    mutacion_intercambio_por_etapa,
    prob_cruz=0.5748538522008351,
    prob_mut=0.490015123270944,
    tamano_poblacion=240,
)
fin = time.time()
print(
    f"\nMejor fitness encontrado en la generación {mejor_generacion + 1}: {mejor_fitness:.16f}"
)
print(
    f"Mejor tiempo encontrado en la generación {mejor_generacion + 1}: {1/mejor_fitness:.16f}"
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
