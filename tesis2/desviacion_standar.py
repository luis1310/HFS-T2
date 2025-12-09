from Parametros.Parametros_tot import *
from graficos_prom_time import *

# Configurar Pandas para que muestre 10 decimales de exactitud
pd.set_option("display.float_format", "{:.10f}".format)

# Ajustar la opción para mostrar todas las filas
pd.set_option("display.max_rows", None)  # Muestra todas las filas del DataFrame

# Cargar el archivo CSV
archivo = "v2_resultados_META_algoritmo.csv"


def calcular_estadisticas(archivo=archivo, output_file="v2_estadisticas_modelos.csv"):
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
            Promedio_promedios=("Promedios_20p", "mean"),
            Desviacion_promedio_20p=("Promedios_20p", "std"),
            
        )
        .reset_index()
    )

    # Mostrar la tabla de resultados
    print(estadisticas_modelos)

    # Guardar las estadísticas en un nuevo archivo CSV
    estadisticas_modelos.to_csv(output_file, index=False)
    return estadisticas_modelos

################################

def calcular_estadisticas_makespam(archivo=archivo, output_file="v2_estadisticas_makespam.csv"):
    # Leer el archivo CSV
    df = pd.read_csv(archivo)

    # Agregar una columna con las inversas de Mejor_Fitness
    df['Tiempos_makespam'] = 1 / df['Mejor_Fitness']

    # Agregar una columna con las inversas de Promedios_20p
    df['Tiempos_Promedios_20p'] = 1 / df['Promedios_20p']

    # Agrupar por el conjunto único de columnas que definen un modelo
    estadisticas_modelos = (
        df.groupby(
            ["Configuracion", "Metodo_Seleccion", "Metodo_Cruce", "Metodo_Mutacion"]
        )
        .agg(
            Promedio_Mejor_Generacion=("Mejor_generacion", "mean"),
            Desviacion_Generacion=("Mejor_generacion", "std"),
            Promedio_makespam=("Tiempos_makespam", "mean"),
            Desviacion_makespam=("Tiempos_makespam", "std"),
            Promedio_promedios_tiempos=("Tiempos_Promedios_20p", "mean"),
            Desviacion_promedios_tiempos=("Tiempos_Promedios_20p", "std"),
        )
        .reset_index()
    )
    # Seleccionar las 10 filas con la menor desviación estándar de las inversas
    top_10_menor_desviacion = estadisticas_modelos.nsmallest(10, "Desviacion_promedios_tiempos")

    # Mostrar la tabla de resultados
    print("Estadísticas completas:")
    print(estadisticas_modelos)
    print("\nTop 10 modelos con menor desviación estandar:")
    print(top_10_menor_desviacion)

    # Guardar las estadísticas completas en un nuevo archivo CSV
    estadisticas_modelos.to_csv(output_file, index=False)

    # Guardar el top 10 en otro archivo CSV
    top_10_output_file = output_file.replace(".csv", "_top10.csv")
    top_10_menor_desviacion.to_csv(top_10_output_file, index=False)

    return estadisticas_modelos, top_10_menor_desviacion


################################

estadisticas_makespam, top_10 = calcular_estadisticas_makespam()

################################

#estadisticas_promedio_tiempos = calcular_estadisticas()

################################
"""
# Cargar el data frame
df = estadisticas_promedio_tiempos

# Lista de métodos únicos a graficar
metodos_unicos = df[["Metodo_Seleccion", "Metodo_Cruce", "Metodo_Mutacion"]].drop_duplicates().values.tolist()

# Generar los gráficos
graficar_promedios(df, metodos_unicos, columna_fitness="Promedio_promedios")
"""
"""
# Cargar el data frame
df = estadisticas_makespam

# Lista de métodos únicos a graficar
metodos_unicos = df[["Metodo_Seleccion", "Metodo_Cruce", "Metodo_Mutacion"]].drop_duplicates().values.tolist()

# Generar los gráficos
graficar_promedios_2(df, metodos_unicos, columna_fitness="Promedio_Mejor_Fitness")


"""