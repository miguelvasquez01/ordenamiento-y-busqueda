"""
Punto 2 - Exporta los CSV listos para importar en Excel y generar las gráficas/tablas del enunciado.

Uso:  py punto2/exportar_graficas.py
Lee:  resultados_experimentos/resultados_punto2_busqueda.json
Escribe en resultados_experimentos/graficas_punto2/:
  1_crecimiento_python.csv          -> gráfica de líneas (filas = n, una columna por algoritmo)
  2_crecimiento_java.csv            -> gráfica de líneas (filas = n, una columna por algoritmo)
  3_compilado_vs_interpretado.csv   -> gráfico de barras n = 1.000.000 (filas = algoritmo, columnas Java/Python)
  4_posicion_clave_python.csv       -> tabla n = 1.000.000 (filas = algoritmo, columnas inicio/centro/final)
  5_posicion_clave_java.csv         -> tabla n = 1.000.000 (filas = algoritmo, columnas inicio/centro/final)

Todos los tiempos son el promedio por búsqueda en nanosegundos (ns).
Formato: separador ',' y decimal '.', UTF-8 con BOM (Excel muestra bien las tildes).
"""
import csv
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)
sys.path.insert(0, RAIZ)

from registrar_resultados import RESULTS_DIR, PUNTO2, cargar_resultados

SALIDA = os.path.join(RESULTS_DIR, "graficas_punto2")
SIZES = [1_000, 10_000, 100_000, 1_000_000]
N_COMPARACION = 1_000_000
LENGUAJES = ["Python", "Java"]
POSICIONES = ["inicio", "centro", "final"]
ALGORITMOS = [
    "Busqueda Lineal", "Busqueda Binaria", "Busqueda Ternaria",
    "Busqueda por Saltos", "Busqueda por Interpolacion", "Busqueda Exponencial",
]


def indexar(registros):
    """(algoritmo, lenguaje, variante, n) -> registro"""
    return {(r["algoritmo"], r["lenguaje"], r["variante_entrada"], r["n"]): r for r in registros}


def valor(indice, algoritmo, lenguaje, variante, n):
    """Promedio en ns; si el registro es estimado lo anota en 'estimados' para avisar al final."""
    r = indice.get((algoritmo, lenguaje, variante, n))
    if r is None:
        print(f"  [AVISO] Falta {algoritmo} / {lenguaje} / {variante} / n={n}")
        return ""
    if r["estado"] == "estimado":
        estimados.append(f"{algoritmo} / {lenguaje} / {variante} / n={n}")
    return r["promedio_ns"]


def escribir(nombre, encabezado, filas):
    ruta = os.path.join(SALIDA, nombre)
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(encabezado)
        writer.writerows(filas)
    print(f"  -> {ruta}")


estimados = []

if __name__ == "__main__":
    os.makedirs(SALIDA, exist_ok=True)
    indice = indexar(cargar_resultados(PUNTO2))
    print(f"Exportando CSV para Excel en {SALIDA}/")

    # 1 y 2. Crecimiento: n contra tiempo promedio por búsqueda, una columna por algoritmo
    for i, lenguaje in enumerate(LENGUAJES, start=1):
        escribir(f"{i}_crecimiento_{lenguaje.lower()}.csv",
                 ["n"] + [f"{a} (ns)" for a in ALGORITMOS],
                 [[n] + [valor(indice, a, lenguaje, "mezclado", n) for a in ALGORITMOS] for n in SIZES])

    # 3. Compilado frente a interpretado, n = 1.000.000
    escribir("3_compilado_vs_interpretado.csv",
             ["Algoritmo", "Java (ns)", "Python (ns)", "Python / Java (veces)"],
             [[a, j, p, round(p / j, 1) if j and p else ""]
              for a in ALGORITMOS
              for j, p in [(valor(indice, a, "Java", "mezclado", N_COMPARACION),
                            valor(indice, a, "Python", "mezclado", N_COMPARACION))]])

    # 4 y 5. Posición de la clave, n = 1.000.000
    for i, lenguaje in enumerate(LENGUAJES, start=4):
        escribir(f"{i}_posicion_clave_{lenguaje.lower()}.csv",
                 ["Algoritmo"] + [f"{p.capitalize()} (ns)" for p in POSICIONES],
                 [[a] + [valor(indice, a, lenguaje, p, N_COMPARACION) for p in POSICIONES] for a in ALGORITMOS])

    if estimados:
        print("\n[AVISO] Estos valores son ESTIMADOS; dibújelos distinto (línea punteada / barra rayada):")
        for e in estimados:
            print(f"  - {e}")
    else:
        print("\nTodos los valores exportados son medidos (ninguno estimado).")
