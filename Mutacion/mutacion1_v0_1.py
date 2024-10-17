from Parametros.Parametros_tot import *

##Mutación v0.1
def mutacion(cromosoma, prob_mutacion=0.1):
    for pedido in cromosoma:
        if random.random() < prob_mutacion:
            etapa_mutar = random.randint(0, len(pedido) - 1)
            max_maquinas = asignaciones_por_etapa[etapa_mutar]
            pedido[etapa_mutar] = random.randint(1, max_maquinas)
    return cromosoma
