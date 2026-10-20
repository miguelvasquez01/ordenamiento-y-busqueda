"""
Punto 1 - Genera las 6 gráficas del enunciado y las tablas de apoyo.

Uso:  py punto1/exportar_graficas.py
Lee:  resultados_experimentos/punto1/resultados_punto1_ordenamiento.json
Escribe en resultados_experimentos/punto1/graficas_punto1/:
  1_crecimiento_java.png                  líneas n vs tiempo (log-log), entrada aleatoria
  2_crecimiento_python.png                líneas n vs tiempo (log-log), entrada aleatoria
  3/4/5_orden_entrada_java_n{n}.png       barras random/asc/desc, n = 1.000, 10.000, 100.000
  6_java_vs_python_n1000000.png           barras Java vs Python, n = 1.000.000, aleatoria
  factores_crecimiento.csv                T(10n)/T(n) observado vs teórico (entrada aleatoria)
  tabla_tiempos_ms.csv                    promedio ± desviación (ms) de todos los casos

Los valores estimados se dibujan distinto (línea punteada / barra rayada) y se marcan "(est.)".
"""
import csv
import math
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RAIZ)
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "punto1"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from registrar_resultados import PUNTO1, carpeta_resultados, cargar_resultados
from benchmark_ordenamiento import ALGORITMOS as _ALG, SIZES as TAMANOS, VARIANTES, complejidad, f

GRA = os.path.join(carpeta_resultados(PUNTO1), "graficas_punto1")
RES = GRA
ALGORITMOS = list(_ALG)
NOMBRES = dict(_ALG)
COLORES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6"]
MARCADORES = ["o", "s", "^", "D", "v", "P"]
TINTA, TINTA2, REJILLA = "#1f1f1f", "#5c5c5c", "#e4e4e4"
NOMBRE_VARIANTE = {"random": "Aleatoria", "asc": "Ascendente", "desc": "Descendente"}


def fmt_t(ms):
    """Formatea un tiempo en ms con la unidad más legible."""
    if ms < 1:
        return f"{ms*1000:.3g} µs"
    if ms < 1000:
        return f"{ms:.3g} ms"
    s = ms / 1000
    if s < 120:
        return f"{s:.3g} s"
    if s < 7200:
        return f"{s/60:.3g} min"
    return f"{s/3600:.3g} h"


def construir_registros():
    regs = []
    for r in cargar_resultados(PUNTO1):
        clave = next(k for k, v in NOMBRES.items() if v == r["algoritmo"])
        rep = [r[f"repeticion_{i}_ns"] for i in range(1, 6)]
        regs.append({"clave_alg": clave, "lenguaje": r["lenguaje"], "variante": r["variante_entrada"],
                     "n": r["n"], "promedio_ms": r["promedio_ns"] / 1e6,
                     "desviacion_ms": r["desviacion_estandar_ns"] / 1e6, "estado": r["estado"],
                     "tiempos_ms": [t / 1e6 for t in rep if t >= 0]})
    return regs


