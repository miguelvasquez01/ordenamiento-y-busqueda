package punto2;

import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/**
 * Punto 2 - Benchmark de algoritmos de búsqueda (Java).
 *
 * Compilar y ejecutar desde la raíz del repositorio:
 *   javac -d out punto2/algoritmos.java punto2/BenchmarkBusqueda.java
 *   java -Xss64m -cp out punto2.BenchmarkBusqueda
 * Luego registrar los resultados:
 *   py punto2/benchmark_busqueda.py --java
 *
 * Escribe resultados_experimentos/tiempos_crudos_java_punto2_busqueda.csv con el tiempo promedio
 * POR BÚSQUEDA (total de 1.000 búsquedas / 1.000) de cada una de las 5 repeticiones.
 */
public class BenchmarkBusqueda {

    static final int[] SIZES = {1_000, 10_000, 100_000, 1_000_000};
    static final int REPETICIONES = 5;
    static final int N_POSICIONES = 1_000_000;
    static final int BUSQUEDAS_POR_POSICION = 1_000;
    static final String SALIDA = "resultados_experimentos/tiempos_crudos_java_punto2_busqueda.csv";

    interface Busqueda {
        boolean buscar(int[] arr, int x);
    }

    static final String[] NOMBRES = {
        "Busqueda Lineal", "Busqueda Binaria", "Busqueda Ternaria",
        "Busqueda por Saltos", "Busqueda por Interpolacion", "Busqueda Exponencial"
    };

    static final Busqueda[] ALGORITMOS = {
        (arr, x) -> algoritmos.linear_search(arr, x) != -1,
        (arr, x) -> algoritmos.binarySearch(arr, x) != -1,
        (arr, x) -> algoritmos.ternarySearch(arr, x),
        (arr, x) -> algoritmos.jumpSearch(arr, x) != -1,
        (arr, x) -> algoritmos.interpolationSearch(arr, 0, arr.length - 1, x) != -1,
        (arr, x) -> algoritmos.exponential_search(arr, x) != -1,
    };

    // Evita que el JIT elimine las búsquedas cuyo resultado no se usa
    static long sumidero = 0;

    static int[] cargar(String ruta) throws IOException {
        List<String> lineas = Files.readAllLines(Path.of(ruta));
        return lineas.stream().filter(l -> !l.isBlank()).mapToInt(l -> Integer.parseInt(l.trim())).toArray();
    }

    /** Tiempo promedio por búsqueda (ns) de buscar todas las claves, una vez. */
    static double medir(Busqueda b, int[] arr, int[] claves) {
        int encontrados = 0;
        long inicio = System.nanoTime();
        for (int x : claves) {
            if (b.buscar(arr, x)) encontrados++;
        }
        long fin = System.nanoTime();
        sumidero += encontrados;
        return (double) (fin - inicio) / claves.length;
    }

    /** Fuera de la medición: comprueba que el algoritmo encuentra exactamente las claves presentes. */
    static void verificar(String nombre, Busqueda b, int[] arr, int[] claves, Set<Integer> conjunto) {
        for (int x : claves) {
            if (b.buscar(arr, x) != conjunto.contains(x)) {
                throw new IllegalStateException(nombre + " devolvió un resultado incorrecto para la clave " + x);
            }
        }
    }

    static double[] repetir(Busqueda b, int[] arr, int[] claves) {
        medir(b, arr, claves); // calentamiento JIT, no se incluye en el promedio
        double[] t = new double[REPETICIONES];
        for (int r = 0; r < REPETICIONES; r++) t[r] = medir(b, arr, claves);
        return t;
    }

    static void escribir(PrintWriter out, String algoritmo, String variante, int n, double[] t) {
        StringBuilder sb = new StringBuilder(algoritmo + "," + variante + "," + n);
        double suma = 0;
        for (double v : t) {
            sb.append(String.format(Locale.US, ",%.3f", v));
            suma += v;
        }
        out.println(sb);
        out.flush();
        System.out.printf(Locale.US, "  [%-8s] %-28s %14.1f ns/búsqueda%n", variante, algoritmo, suma / t.length);
    }

    public static void main(String[] args) throws IOException {
        Files.createDirectories(Path.of("resultados_experimentos"));
        int[] claves = cargar("datos_prueba/claves_busqueda_punto2.txt");

        // Calentamiento global (no se mide): deja que el JIT compile todos los algoritmos
        // antes de la primera medición, para que n pequeños no queden afectados.
        int[] arrCalentamiento = cargar("datos_prueba/datos_100000_asc.txt");
        for (int i = 0; i < 20; i++) {
            for (Busqueda b : ALGORITMOS) medir(b, arrCalentamiento, claves);
        }

        try (PrintWriter out = new PrintWriter(Files.newBufferedWriter(Path.of(SALIDA)))) {
            out.println("algoritmo,variante,n,t1_ns,t2_ns,t3_ns,t4_ns,t5_ns");

            // ---- Experimento 1: 1.000 claves mezcladas ----
            for (int n : SIZES) {
                int[] arr = cargar("datos_prueba/datos_" + n + "_asc.txt");
                Set<Integer> conjunto = new HashSet<>();
                for (int v : arr) conjunto.add(v);
                System.out.printf("%nn = %,d%n", n);
                for (int a = 0; a < ALGORITMOS.length; a++) {
                    verificar(NOMBRES[a], ALGORITMOS[a], arr, claves, conjunto);
                    escribir(out, NOMBRES[a], "mezclado", n, repetir(ALGORITMOS[a], arr, claves));
                }
            }

            // ---- Experimento 2: posición de la clave (n = 1.000.000) ----
            int[] arr = cargar("datos_prueba/datos_" + N_POSICIONES + "_asc.txt");
            String[] posiciones = {"inicio", "centro", "final"};
            int[] valores = {arr[0], arr[arr.length / 2], arr[arr.length - 1]};
            System.out.printf("%nPosición de la clave, n = %,d%n", N_POSICIONES);
            for (int p = 0; p < posiciones.length; p++) {
                int[] clavesPos = new int[BUSQUEDAS_POR_POSICION];
                java.util.Arrays.fill(clavesPos, valores[p]);
                for (int a = 0; a < ALGORITMOS.length; a++) {
                    if (!ALGORITMOS[a].buscar(arr, valores[p])) {
                        throw new IllegalStateException(NOMBRES[a] + " no encontró la clave de la posición " + posiciones[p]);
                    }
                    escribir(out, NOMBRES[a], posiciones[p], N_POSICIONES, repetir(ALGORITMOS[a], arr, clavesPos));
                }
            }
        }
        System.out.println("\n[OK] Tiempos guardados en " + SALIDA + " (sumidero=" + sumidero + ")");
        System.out.println("Ejecute: py punto2/benchmark_busqueda.py --java  para registrarlos.");
    }
}
