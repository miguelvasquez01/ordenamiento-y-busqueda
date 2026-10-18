import os
import random
import sys

# Configuración del Taller
SIZES = [1_000, 10_000, 100_000, 1_000_000]
MIN_VAL = 10_000_000
MAX_VAL = 99_999_999
SEED = 42  # Semilla fija para reproducibilidad
DATA_DIR = "datos_prueba"

def crear_directorio():
    """Crea la carpeta para almacenar los datos si no existe."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Directorio creado: {DATA_DIR}/")

def generar_datos_ordenamiento(force=False):
    """
    Genera y guarda los arreglos de enteros de 8 dígitos para el Punto 1.
    Crea 3 archivos por tamaño: aleatorio, ascendente y descendente.
    """
    random.seed(SEED)
    print("=" * 60)
    print("GENERANDO DATOS DE PRUEBA PARA ALGORITMOS DE ORDENAMIENTO")
    print("=" * 60)

    for n in SIZES:
        archivo_aleatorio = os.path.join(DATA_DIR, f"datos_{n}_random.txt")
        archivo_ascendente = os.path.join(DATA_DIR, f"datos_{n}_asc.txt")
        archivo_descendente = os.path.join(DATA_DIR, f"datos_{n}_desc.txt")

        # Verificar si ya existen
        if not force and os.path.exists(archivo_aleatorio) and os.path.exists(archivo_ascendente) and os.path.exists(archivo_descendente):
            print(f"[OMITIDO] Datos para N = {n:,} ya existen.")
            continue

        print(f"Generando {n:,} elementos aleatorios de 8 dígitos...")
        # Generar arreglo aleatorio
        arr = [random.randint(MIN_VAL, MAX_VAL) for _ in range(n)]

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
    Genera 1.000 claves para el Punto 2 (Búsqueda):
    - 500 claves presentes en el arreglo ordenado de 1.000.000.
    - 500 claves ausentes.
    """
    archivo_claves = os.path.join(DATA_DIR, "claves_busqueda_1000.txt")
    archivo_asc_1m = os.path.join(DATA_DIR, "datos_1000000_asc.txt")

    if not force and os.path.exists(archivo_claves):
        print(f"\n[OMITIDO] Claves de búsqueda ya existen: {archivo_claves}")
        return

    print("\n" + "=" * 60)
    print("GENERANDO CLAVES DE BÚSQUEDA (PUNTO 2)")
    print("=" * 60)

    if not os.path.exists(archivo_asc_1m):
        print("Error: Se necesita 'datos_1000000_asc.txt' previamente generado.")
        return

    # Cargar los datos ordenados de 1M
    print("Cargando arreglo de N = 1.000.000 para extraer muestras...")
    with open(archivo_asc_1m, "r") as f:
        arr_1m = [int(line.strip()) for line in f]

    set_1m = set(arr_1m)

    # 1. Seleccionar 500 claves PRESENTES
    claves_presentes = random.sample(arr_1m, 500)

    # 2. Generar 500 claves AUSENTES
    claves_ausentes = []
    while len(claves_ausentes) < 500:
        val = random.randint(MIN_VAL, MAX_VAL)
        if val not in set_1m:
            claves_ausentes.append(val)

    # Mezclar las 1.000 claves para intercalar presentes y ausentes
    todas_las_claves = claves_presentes + claves_ausentes
    random.shuffle(todas_las_claves)

    # Guardar en archivo
    with open(archivo_claves, "w") as f:
        f.write("\n".join(map(str, todas_las_claves)) + "\n")

    print(f"  -> Guardado: {archivo_claves} (500 presentes + 500 ausentes)")

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
    ruta = os.path.join(DATA_DIR, "claves_busqueda_1000.txt")
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