from Parametros.Parametros_tot import *

## Población v0.2

def inicializar_poblacion(tamano_poblacion, maquinas_por_etapa, num_pedidos):
    poblacion = [
        [[random.choice(maquinas_por_etapa[i]) for i in range(5)] for _ in range(num_pedidos)]
        for _ in range(tamano_poblacion)
    ]
    return poblacion

