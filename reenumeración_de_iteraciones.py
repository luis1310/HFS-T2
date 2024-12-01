from Parametros.Parametros_tot import *


def renumerar_iteraciones(archivo_entrada, archivo_salida):
    # Cargar el archivo CSV en un DataFrame
    df = pd.read_csv(archivo_entrada)

    # Agrupar por modelo (selección, cruce, mutación) y renumerar las iteraciones
    df["Iteracion"] = (
        df.groupby(
            ["Configuracion", "Metodo_Seleccion", "Metodo_Cruce", "Metodo_Mutacion"]
        ).cumcount()
        + 1
    )

    # Guardar el nuevo DataFrame en un archivo CSV de salida
    df.to_csv(archivo_salida, index=False)
    print(f"Archivo renumerado guardado en {archivo_salida}")


"""
# Ejecución:
archivo_entrada = "resultados_META_algoritmo.csv"
archivo_salida = "resultados_META_algoritmo_renumerado.csv"
renumerar_iteraciones(archivo_entrada, archivo_salida)

"""
