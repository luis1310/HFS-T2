from Parametros.Parametros_tot import *

## Población v0.2

def inicializar_poblacion(size, num_pedidos):
    poblacion = []
    for _ in range(size):
        cromosoma = []
        for _ in range(num_pedidos):
            
            # Se añaden restricciones en cada etapa para asignar determinadas maquinas (las mismas que en la mutación v0.2)
            pedido = [
                random.randint(1, 3),  # Etapa 1: maquinas 1 a 3
                random.randint(4, 5),  # Etapa 1: maquinas 4 a 5
                random.randint(6, 8),  # Etapa 1: maquinas 6 a 8
                random.randint(9, 10),  # Etapa 1: maquinas 9 a 10
                11    # Etapa 5: maquina 11
            ]

            cromosoma.append(pedido)
        poblacion.append(cromosoma)
    return poblacion

