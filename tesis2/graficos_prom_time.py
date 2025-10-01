################################

from Parametros.Parametros_tot import os, plt


def graficar_promedios(df, metodos, columna_fitness="Promedio_promedios"):
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

        # Guardar el gráfico
        nombre_grafico = f"graf_configv2/prom_modelos/graf_tiempo_mod_{i + 1}.png"

        # Extraer el directorio de la ruta
        directorio = os.path.dirname(nombre_grafico)

        # Crear las carpetas si no existen
        os.makedirs(directorio, exist_ok=True)

        plt.savefig(nombre_grafico)
        print(f"Gráfico de evolucion de fitness guardado: {nombre_grafico}")


def graficar_promedios_2(df, metodos, columna_fitness="Promedio_promedios"):
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

        # Guardar el gráfico
        nombre_grafico = f"graf_configv2/prom_modelos/graf_makespam_promedio_{i + 1}.png"

        # Extraer el directorio de la ruta
        directorio = os.path.dirname(nombre_grafico)

        # Crear las carpetas si no existen
        os.makedirs(directorio, exist_ok=True)

        plt.savefig(nombre_grafico)
        print(f"Gráfico de evolucion de fitness guardado: {nombre_grafico}")