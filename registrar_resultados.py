"""
Utilidades compartidas por todos los puntos del taller:
  - Lectura de los datos de prueba (arreglos y claves de búsqueda).
  - Registro de resultados (medidos o estimados) en CSV y JSON, un par de archivos por punto:
        resultados_experimentos/punto1/resultados_punto1_ordenamiento.{csv,json}
        resultados_experimentos/punto2/resultados_punto2_busqueda.{csv,json}
  - Importación de los tiempos crudos producidos por el lenguaje compilado (Java).
  - Consulta de resultados ya registrados (útil para gráficas y para el Punto 3).

Uso típico:
    gestor = GestorResultados(PUNTO2)
    gestor.registrar_ejecucion_medida("Busqueda Binaria", "Python", "mezclado", 1000, tiempos_ns)
"""
import os
import json
import csv
import math
import time
from typing import List, Dict, Any

# ==============================================================================
# CONFIGURACIÓN GENERAL
# ==============================================================================
DATA_DIR = "datos_prueba"
RESULTS_DIR = "resultados_experimentos"
ARCHIVO_CLAVES = "claves_busqueda_punto2.txt"
REPETICIONES = 5

# Identificadores de cada experimento: definen el tipo_experimento y el nombre de los archivos
PUNTO1 = "punto1_ordenamiento"
PUNTO2 = "punto2_busqueda"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

def carpeta_resultados(experimento: str) -> str:
    """Carpeta de resultados de un punto, p. ej. 'punto2_busqueda' -> resultados_experimentos/punto2"""
    return os.path.join(RESULTS_DIR, experimento.split("_")[0])

# ==============================================================================
# 1. FUNCIONES AUXILIARES DE LECTURA DE DATOS DE ENTRADA
# ==============================================================================

def _leer_enteros(ruta: str) -> List[int]:
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"El archivo {ruta} no existe. Ejecute seed.py primero.")
    with open(ruta, "r", encoding="utf-8") as f:
        return [int(line) for line in f if line.strip()]

def cargar_arreglo(n: int, variante: str = "random") -> List[int]:
    """
    Carga un arreglo de enteros generado previamente por seed.py.

    :param n: Tamaño del arreglo (1000, 10000, 100000, 1000000)
    :param variante: 'random', 'asc', o 'desc'
    """
    return _leer_enteros(os.path.join(DATA_DIR, f"datos_{n}_{variante}.txt"))

def cargar_claves_busqueda() -> List[int]:
    """Carga las 1.000 claves de búsqueda del Punto 2 (500 presentes y 500 ausentes en todos los n)."""
    return _leer_enteros(os.path.join(DATA_DIR, ARCHIVO_CLAVES))

# ==============================================================================
# 2. CLASE Y FUNCIONES PARA REGISTRO Y EXPORTACIÓN DE RESULTADOS
# ==============================================================================

