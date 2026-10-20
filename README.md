# Taller 3 – Ordenamiento y Búsqueda

Comparación experimental de algoritmos de ordenamiento y búsqueda en un lenguaje compilado (**Java**) y uno interpretado (**Python**).

## Estructura

```
├── seed.py                    # Genera los datos de prueba (semilla fija = 42)
├── registrar_resultados.py    # Utilidades compartidas: carga de datos y registro de resultados (CSV/JSON)
├── datos_prueba/              # Datos de entrada generados por seed.py
├── punto1/                    # Algoritmos de ordenamiento
│   ├── algoritmos_ordenamiento.py / AlgoritmosOrdenamiento.java   # Implementaciones (basadas en GeeksforGeeks)
│   ├── benchmark_ordenamiento.py           # Mediciones en Python y en Java (--java), regla de 5 min y estimaciones
│   ├── BenchmarkOrdenamiento.java          # Mide un caso en Java (lo invoca benchmark_ordenamiento.py --java)
│   └── exportar_graficas.py                # Genera las 6 gráficas (PNG) y las tablas de apoyo
├── punto2/                    # Algoritmos de búsqueda
│   ├── algoritmos.py / algoritmos.java     # Implementaciones (basadas en GeeksforGeeks)
│   ├── benchmark_busqueda.py               # Mediciones en Python + registro de los tiempos de Java
│   ├── BenchmarkBusqueda.java              # Mediciones en Java
│   └── exportar_graficas.py                # Genera los CSV para las gráficas/tablas en Excel
└── resultados_experimentos/
    ├── punto1/                # Resultados de ordenamiento
    │   ├── resultados_punto1_ordenamiento.csv/.json  # Registro completo (Python y Java)
    │   └── graficas_punto1/                          # 6 gráficas PNG + factores_crecimiento.csv + tabla_tiempos_ms.csv
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

# 2. Punto 1 – Ordenamiento (Python y Java) y gráficas
python punto1/benchmark_ordenamiento.py
javac -d out punto1/AlgoritmosOrdenamiento.java punto1/BenchmarkOrdenamiento.java
python punto1/benchmark_ordenamiento.py --java
python punto1/exportar_graficas.py

# 3. Punto 2 – Java
javac -d out punto2/algoritmos.java punto2/BenchmarkBusqueda.java
java -cp out punto2.BenchmarkBusqueda

# 4. Punto 2 – Python y registro de los tiempos de Java
python punto2/benchmark_busqueda.py
python punto2/benchmark_busqueda.py --java

# 5. Exportar los CSV para las gráficas (Punto 2)
python punto2/exportar_graficas.py
```

## Formato de los resultados

Cada registro incluye: algoritmo, lenguaje, tipo de experimento, variante de entrada, n, los 5 tiempos medidos, promedio, desviación estándar, estado (`medido` / `estimado`) y una observación. Los tiempos están en nanosegundos; `promedio_ms` es el mismo promedio expresado en milisegundos. En el Punto 2, los tiempos son **por búsqueda** (tiempo total de las 1.000 búsquedas dividido entre 1.000).

## Punto 1 – Ordenamiento

- Algoritmos: Insertion Sort, Dual-Pivot QuickSort (pivotes en el primer y el último elemento), Merge Sort, Heap Sort, Radix Sort (LSD, base 10) y Bucket Sort (n cubetas; el valor x va a la cubeta `(x − min) · n / (max − min + 1)` y cada cubeta se ordena con Insertion Sort).
- Variantes de entrada: `random`, `asc` y `desc` (los archivos de `datos_prueba/`).
- Cada repetición ordena una copia nueva del arreglo (la copia no se mide) y el resultado se verifica fuera de la medición.
- Java: calentamiento JIT antes de medir (20 ejecuciones sobre un subarreglo de hasta 10.000 elementos y 1 ejecución completa), que no entra en el promedio. Se usa el tamaño de pila por defecto de la JVM (sin `-Xss`).
- Cada caso corre en un proceso aparte. Si la predicción de una ejecución supera 5 minutos, o el caso falla (`RecursionError` en Python, `StackOverflowError` en Java para Dual-Pivot QuickSort con datos ordenados), se registra como `estimado` con T(n) = T(n0) · f(n) / f(n0), donde n0 es el mayor tamaño medido y f la complejidad teórica del caso. La columna `observacion` explica cada estimación.
- Si se vuelve a ejecutar, `benchmark_ordenamiento.py` salta los casos ya registrados; use `--rehacer` para medir todo de nuevo.

## Referencias

Las implementaciones de los algoritmos están basadas en [GeeksforGeeks](https://www.geeksforgeeks.org/).
