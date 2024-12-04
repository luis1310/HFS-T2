from Parametros.Parametros_tot import *

# Configurar Pandas para que muestre 10 decimales de exactitud
pd.set_option("display.float_format", "{:.10f}".format)

# Ajustar la opción para mostrar todas las filas
pd.set_option("display.max_rows", None)  # Muestra todas las filas del DataFrame

# Cargar el archivo CSV
archivo = "resultados_META_algoritmo_renumerado.csv"


def calcular_estadisticas(archivo=archivo, output_file="estadisticas_modelos.csv"):
    df = pd.read_csv(archivo)

    # Agrupar por el conjunto único de columnas que definen un modelo
    estadisticas_modelos = (
        df.groupby(
            ["Configuracion", "Metodo_Seleccion", "Metodo_Cruce", "Metodo_Mutacion"]
        )
        .agg(
            Promedio_Mejor_Generacion=("Mejor_generacion", "mean"),
            Desviacion_Generacion=("Mejor_generacion", "std"),
            Promedio_Mejor_Fitness=("Mejor_Fitness", "mean"),
            Desviacion_Fitness=("Mejor_Fitness", "std"),
        )
        .reset_index()
    )

    # Mostrar la tabla de resultados
    print(estadisticas_modelos)

    # Guardar las estadísticas en un nuevo archivo CSV
    estadisticas_modelos.to_csv(output_file, index=False)
    return estadisticas_modelos


estadisticas_p_modelos = calcular_estadisticas()


def graficar_modelos_por_grupos(data, num_filas=2, num_columnas=2):
    """
    Genera gráficos agrupados por Método_Seleccion, Método_Cruce y Método_Mutacion,
    mostrando las configuraciones en el eje X con etiquetas de valor en las barras.

    Parámetros:
    - data: DataFrame con los datos.
    - num_filas: int, número de filas en cada figura.
    - num_columnas: int, número de columnas en cada figura.
    """
    # Crear una columna para identificar cada combinación única de métodos
    data["Metodo_Grupo"] = (
        data["Metodo_Seleccion"].astype(str)
        + " | "
        + data["Metodo_Cruce"].astype(str)
        + " | "
        + data["Metodo_Mutacion"].astype(str)
    )

    grupos = data["Metodo_Grupo"].unique()  # Obtener combinaciones únicas de métodos
    num_grupos = len(grupos)
    graficos_por_figura = num_filas * num_columnas
    num_figuras = (
        num_grupos + graficos_por_figura - 1
    ) // graficos_por_figura  # Total de figuras

    for fig_idx in range(num_figuras):
        fig, axes = plt.subplots(num_filas, num_columnas, figsize=(16, 10))
        axes = axes.flatten()  # Aplanar los ejes para acceder fácilmente

        for ax_idx in range(graficos_por_figura):
            grupo_idx = fig_idx * graficos_por_figura + ax_idx
            if grupo_idx >= num_grupos:
                axes[ax_idx].axis("off")  # Apagar ejes vacíos
                continue

            grupo = grupos[grupo_idx]
            subset = data[data["Metodo_Grupo"] == grupo]

            # Crear gráfico de barras
            barplot = sns.barplot(
                data=subset,
                x="Configuracion",
                y="Promedio_Mejor_Fitness",
                hue="Configuracion",  # Diferenciar configuraciones por color
                dodge=False,
                ax=axes[ax_idx],
            )
            # Agregar etiquetas con el valor en cada barra
            for container in barplot.containers:
                barplot.bar_label(container, fmt="%.8f", fontsize=9, padding=3)

            # Personalización del gráfico
            axes[ax_idx].set_title(f"Grupo: {grupo}", fontsize=11)
            axes[ax_idx].set_ylabel("Promedio Mejor Fitness")
            axes[ax_idx].set_xlabel("Configuración")
            axes[ax_idx].tick_params(axis="x", rotation=45)  # Rotar etiquetas en X

        # Ajustar diseño
        fig.tight_layout()
        fig.subplots_adjust(top=0.9)
        fig.suptitle(f"Gráficos {fig_idx + 1} de {num_figuras}", fontsize=14)
        plt.show()


"""
graficar_modelos_por_grupos(
    data=estadisticas_p_modelos,
    num_filas=2,  # Por ejemplo, 2 filas por figura
    num_columnas=1  # Por ejemplo, 2 columnas por figura
)

"""
