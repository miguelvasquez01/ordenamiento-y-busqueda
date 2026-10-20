"""
Punto 1 - Benchmark de algoritmos de ordenamiento (Python y Java) y registro de resultados.

Uso (desde la raíz del repositorio):
    py punto1/benchmark_ordenamiento.py            -> mide los 6 algoritmos en Python
    py punto1/benchmark_ordenamiento.py --java     -> mide los 6 algoritmos en Java
                                                      (antes: javac -d out punto1/AlgoritmosOrdenamiento.java punto1/BenchmarkOrdenamiento.java)
    Agregue --rehacer para volver a medir casos que ya estén registrados.

Para cada algoritmo, variante de entrada (random, asc, desc) y n (de menor a mayor):
  1. Predice el tiempo de UNA ejecución a partir del n anterior medido y de la complejidad
     teórica del caso (factor al multiplicar n por 10: O(n) x10, O(n log n) x~12, O(n^2) x100).
  2. Si la predicción supera 5 minutos (300 s), no ejecuta el caso: lo registra como ESTIMADO.
  3. Si el caso falla (RecursionError, StackOverflowError...), registra el error y estima
     ese tamaño y los mayores.
  Estimación: T(n) = T(n0) * f(n) / f(n0), con n0 el mayor tamaño medido del mismo caso
  y f la complejidad teórica del caso (n, n log n o n^2).

Cada caso se ejecuta en un proceso aparte, así un fallo no detiene el experimento.
Cada repetición ordena una copia nueva del arreglo (la copia no se mide), el tiempo se mide
con time.perf_counter_ns() / System.nanoTime() y el resultado se verifica fuera de la medición.
Los resultados se guardan con GestorResultados en
resultados_experimentos/punto1/resultados_punto1_ordenamiento.{csv,json} (tiempos en ns).
"""
import json
import math
import os
import subprocess
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)  # registrar_resultados usa rutas relativas a la raíz
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "punto1"))

from registrar_resultados import GestorResultados, PUNTO1, REPETICIONES, cargar_arreglo

SIZES = [1_000, 10_000, 100_000, 1_000_000]
VARIANTES = ["random", "asc", "desc"]
LIMITE_S = 300  # 5 minutos por ejecución

# clave interna -> nombre que se registra
ALGORITMOS = {
    "insertion": "Insertion Sort",
    "dualpivot_quick": "Dual-Pivot QuickSort",
    "merge": "Merge Sort",
    "heap": "Heap Sort",
    "radix": "Radix Sort",
    "bucket": "Bucket Sort",
}


def complejidad(alg, variante):
    """Complejidad teórica de cada caso: 'n', 'nlogn' o 'n2'."""
    if alg == "insertion":
        return "n" if variante == "asc" else "n2"
    if alg == "dualpivot_quick":
        return "nlogn" if variante == "random" else "n2"   # pivotes extremos en datos ordenados
    if alg in ("merge", "heap"):
        return "nlogn"
    return "n"                                            # radix (d = 8 fijo), bucket (uniforme)


def f(c, n):
    return {"n": n, "nlogn": n * math.log2(n), "n2": n * n}[c]


ETIQUETA = {"n": "O(n)", "nlogn": "O(n log n)", "n2": "O(n^2)"}


# ------------------------------------------------------------------ worker Python
def caso_python(alg, variante, n):
    """Mide un caso en Python (se ejecuta en un proceso aparte). Imprime JSON."""
    import algoritmos_ordenamiento as A
    sort = A.ALGORITMOS[alg]
    original = cargar_arreglo(n, variante)                 # carga ANTES de medir
    referencia = sorted(original)
    tiempos = []
    for _ in range(REPETICIONES):
        copia = list(original)                              # copia fuera del tiempo medido
        try:
            t0 = time.perf_counter_ns()
            sort(copia)
            t1 = time.perf_counter_ns()
        except RecursionError as e:
            print(json.dumps({"ok": False, "error": f"RecursionError: {e} "
                              f"(límite de recursión de Python = {sys.getrecursionlimit()})"}))
            return
        if copia != referencia:                             # verificación fuera del tiempo
            print(json.dumps({"ok": False, "error": "verificacion fallida"}))
            return
        tiempos.append(t1 - t0)
    print(json.dumps({"ok": True, "tiempos_ns": tiempos}))


