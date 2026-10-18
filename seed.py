import os
import random
import sys

# Configuración del Taller
SIZES = [1_000, 10_000, 100_000, 1_000_000]
MIN_VAL = 10_000_000
MAX_VAL = 99_999_999
SEED = 42  # Semilla fija para reproducibilidad
DATA_DIR = "datos_prueba"
ARCHIVO_CLAVES = "claves_busqueda_punto2.txt"

def crear_directorio():
    """Crea la carpeta para almacenar los datos si no existe."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Directorio creado: {DATA_DIR}/")

def generar_datos_ordenamiento(force=False):
    """
    Genera y guarda los arreglos de enteros de 8 dígitos para el Punto 1.
    Crea 3 archivos por tamaño: aleatorio, ascendente y descendente.

    Se genera UN solo arreglo aleatorio de N_MAX elementos y el arreglo de tamaño n
    son sus primeros n elementos. Así los conjuntos quedan anidados
    (datos_1000 ⊂ datos_10000 ⊂ datos_100000 ⊂ datos_1000000), lo que permite que
    un mismo conjunto de claves de búsqueda sirva para todos los tamaños (Punto 2).
    Cada prefijo sigue siendo una muestra aleatoria uniforme e independiente del resto.
    """
    random.seed(SEED)
    print("=" * 60)
    print("GENERANDO DATOS DE PRUEBA PARA ALGORITMOS DE ORDENAMIENTO")
    print("=" * 60)

    n_max = max(SIZES)
    print(f"Generando {n_max:,} elementos aleatorios de 8 dígitos (semilla {SEED})...")
    arr_completo = [random.randint(MIN_VAL, MAX_VAL) for _ in range(n_max)]

    for n in SIZES:
        archivo_aleatorio = os.path.join(DATA_DIR, f"datos_{n}_random.txt")
        archivo_ascendente = os.path.join(DATA_DIR, f"datos_{n}_asc.txt")
        archivo_descendente = os.path.join(DATA_DIR, f"datos_{n}_desc.txt")

        # Verificar si ya existen
        if not force and os.path.exists(archivo_aleatorio) and os.path.exists(archivo_ascendente) and os.path.exists(archivo_descendente):
            print(f"[OMITIDO] Datos para N = {n:,} ya existen.")
            continue

        arr = arr_completo[:n]

        # 1. Guardar archivo Aleatorio
        with open(archivo_aleatorio, "w") as f:
            f.write("\n".join(map(str, arr)) + "\n")
        print(f"  -> Guardado: {archivo_aleatorio}")

        # 2. Guardar archivo Ascendente
        arr_asc = sorted(arr)
        with open(archivo_ascendente, "w") as f:
            f.write("\n".join(map(str, arr_asc)) + "\n")
        print(f"  -> Guardado: {archivo_ascendente}")

        # 3. Guardar archivo Descendente
        arr_desc = arr_asc[::-1]
        with open(archivo_descendente, "w") as f:
            f.write("\n".join(map(str, arr_desc)) + "\n")
        print(f"  -> Guardado: {archivo_descendente}")

def generar_claves_busqueda(force=False):
    """
    Genera 1.000 claves para el Punto 2 (Búsqueda), válidas para TODOS los tamaños:
    - 500 claves presentes: tomadas del arreglo más pequeño (n = 1.000). Como los
      arreglos están anidados, también están presentes en los de 10.000, 100.000 y 1.000.000.
    - 500 claves ausentes: valores de 8 dígitos que no están en el arreglo de 1.000.000,
      por lo tanto tampoco en ninguno de los menores.
    """
    archivo_claves = os.path.join(DATA_DIR, ARCHIVO_CLAVES)
    archivo_menor = os.path.join(DATA_DIR, f"datos_{min(SIZES)}_random.txt")
    archivo_mayor = os.path.join(DATA_DIR, f"datos_{max(SIZES)}_random.txt")

    if not force and os.path.exists(archivo_claves):
        print(f"\n[OMITIDO] Claves de búsqueda ya existen: {archivo_claves}")
        return

    print("\n" + "=" * 60)
    print("GENERANDO CLAVES DE BÚSQUEDA (PUNTO 2)")
    print("=" * 60)

    if not os.path.exists(archivo_menor) or not os.path.exists(archivo_mayor):
        print("Error: Se necesitan los arreglos de datos previamente generados.")
        return

    with open(archivo_menor, "r") as f:
        arr_menor = [int(line) for line in f if line.strip()]
    with open(archivo_mayor, "r") as f:
        set_mayor = {int(line) for line in f if line.strip()}

    # Semilla propia para que las claves no dependan del orden de generación de los datos
    rng = random.Random(SEED + 1)

    # 1. Seleccionar 500 claves PRESENTES (del arreglo de n = 1.000, sin repetir valores)
    claves_presentes = rng.sample(sorted(set(arr_menor)), 500)

    # 2. Generar 500 claves AUSENTES (distintas entre sí)
    claves_ausentes = set()
    while len(claves_ausentes) < 500:
        val = rng.randint(MIN_VAL, MAX_VAL)
        if val not in set_mayor:
            claves_ausentes.add(val)

    # Mezclar las 1.000 claves para intercalar presentes y ausentes
    todas_las_claves = claves_presentes + sorted(claves_ausentes)
    rng.shuffle(todas_las_claves)

    # Guardar en archivo
    with open(archivo_claves, "w") as f:
        f.write("\n".join(map(str, todas_las_claves)) + "\n")

    print(f"  -> Guardado: {archivo_claves} (500 presentes + 500 ausentes, para todos los n)")

# ==============================================================================
# FUNCIONES AUXILIARES PARA USAR EN TUS ALGORITMOS (LECTURA)
# ==============================================================================

def cargar_arreglo(n: int, variante: str = "random") -> list[int]:
    """
    Función de utilidad para cargar un arreglo previamente generado.
    
    :param n: Tamaño del arreglo (1000, 10000, 100000, 1000000)
    :param variante: 'random', 'asc', o 'desc'
    :return: Lista de enteros
    """
    nombre_archivo = f"datos_{n}_{variante}.txt"
    ruta = os.path.join(DATA_DIR, nombre_archivo)
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"El archivo {ruta} no existe. Ejecuta generar_datos.py primero.")
    
    with open(ruta, "r") as f:
        return [int(line) for line in f if line.strip()]

def cargar_claves_busqueda() -> list[int]:
    """Carga la lista de las 1.000 claves de búsqueda para el Punto 2."""
    ruta = os.path.join(DATA_DIR, ARCHIVO_CLAVES)
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"El archivo {ruta} no existe. Ejecuta generar_datos.py primero.")
    
    with open(ruta, "r") as f:
        return [int(line) for line in f if line.strip()]

if __name__ == "__main__":
    forzar_regeneracion = "--force" in sys.argv or "-f" in sys.argv
    crear_directorio()
    generar_datos_ordenamiento(force=forzar_regeneracion)
    generar_claves_busqueda(force=forzar_regeneracion)
    print("\n[OK] Generación finalizada exitosamente.")