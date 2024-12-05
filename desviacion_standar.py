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




def graficar_promedios_scatter(df, metodos, columna_fitness="Promedio_Mejor_Fitness"):
    """
    Generar gráficos de puntos con etiquetas descriptivas en el eje X (e.g., "Configuración 1").
    Agrupa por "Metodo_Seleccion", "Metodo_Cruce" y "Metodo_Mutacion".

    Args:
        df (pd.DataFrame): DataFrame con las estadísticas de los modelos.
        metodos (list): Lista de combinaciones de métodos a graficar.
        columna_generacion (str): Columna con el promedio de generación (se invertirá para mostrar tiempos).
    """
    for i, metodo in enumerate(metodos):
        subset = df[
            (df["Metodo_Seleccion"] == metodo[0]) &
            (df["Metodo_Cruce"] == metodo[1]) &
            (df["Metodo_Mutacion"] == metodo[2])
        ]
        
        if subset.empty:
            print(f"No hay datos para el método {metodo}")
            continue
        
        # Calcular los valores invertidos para mostrar como tiempos
        subset["Tiempo_Promedio"] = 1 / subset[columna_fitness]
        
        # Crear el gráfico scatter
        plt.figure(figsize=(12, 8))
        plt.scatter(range(len(subset)), subset["Tiempo_Promedio"], color="blue", label="Makespan promedio por configuración")

         # Conexión de los puntos con líneas punteadas
        plt.plot(range(len(subset)), subset["Tiempo_Promedio"], linestyle="--", color="gray", alpha=0.7)
        
        
        # Etiquetas descriptivas en el eje X
        configuraciones_etiquetas = [f"Configuración {int(c)}" for c in subset["Configuracion"]]
        plt.xticks(ticks=range(len(configuraciones_etiquetas)), labels=configuraciones_etiquetas, rotation=45)
        
        # Etiquetas en cada punto
        for x, y in enumerate(subset["Tiempo_Promedio"]):
            plt.text(x, y, f"{y:.6f}", fontsize=8, ha="center", va="bottom")
        
        # Configuración del gráfico
        plt.title(f"Modelo {i+1}: {metodo[0]}, {metodo[1]}, {metodo[2]}")
        plt.xlabel("Configuraciones")
        plt.ylabel("Tiempos Invertidos")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend()
        
        # Mostrar el gráfico
        plt.tight_layout()
        plt.show()

# Cargar el DataFrame (ajustar la ruta al archivo CSV según tu caso)
df = estadisticas_p_modelos

# Lista de métodos únicos a graficar
metodos_unicos = df[["Metodo_Seleccion", "Metodo_Cruce", "Metodo_Mutacion"]].drop_duplicates().values.tolist()

# Generar los gráficos scatter
graficar_promedios_scatter(df, metodos_unicos)