class GestorResultados:
    """
    Registra los tiempos de las repeticiones de un experimento (un punto del taller),
    calcula estadísticas y exporta a CSV y JSON.

    Cada registro se identifica por (algoritmo, lenguaje, variante_entrada, n): si se vuelve
    a registrar la misma combinación, reemplaza a la anterior, de modo que volver a ejecutar
    un benchmark no duplica filas. CSV y JSON se reescriben siempre con el mismo contenido.
    """

    FIELDNAMES = [
        "algoritmo",
        "lenguaje",
        "tipo_experimento", # PUNTO1 / PUNTO2
        "variante_entrada", # 'random', 'asc', 'desc' (P1) | 'mezclado', 'inicio', 'centro', 'final' (P2)
        "n",
        "repeticion_1_ns",
        "repeticion_2_ns",
        "repeticion_3_ns",
        "repeticion_4_ns",
        "repeticion_5_ns",
        "promedio_ns",
        "promedio_ms",
        "desviacion_estandar_ns",
        "estado",           # 'medido' o 'estimado'
        "observacion"       # p. ej. método de estimación o error ocurrido (StackOverflow, RecursionError...)
    ]

    CLAVE = ("algoritmo", "lenguaje", "variante_entrada", "n")

    def __init__(self, experimento: str, directorio: str = None):
        self.experimento = experimento
        # Por defecto cada punto usa su carpeta: resultados_experimentos/punto1, .../punto2
        directorio = directorio or carpeta_resultados(experimento)
        os.makedirs(directorio, exist_ok=True)
        self.ruta_csv = os.path.join(directorio, f"resultados_{experimento}.csv")
        self.ruta_json = os.path.join(directorio, f"resultados_{experimento}.json")
        self.registros: List[Dict[str, Any]] = []
        # Conservar los registros de ejecuciones anteriores (p. ej. Python y luego Java)
        if os.path.exists(self.ruta_json):
            with open(self.ruta_json, "r", encoding="utf-8") as f:
                self.registros = json.load(f)

    @staticmethod
    def calcular_estadisticas(tiempos: List[float]) -> tuple[float, float]:
        """Calcula el promedio y la desviación estándar muestral."""
        if not tiempos:
            return 0.0, 0.0
        n = len(tiempos)
        promedio = sum(tiempos) / n
        if n == 1:
            return promedio, 0.0
        varianza = sum((x - promedio) ** 2 for x in tiempos) / (n - 1)
        desviacion = math.sqrt(varianza)
        return promedio, desviacion

    def registrar_ejecucion_medida(self, algoritmo: str, lenguaje: str, variante_entrada: str,
                                   n: int, tiempos_ns: List[float], observacion: str = "") -> Dict[str, Any]:
        """Registra una medición real compuesta por 5 repeticiones (en nanosegundos)."""
        prom_ns, dev_ns = self.calcular_estadisticas(tiempos_ns)

        # Garantizar exactamente 5 repeticiones en el registro
        repeticiones = list(tiempos_ns) + [0.0] * (REPETICIONES - len(tiempos_ns))

        registro = self._crear_registro(algoritmo, lenguaje, variante_entrada, n, repeticiones,
                                        prom_ns, dev_ns, "medido", observacion)
        self._guardar_registro(registro)
        return registro

    def registrar_ejecucion_estimada(self, algoritmo: str, lenguaje: str, variante_entrada: str,
                                     n: int, promedio_estimado_ns: float, observacion: str = "") -> Dict[str, Any]:
        """
        Registra un tiempo estimado para ejecuciones que superan los 5 minutos o fallaron.
        Use 'observacion' para indicar cómo se estimó o qué error ocurrió.
        """
        registro = self._crear_registro(algoritmo, lenguaje, variante_entrada, n, [-1.0] * REPETICIONES,
                                        promedio_estimado_ns, 0.0, "estimado", observacion)
        self._guardar_registro(registro)
        return registro

    def importar_tiempos_crudos(self, ruta: str, lenguaje: str) -> int:
        """
        Registra los tiempos escritos por otro lenguaje (p. ej. Java) en un CSV con columnas:
            algoritmo,variante,n,t1_ns,t2_ns,t3_ns,t4_ns,t5_ns[,observacion]
        Si las columnas t*_ns vienen vacías o en -1, se registra como estimado usando 'estimado_ns'.
        Devuelve la cantidad de registros importados.
        """
        if not os.path.exists(ruta):
            raise FileNotFoundError(f"No existe {ruta}. Ejecute primero el benchmark de {lenguaje}.")
        cantidad = 0
        with open(ruta, newline="", encoding="utf-8") as f:
            for fila in csv.DictReader(f):
                observacion = fila.get("observacion", "") or ""
                valores = [fila.get(f"t{i}_ns", "") for i in range(1, REPETICIONES + 1)]
                if all(v not in ("", None) and float(v) >= 0 for v in valores):
                    self.registrar_ejecucion_medida(fila["algoritmo"], lenguaje, fila["variante"],
                                                    int(fila["n"]), [float(v) for v in valores], observacion)
                else:
                    self.registrar_ejecucion_estimada(fila["algoritmo"], lenguaje, fila["variante"],
                                                      int(fila["n"]), float(fila["estimado_ns"]), observacion)
                cantidad += 1
        return cantidad

    def buscar(self, **filtros) -> List[Dict[str, Any]]:
        """Devuelve los registros que coinciden con los filtros, p. ej. buscar(lenguaje='Java', n=1000000)."""
        return [r for r in self.registros if all(r.get(k) == v for k, v in filtros.items())]

    def _crear_registro(self, algoritmo, lenguaje, variante_entrada, n, repeticiones,
                        prom_ns, dev_ns, estado, observacion) -> Dict[str, Any]:
        return {
            "algoritmo": algoritmo,
            "lenguaje": lenguaje,
            "tipo_experimento": self.experimento,
            "variante_entrada": variante_entrada,
            "n": n,
            "repeticion_1_ns": repeticiones[0],
            "repeticion_2_ns": repeticiones[1],
            "repeticion_3_ns": repeticiones[2],
            "repeticion_4_ns": repeticiones[3],
            "repeticion_5_ns": repeticiones[4],
            "promedio_ns": round(prom_ns, 2),
            "promedio_ms": round(prom_ns / 1_000_000.0, 6),
            "desviacion_estandar_ns": round(dev_ns, 2),
            "estado": estado,
            "observacion": observacion,
        }

    def _guardar_registro(self, registro: Dict[str, Any]):
        """Agrega (o reemplaza) el registro y reescribe los archivos CSV y JSON."""
        clave = tuple(registro[k] for k in self.CLAVE)
        self.registros = [r for r in self.registros if tuple(r.get(k) for k in self.CLAVE) != clave]
        self.registros.append(registro)

        with open(self.ruta_csv, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(self.registros)

        with open(self.ruta_json, mode="w", encoding="utf-8") as f:
            json.dump(self.registros, f, indent=4, ensure_ascii=False)


def cargar_resultados(experimento: str, directorio: str = None) -> List[Dict[str, Any]]:
    """Lee los resultados registrados de un punto (para gráficas o para el Punto 3)."""
    return GestorResultados(experimento, directorio).registros


# ==============================================================================
# 3. EJEMPLO PRÁCTICO DE USO (escribe en resultados_ejemplo.*, no en los de un punto)
# ==============================================================================

if __name__ == "__main__":
    gestor = GestorResultados("ejemplo")
    arr_original = cargar_arreglo(n=1000, variante="random")
    esperado = sorted(arr_original)

    tiempos_obtenidos = []
    for rep in range(REPETICIONES):
        copia_trabajo = arr_original.copy()  # Copia sin incluir el tiempo de clonado

        t_inicio = time.perf_counter_ns()
        copia_trabajo.sort()  # --- AQUÍ VA TU ALGORITMO A EVALUAR ---
        t_fin = time.perf_counter_ns()

        # Verificación fuera de la medición
        assert copia_trabajo == esperado, "Error: El arreglo no quedó ordenado"
        tiempos_obtenidos.append(t_fin - t_inicio)

    print(json.dumps(gestor.registrar_ejecucion_medida(
        "Ejemplo Sort nativo", "Python", "random", 1000, tiempos_obtenidos), indent=2))

    # Ejemplo de valor estimado (p. ej. Insertion Sort con n = 1.000.000)
    print(json.dumps(gestor.registrar_ejecucion_estimada(
        "Ejemplo Insertion Sort", "Python", "random", 1_000_000, 500_000_000_000.0,
        observacion="Supera 5 min; estimado como T(100000) * 100 por O(n^2)"), indent=2))
