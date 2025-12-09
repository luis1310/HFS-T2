# Continuación Automática de Experimentos

## **Problema Resuelto**

**Antes:** Si interrumpías un experimento con `Ctrl+C`, al volver a ejecutar el script empezaba desde cero, duplicando trabajo ya realizado.

**Ahora:** El script detecta automáticamente qué configuraciones ya están completas y solo ejecuta las faltantes.

## **Cómo Funciona**

### **1. Detección Automática**
```python
# Al iniciar, el script:
Busca archivos parciales: tunning_multimetrica_parcial_*.csv
Busca archivos finales: tunning_multimetrica_real_*.csv
Identifica configuraciones completas
Calcula configuraciones faltantes
```

### **2. Continuación Inteligente**
```python
# Solo ejecuta lo que falta:
Total configuraciones: 64
Completadas: 12 (18.8%)
Faltantes: 52 (81.2%)
Solo ejecuta las 52 faltantes
```

### **3. Guardado Inteligente**
```python
# Guarda con timestamp único:
tunning_multimetrica_parcial_20250124_143022.csv
tunning_multimetrica_real_20250124_150045.csv
```

## 📋 **Scripts Modificados**

### **`tunning_multimetrica.py`**
- Detecta resultados previos automáticamente
- Solo ejecuta configuraciones faltantes
- Guarda con timestamp único
- No duplica trabajo

### **`comparacion_operadores.py`**
- Misma lógica de continuación automática
- Detecta configuraciones completas
- Solo ejecuta las faltantes

### **`prueba_rapida.py`**
- Misma lógica de continuación automática
- Detecta configuraciones completas
- Solo ejecuta las faltantes

## **Scripts de Gestión**

### **`demo_continuacion.py`**
```bash
python3 tesis3/experiments/paralelizacion/demo_continuacion.py
```
- Analiza el estado actual
- Muestra progreso
- Estima tiempo restante

### **`prueba_continuacion.py`**
```bash
python3 tesis3/experiments/paralelizacion/prueba_continuacion.py
```
- Simula la detección automática
- Muestra qué se ejecutaría
- Calcula tiempo estimado

### **`gestionar_experimentos.py`**
```bash
python3 tesis3/experiments/paralelizacion/gestionar_experimentos.py
```
- Analiza progreso
- 🔗 Combina resultados
- 🧹 Limpia archivos antiguos

## 💡 **Uso Práctico**

### **Escenario 1: Primera ejecución**
```bash
python3 tesis3/experiments/paralelizacion/tunning_multimetrica.py
# Seleccionar núcleos
# Ejecuta todas las 64 configuraciones
```

### **Escenario 2: Interrupción y continuación**
```bash
# Ejecutar experimento
python3 tesis3/experiments/paralelizacion/tunning_multimetrica.py
# ... se ejecuta por 2 horas ...
# Ctrl+C para interrumpir

# Continuar más tarde
python3 tesis3/experiments/paralelizacion/tunning_multimetrica.py
# Detecta automáticamente: 12 completas, 52 faltantes
# Solo ejecuta las 52 faltantes
```

### **Escenario 3: Verificar progreso**
```bash
# Ver estado actual
python3 tesis3/experiments/paralelizacion/demo_continuacion.py

# Gestionar experimentos
python3 tesis3/experiments/paralelizacion/gestionar_experimentos.py
```

## 🎉 **Ventajas**

### **No Duplica Trabajo**
- Detecta configuraciones ya completas
- Solo ejecuta las faltantes
- Ahorra tiempo y recursos

### **Continuación Automática**
- No requiere intervención manual
- Detecta automáticamente el progreso
- Continúa exactamente donde se quedó

### **Guardado Inteligente**
- Archivos con timestamp único
- No sobrescribe resultados previos
- Combina resultados automáticamente

### **Gestión Completa**
- Scripts para analizar progreso
- Herramientas para combinar resultados
- Limpieza automática de archivos antiguos

## **Ejemplo de Salida**

```
Detectando resultados previos...
   Archivos parciales encontrados: 1
   Archivos finales encontrados: 0
   Configuración completa detectada: Pob:100 Gen:400 PC:0.8 PM:0.10 K:5 IL:3
   ... (más configuraciones)
   Total configuraciones completas previas: 12

RESUMEN:
   Configuraciones totales: 64
   Configuraciones completas previas: 12
   Configuraciones faltantes: 52
   Progreso: 18.8%

Tiempo estimado restante: 8.7 horas
Total de ejecuciones: 1560

¿Continuar con las 52 configuraciones faltantes? (s/n): s
```

## 🔧 **Implementación Técnica**

### **Detección de Resultados Previos**
```python
def detectar_resultados_previos():
    # Buscar archivos parciales y finales
    archivos_parciales = glob.glob('tesis3/results/tunning_multimetrica_parcial_*.csv')
    archivos_finales = glob.glob('tesis3/results/tunning_multimetrica_real_*.csv')
    
    # Cargar configuraciones completas
    configuraciones_completas = set()
    for archivo in archivos_parciales + archivos_finales:
        # Leer y procesar configuraciones
        # ...
    
    return configuraciones_completas
```

### **Filtrado de Configuraciones**
```python
# Filtrar configuraciones que ya están completas
combinaciones_faltantes = []
for combo in combinaciones:
    config_key = tuple(sorted(combo.items()))
    if config_key not in configuraciones_completas_previas:
        combinaciones_faltantes.append(combo)
```

### **Guardado con Timestamp**
```python
timestamp = time.strftime('%Y%m%d_%H%M%S')
output_file = f'tesis3/results/tunning_multimetrica_parcial_{timestamp}.csv'
```

## **Resultado Final**

**¡Ahora puedes interrumpir y continuar experimentos sin perder trabajo!**

- **Ctrl+C** → Interrumpir experimento
- **Reiniciar** → Continúa automáticamente
- **No duplica** → Solo ejecuta lo faltante
- **Guarda inteligente** → Timestamp único
- **Gestión completa** → Scripts de análisis
