# Taller 3 – Ordenamiento y Búsqueda

Comparación experimental de algoritmos de ordenamiento y búsqueda en un lenguaje compilado (**Java**) y uno interpretado (**Python**).

## Estructura

```
├── seed.py                    # Genera los datos de prueba (semilla fija = 42)
├── registrar_resultados.py    # Utilidades compartidas: carga de datos y registro de resultados (CSV/JSON)
├── datos_prueba/              # Datos de entrada generados por seed.py
├── punto2/                    # Algoritmos de búsqueda
│   ├── algoritmos.py / algoritmos.java     # Implementaciones (basadas en GeeksforGeeks)
│   ├── benchmark_busqueda.py               # Mediciones en Python + registro de los tiempos de Java
│   ├── BenchmarkBusqueda.java              # Mediciones en Java
│   └── exportar_graficas.py                # Genera los CSV para las gráficas/tablas en Excel
└── resultados_experimentos/
    ├── punto1/                # Resultados de ordenamiento
    └── punto2/                # Resultados de búsqueda
        ├── resultados_punto2_busqueda.csv/.json      # Registro completo (Python y Java)
        ├── tiempos_crudos_java_punto2_busqueda.csv   # Salida directa del benchmark de Java
        └── graficas_punto2/                          # CSV listos para Excel + graficos.xlsx
```

## Datos de prueba

- `datos_{n}_{random|asc|desc}.txt`: enteros de 8 dígitos para n = 1.000, 10.000, 100.000 y 1.000.000. Los arreglos están anidados: cada tamaño corresponde a los primeros n elementos de un mismo arreglo aleatorio.
- `claves_busqueda_punto2.txt`: 1.000 claves de búsqueda (500 presentes y 500 ausentes), válidas para todos los tamaños.

## Ejecución

Todos los comandos se ejecutan desde la raíz del repositorio.

```bash
# 1. Generar los datos (solo una vez; --force para regenerar)
python seed.py

# 2. Punto 2 – Java
javac -d out punto2/algoritmos.java punto2/BenchmarkBusqueda.java
java -cp out punto2.BenchmarkBusqueda

# 3. Punto 2 – Python y registro de los tiempos de Java
python punto2/benchmark_busqueda.py
python punto2/benchmark_busqueda.py --java

# 4. Exportar los CSV para las gráficas
python punto2/exportar_graficas.py
```

## Formato de los resultados

Cada registro incluye: algoritmo, lenguaje, tipo de experimento, variante de entrada, n, los 5 tiempos medidos, promedio, desviación estándar, estado (`medido` / `estimado`) y una observación. Los tiempos están en nanosegundos; `promedio_ms` es el mismo promedio expresado en milisegundos. En el Punto 2, los tiempos son **por búsqueda** (tiempo total de las 1.000 búsquedas dividido entre 1.000).

## Referencias

Las implementaciones de los algoritmos están basadas en [GeeksforGeeks](https://www.geeksforgeeks.org/).