def exportar(regs):
    with open(os.path.join(RES, "tabla_tiempos_ms.csv"), "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["lenguaje", "variante", "algoritmo"] + [f"n={n}" for n in TAMANOS])
        for lang in ("Java", "Python"):
            for var in VARIANTES:
                for a in ALGORITMOS:
                    fila = []
                    for n in TAMANOS:
                        r = buscar(regs, a, lang, var, n)
                        if r is None:
                            fila.append("")
                        elif r["estado"] == "estimado":
                            fila.append(f"{r['promedio_ms']:.4f} (Estimado)")
                        else:
                            fila.append(f"{r['promedio_ms']:.4f} ± {r['desviacion_ms']:.4f}")
                    w.writerow([lang, var, NOMBRES[a]] + fila)


def buscar(regs, alg, lang, var, n):
    for r in regs:
        if (r["clave_alg"], r["lenguaje"], r["variante"], r["n"]) == (alg, lang, var, n):
            return r


def estilo(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#9a9a9a")
    ax.tick_params(colors=TINTA2, labelsize=9)
    ax.grid(True, which="major", color=REJILLA, linewidth=0.8)
    ax.set_axisbelow(True)


def grafica_crecimiento(regs, lang, nombre):
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=150)
    etiquetas = []
    for i, alg in enumerate(ALGORITMOS):
        pts = [buscar(regs, alg, lang, "random", n) for n in TAMANOS]
        xs = [p["n"] for p in pts]
        ys = [p["promedio_ms"] for p in pts]
        est = [p["estado"] == "estimado" for p in pts]
        col = COLORES[i]
        # Segmentos: sólidos entre medidos, punteados si llegan a un estimado
        for k in range(len(xs) - 1):
            ax.plot(xs[k:k+2], ys[k:k+2], color=col, linewidth=2,
                    linestyle="--" if est[k+1] else "-")
        for x, y, e in zip(xs, ys, est):
            ax.plot(x, y, marker=MARCADORES[i], markersize=8, color=col,
                    markerfacecolor="white" if e else col, markeredgewidth=2)
        etiquetas.append([math.log10(ys[-1]), ys[-1],
                          f"{NOMBRES[alg]}  {fmt_t(ys[-1])}{' (est.)' if est[-1] else ''}"])
    # Separa verticalmente las etiquetas finales para que no se encimen
    etiquetas.sort()
    sep = 0.17
    for k in range(1, len(etiquetas)):
        etiquetas[k][0] = max(etiquetas[k][0], etiquetas[k-1][0] + sep)
    for ly, y, txt in etiquetas:
        ax.annotate(txt, (TAMANOS[-1], y), xytext=(1.25 * TAMANOS[-1], 10 ** ly),
                    textcoords="data", va="center", fontsize=8.5, color=TINTA,
                    arrowprops=dict(arrowstyle="-", color="#b0b0b0", linewidth=0.6))
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(TAMANOS, ["1.000", "10.000", "100.000", "1.000.000"])
    ax.set_xlim(700, 1.6e7)
    ax.set_xlabel("Tamaño del arreglo n (escala log)", color=TINTA2)
    ax.set_ylabel("Tiempo promedio de 5 repeticiones [ms] (escala log)", color=TINTA2)
    ax.set_title(f"Crecimiento del tiempo con n — {lang}, entrada aleatoria",
                 color=TINTA, fontsize=13, loc="left", pad=12)
    estilo(ax)
    ax.grid(True, which="minor", color="#f2f2f2", linewidth=0.5)
    leyenda = [Line2D([], [], color=COLORES[i], marker=MARCADORES[i], linewidth=2,
                      label=NOMBRES[a]) for i, a in enumerate(ALGORITMOS)]
    leyenda += [Line2D([], [], color=TINTA2, marker="o", linewidth=2, label="Medido"),
                Line2D([], [], color=TINTA2, marker="o", markerfacecolor="white",
                       linestyle="--", linewidth=2, label="Estimado (no ejecutado / falló)")]
    ax.legend(handles=leyenda, fontsize=8.5, frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(GRA, nombre))
    plt.close(fig)


def barras(ax, grupos, series, valores, estimados, colores, nombres_series):
    """Barras agrupadas en escala log con el valor encima de cada barra."""
    k = len(series)
    ancho = 0.8 / k
    for j in range(k):
        for g in range(len(grupos)):
            x = g + (j - (k - 1) / 2) * ancho
            v, e = valores[j][g], estimados[j][g]
            ax.bar(x, v, width=ancho * 0.92, color="white" if e else colores[j],
                   edgecolor=colores[j], linewidth=1.5 if e else 0,
                   hatch="////" if e else None)
            ax.text(x, v * 1.15, fmt_t(v) + ("\n(est.)" if e else ""), ha="center",
                    va="bottom", fontsize=7, color=TINTA, rotation=90)
    ax.set_yscale("log")
    ax.set_xticks(range(len(grupos)), grupos, fontsize=9)
    estilo(ax)
    ax.grid(False, axis="x")
    lo = min(min(v) for v in valores)
    hi = max(max(v) for v in valores)
    ax.set_ylim(lo / 3, hi * 60)
    leyenda = [Patch(color=colores[j], label=nombres_series[j]) for j in range(k)]
    if any(any(e) for e in estimados):
        leyenda.append(Patch(facecolor="white", edgecolor=TINTA2, hatch="////",
                             label="Estimado"))
    ax.legend(handles=leyenda, fontsize=9, frameon=False, loc="upper right", ncol=len(leyenda))


def grafica_orden(regs, n, nombre):
    fig, ax = plt.subplots(figsize=(11, 6), dpi=150)
    vals, ests = [], []
    for var in VARIANTES:
        ps = [buscar(regs, a, "Java", var, n) for a in ALGORITMOS]
        vals.append([p["promedio_ms"] for p in ps])
        ests.append([p["estado"] == "estimado" for p in ps])
    barras(ax, [NOMBRES[a] for a in ALGORITMOS], VARIANTES, vals, ests, COLORES[:3],
           ["Aleatoria", "Ascendente", "Descendente"])
    ax.set_ylabel("Tiempo promedio [ms] (escala log)", color=TINTA2)
    ax.set_title("Efecto del orden de la entrada — Java, n = " + f"{n:,}".replace(",", "."),
                 color=TINTA, fontsize=13, loc="left", pad=12)
    fig.tight_layout()
    fig.savefig(os.path.join(GRA, nombre))
    plt.close(fig)


def grafica_lenguajes(regs, nombre):
    fig, ax = plt.subplots(figsize=(11, 6), dpi=150)
    vals, ests = [], []
    for lang in ("Java", "Python"):
        ps = [buscar(regs, a, lang, "random", 1_000_000) for a in ALGORITMOS]
        vals.append([p["promedio_ms"] for p in ps])
        ests.append([p["estado"] == "estimado" for p in ps])
    barras(ax, [NOMBRES[a] for a in ALGORITMOS], ["Java", "Python"], vals, ests,
           COLORES[:2], ["Java (compilado + JIT)", "Python (interpretado)"])
    ax.set_ylabel("Tiempo promedio [ms] (escala log)", color=TINTA2)
    ax.set_title("Compilado vs. interpretado — n = 1.000.000, entrada aleatoria",
                 color=TINTA, fontsize=13, loc="left", pad=12)
    fig.tight_layout()
    fig.savefig(os.path.join(GRA, nombre))
    plt.close(fig)


def tabla_crecimiento(regs):
    """Factor t(10n)/t(n) medido vs teórico, entrada aleatoria."""
    filas = []
    for lang in ("Java", "Python"):
        for alg in ALGORITMOS:
            c = complejidad(alg, "random")
            for n in TAMANOS[1:]:
                a = buscar(regs, alg, lang, "random", n // 10)
                b = buscar(regs, alg, lang, "random", n)
                filas.append({"lenguaje": lang, "algoritmo": NOMBRES[alg],
                              "de": n // 10, "a": n,
                              "factor_observado": b["promedio_ms"] / a["promedio_ms"],
                              "factor_teorico": f(c, n) / f(c, n // 10),
                              "estimado": b["estado"] == "estimado"})
    with open(os.path.join(RES, "factores_crecimiento.csv"), "w", newline="",
              encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    return filas


def main():
    os.makedirs(GRA, exist_ok=True)
    regs = construir_registros()
    exportar(regs)
    grafica_crecimiento(regs, "Java", "1_crecimiento_java.png")
    grafica_crecimiento(regs, "Python", "2_crecimiento_python.png")
    for i, n in enumerate((1_000, 10_000, 100_000), start=3):
        grafica_orden(regs, n, f"{i}_orden_entrada_java_n{n}.png")
    grafica_lenguajes(regs, "6_java_vs_python_n1000000.png")
    for fl in tabla_crecimiento(regs):
        print(f"{fl['lenguaje']:6} {fl['algoritmo']:22} {fl['de']:>7}->{fl['a']:<8} "
              f"obs {fl['factor_observado']:7.2f}  teo {fl['factor_teorico']:7.2f}"
              f"{'  (est)' if fl['estimado'] else ''}")


if __name__ == "__main__":
    main()
