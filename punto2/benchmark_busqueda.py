"""
Punto 2 - Benchmark de algoritmos de búsqueda (Python) y registro de resultados.

Uso (desde la raíz del repositorio o desde cualquier carpeta):
    py punto2/benchmark_busqueda.py            -> ejecuta las mediciones en Python
    py punto2/benchmark_busqueda.py --java     -> registra los tiempos generados por BenchmarkBusqueda.java

Experimentos:
  1. 'mezclado': las 1.000 claves de claves_busqueda_punto2.txt (500 presentes y 500 ausentes
     en todos los n) sobre cada datos_{n}_asc.txt.
  2. 'inicio' / 'centro' / 'final': 1.000 búsquedas de una clave ubicada en esa posición (n = 1.000.000).

Cada repetición mide el tiempo total de las 1.000 búsquedas; lo que se registra
es el tiempo promedio POR BÚSQUEDA (total / 1.000), en nanosegundos.
"""
import os
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)  # registrar_resultados usa rutas relativas a la raíz
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "punto2"))

from registrar_resultados import GestorResultados, PUNTO2, carpeta_resultados, cargar_arreglo, cargar_claves_busqueda
import algoritmos

SIZES = [1_000, 10_000, 100_000, 1_000_000]
REPETICIONES = 5
N_POSICIONES = 1_000_000
BUSQUEDAS_POR_POSICION = 1_000
RUTA_TIEMPOS_JAVA = os.path.join(carpeta_resultados(PUNTO2), "tiempos_crudos_java_punto2_busqueda.csv")

# Todas las funciones se adaptan a la firma f(arr, x) -> bool (encontrado o no)
ALGORITMOS = {
    "Busqueda Lineal": lambda arr, x: algoritmos.linear_search(arr, x) != -1,
    "Busqueda Binaria": lambda arr, x: algoritmos.binarySearch(arr, x) != -1,
    "Busqueda Ternaria": lambda arr, x: algoritmos.ternarySearch(arr, x),
    "Busqueda por Saltos": lambda arr, x: algoritmos.jumpSearch(arr, x, len(arr)) != -1,
    "Busqueda por Interpolacion": lambda arr, x: algoritmos.interpolationSearch(arr, 0, len(arr) - 1, x) != -1,
    "Busqueda Exponencial": lambda arr, x: algoritmos.exponential_search(arr, x) != -1,
}


def medir(buscar, arr, claves):
    """Tiempo promedio por búsqueda (ns) de buscar todas las claves, una vez."""
    inicio = time.perf_counter_ns()
    for x in claves:
        buscar(arr, x)
    fin = time.perf_counter_ns()
    return (fin - inicio) / len(claves)


def verificar(nombre, buscar, arr, claves, conjunto):
    """Fuera de la medición: comprueba que el algoritmo encuentra exactamente las claves presentes."""
    for x in claves:
        if buscar(arr, x) != (x in conjunto):
            raise AssertionError(f"{nombre} devolvió un resultado incorrecto para la clave {x}")


def ejecutar_python():
    gestor = GestorResultados(PUNTO2)
    claves = cargar_claves_busqueda()

    # ---- Experimento 1: 1.000 claves mezcladas (500 presentes en n=1M / 500 ausentes) ----
    for n in SIZES:
        arr = cargar_arreglo(n, "asc")
        conjunto = set(arr)
        print(f"\nn = {n:,}  ({sum(x in conjunto for x in claves)} claves presentes)")
        for nombre, buscar in ALGORITMOS.items():
            verificar(nombre, buscar, arr, claves, conjunto)
            tiempos = [medir(buscar, arr, claves) for _ in range(REPETICIONES)]
            reg = gestor.registrar_ejecucion_medida(nombre, "Python", "mezclado", n, tiempos)
            print(f"  {nombre:<28} {reg['promedio_ns']:>14,.1f} ns/búsqueda  (σ {reg['desviacion_estandar_ns']:,.1f})")

    # ---- Experimento 2: posición de la clave (n = 1.000.000) ----
    arr = cargar_arreglo(N_POSICIONES, "asc")
    posiciones = {"inicio": arr[0], "centro": arr[len(arr) // 2], "final": arr[-1]}
    print(f"\nPosición de la clave, n = {N_POSICIONES:,}")
    for posicion, clave in posiciones.items():
        claves_pos = [clave] * BUSQUEDAS_POR_POSICION
        for nombre, buscar in ALGORITMOS.items():
            if not buscar(arr, clave):
                raise AssertionError(f"{nombre} no encontró la clave de la posición '{posicion}'")
            tiempos = [medir(buscar, arr, claves_pos) for _ in range(REPETICIONES)]
            reg = gestor.registrar_ejecucion_medida(nombre, "Python", posicion, N_POSICIONES, tiempos)
            print(f"  [{posicion:<6}] {nombre:<28} {reg['promedio_ns']:>14,.1f} ns/búsqueda")

    print(f"\n[OK] Resultados guardados en {gestor.ruta_csv} y {gestor.ruta_json}")


def importar_java():
    """Registra con GestorResultados los tiempos crudos que escribió BenchmarkBusqueda.java."""
    gestor = GestorResultados(PUNTO2)
    cantidad = gestor.importar_tiempos_crudos(RUTA_TIEMPOS_JAVA, "Java")
    print(f"[OK] {cantidad} registros de Java guardados en {gestor.ruta_csv} y {gestor.ruta_json}")


if __name__ == "__main__":
    if "--java" in sys.argv:
        importar_java()
    else:
        ejecutar_python()
