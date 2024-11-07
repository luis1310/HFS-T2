from Parametros.Parametros_tot import *

# Leer el archivo CSV con pandas
df = pd.read_csv("resultados_algoritmo_renumerado.csv")

# Definir los umbrales de color
umbral_fitness_minimo = 0.00063452 # Tiempo de 1575.99 (aprox)
umbral_fitness_bajo = 0.00063695  # Tiempo de 1569.982 (aprox)
umbral_fitness_alto = 0.00063952  # Tiempo de 1563.673 (aprox)
umbral_fitness_superior = 0.00064155 # Tiempo de 1558.725 (aprox)
# Agrupar por combinación de métodos para graficar cada modelo individualmente
modelos = df.groupby(["Metodo_Seleccion", "Metodo_Cruce", "Metodo_Mutacion"])

for (seleccion, cruce, mutacion), data_modelo in modelos:
    plt.figure(figsize=(15, 9))

    # Scatter plot con coloración basada en umbrales
    """

    colores = [
        (
            "blue"
            if x < umbral_fitness_bajo
            else "orange" if x < umbral_fitness_alto else "green"
        )
        for x in data_modelo["Mejor_Fitness"]
    ]

    """

    #"""

    colores = [
        (
            "orange" if x < umbral_fitness_minimo
            else "purple" if x < umbral_fitness_bajo
            else "blue" if x < umbral_fitness_alto
            else "green" if x < umbral_fitness_superior
            else "red"
        )
        for x in data_modelo["Mejor_Fitness"]
    ]
    
    #"""
    
    plt.scatter(
        data_modelo["Iteracion"],
        data_modelo["Mejor_Fitness"],
        c=colores,
        alpha=0.6,
        label="Fitness",
    )

    # Línea de tendencia (regresión lineal)
    x = data_modelo["Iteracion"]
    y = data_modelo["Mejor_Fitness"]
    coef = np.polyfit(x, y, 1)  # Ajuste lineal (grado 1)
    tendencia = np.poly1d(coef)  # Generar función de tendencia
    plt.plot(
        x, tendencia(x), color="crimson", linestyle="--", label="Línea de tendencia"
    )

    # Configuración del gráfico
    plt.title(f"Dispersión del Mejor Fitness - {seleccion} | {cruce} | {mutacion}")
    plt.xlabel("Iteración")
    plt.ylabel("Mejor Fitness")
    # Calcular y mostrar el conteo de puntos por cada rango de umbral
    conteo_minimo = sum(1 for fit in y if fit < umbral_fitness_minimo)  # Región azul
    conteo_bajo = sum(1 for fit in y if umbral_fitness_minimo <= fit < umbral_fitness_bajo)  # Región naranja
    conteo_medio = sum(1 for fit in y if umbral_fitness_bajo <= fit < umbral_fitness_alto)  # Región amarilla
    conteo_alto = sum(1 for fit in y if umbral_fitness_alto <= fit < umbral_fitness_superior)  # Región púrpura
    conteo_superior = sum(1 for fit in y if fit >= umbral_fitness_superior)  # Región verde

    plt.legend(
        title=f"Puntos:\nSuperior={conteo_superior},\nAlto={conteo_alto},\nMedio={conteo_medio},\nBajo={conteo_bajo},\nMínimo={conteo_minimo}"
    )
    plt.tight_layout()

    # Guardar el gráfico con línea de tendencia
    nombre_grafico = (
        f"modelos_graficos/grafico_con_tendencia_{seleccion}_{cruce}_{mutacion}.png"
    )
    plt.savefig(nombre_grafico)
    print(f"Gráfico con línea de tendencia guardado: {nombre_grafico}")
    #plt.show()