# ------------------------------------------------------------------ orquestador
def comando(lenguaje, alg, variante, n):
    if lenguaje == "Java":
        return ["java", "-cp", "out", "punto1.BenchmarkOrdenamiento", alg, variante, str(n),
                str(REPETICIONES)]
    return [sys.executable, os.path.abspath(__file__), "--caso", alg, variante, str(n)]


def ejecutar(lenguaje, rehacer=False):
    gestor = GestorResultados(PUNTO1)
    for alg, nombre in ALGORITMOS.items():
        for var in VARIANTES:
            c = complejidad(alg, var)
            previo = None      # (n, promedio en ns) del mayor tamaño medido
            bloqueo = None     # motivo por el que ya no se ejecutan tamaños mayores
            for n in SIZES:
                existente = gestor.buscar(algoritmo=nombre, lenguaje=lenguaje,
                                          variante_entrada=var, n=n)
                if existente and not rehacer:
                    r = existente[0]
                    if r["estado"] == "medido":
                        previo = (n, r["promedio_ns"])
                    else:
                        bloqueo = r["observacion"]
                    continue

                motivo = None
                if bloqueo:
                    motivo = f"No ejecutado: un tamaño menor ya no se pudo ejecutar ({bloqueo.split('. Estimado')[0]})"
                elif previo:
                    pred_s = previo[1] * f(c, n) / f(c, previo[0]) / 1e9
                    if pred_s > LIMITE_S:
                        motivo = (f"No ejecutado: predicción de {pred_s:,.0f} s por ejecución "
                                  f"> {LIMITE_S} s (5 min)")
                if motivo is None:
                    t0 = time.time()
                    p = subprocess.run(comando(lenguaje, alg, var, n), capture_output=True,
                                       text=True, timeout=(REPETICIONES + 2) * 3 * LIMITE_S)
                    salida = [l for l in p.stdout.splitlines() if l.startswith("{")]
                    info = json.loads(salida[-1]) if salida else {"ok": False}
                    if p.returncode == 0 and info.get("ok"):
                        reg = gestor.registrar_ejecucion_medida(nombre, lenguaje, var, n,
                                                                info["tiempos_ns"])
                        previo = (n, reg["promedio_ns"])
                        print(f"[{lenguaje}] {nombre:<21} {var:<6} n={n:>9,}: "
                              f"{reg['promedio_ms']:>12.4f} ms  (total {time.time() - t0:.1f} s)",
                              flush=True)
                        continue
                    error = info.get("error") or (p.stderr.strip()[-300:] or
                                                  f"el proceso terminó con código {p.returncode}")
                    motivo = f"FALLO: {error}"
                    print(f"[{lenguaje}] {nombre:<21} {var:<6} n={n:>9,}: {motivo}", flush=True)

                # Estimación a partir del mayor tamaño medido
                n0, t0_ns = previo
                est = t0_ns * f(c, n) / f(c, n0)
                obs = (f"{motivo}. Estimado como T({n0:,}) x f({n:,})/f({n0:,}) con "
                       f"{ETIQUETA[c]}").replace(",", ".")
                gestor.registrar_ejecucion_estimada(nombre, lenguaje, var, n, est, obs)
                bloqueo = bloqueo or motivo
                if not motivo.startswith("No ejecutado: un tamaño"):
                    print(f"[{lenguaje}] {nombre:<21} {var:<6} n={n:>9,}: ESTIMADO "
                          f"{est / 1e6:,.1f} ms  <- {motivo}", flush=True)
    print(f"\n[OK] Resultados guardados en {gestor.ruta_csv} y {gestor.ruta_json}")


if __name__ == "__main__":
    if "--caso" in sys.argv:
        i = sys.argv.index("--caso")
        caso_python(sys.argv[i + 1], sys.argv[i + 2], int(sys.argv[i + 3]))
    else:
        ejecutar("Java" if "--java" in sys.argv else "Python", rehacer="--rehacer" in sys.argv)
