from Parametros.Parametros_tot import *

##Mutación1 v0.2
def mutacion(cromosoma, prob_mutacion=0.1):
    for pedido in cromosoma:
        if random.random() < prob_mutacion:
            etapa_mutar = random.randint(0, 4)  # Selecciona una etapa aleatoria para mutar
            
            # Se añade restricciones en la mutación para que en cada etapa esté asigandas determinadas maquinas
            if etapa_mutar == 0:
                pedido[etapa_mutar] = random.randint(1, 3)  # Etapa 1: maquinas 1 a 3
            elif etapa_mutar == 1:
                pedido[etapa_mutar] = random.randint(4, 5)  # Etapa 1: maquinas 4 a 5
            elif etapa_mutar == 2:
                pedido[etapa_mutar] = random.randint(6, 8)  # Etapa 1: maquinas 6 a 8
            elif etapa_mutar == 3:
                pedido[etapa_mutar] = random.randint(9, 10)  # Etapa 1: maquinas 9 a 10
            else:
                pedido[etapa_mutar] = 11    # Etapa 5: maquina 11
    return cromosoma
