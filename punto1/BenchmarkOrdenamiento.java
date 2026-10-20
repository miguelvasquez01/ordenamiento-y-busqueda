package punto1;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;

/**
 * Punto 1 - Mide UN caso (algoritmo, variante, n) de ordenamiento en Java.
 *
 * Normalmente no se ejecuta a mano: lo llama punto1/benchmark_ordenamiento.py --java,
 * que corre cada caso en un proceso aparte (así un StackOverflowError o un caso que
 * supera los 5 minutos no detiene el resto del experimento).
 *
 * Compilar (desde la raíz del repositorio):
 *   javac -d out punto1/AlgoritmosOrdenamiento.java punto1/BenchmarkOrdenamiento.java
 * Ejecutar un caso a mano:
 *   java -cp out punto1.BenchmarkOrdenamiento insertion random 1000 5
 *
 * - Lee datos_prueba/datos_{n}_{variante}.txt ANTES de medir.
 * - Calentamiento JIT (no se incluye en el promedio): 20 ejecuciones sobre un subarreglo de
 *   hasta 10.000 elementos + 1 ejecución completa. Con una sola ejecución completa las
 *   repeticiones 1 y 2 aún corrían ~3 veces más lento (código sin optimizar del todo).
 * - Cada repetición ordena una COPIA nueva del arreglo original (la copia no se mide).
 * - Mide con System.nanoTime() solo la llamada al algoritmo.
 * - Verifica, fuera del tiempo medido, que el resultado quedó ordenado.
 * - Imprime una línea JSON con los tiempos en ns, o el error si falló.
 * - Se ejecuta con el tamaño de pila por defecto de la JVM (sin -Xss), a propósito: así se
 *   observa el StackOverflowError de Dual-Pivot QuickSort con datos ordenados.
 */
public class BenchmarkOrdenamiento {

    interface Sorter { void sort(int[] a); }

    static Sorter elegir(String alg) {
        switch (alg) {
            case "insertion":       return AlgoritmosOrdenamiento::insertionSort;
            case "dualpivot_quick": return AlgoritmosOrdenamiento::dualPivotQuickSort;
            case "merge":           return AlgoritmosOrdenamiento::mergeSort;
            case "heap":            return AlgoritmosOrdenamiento::heapSort;
            case "radix":           return AlgoritmosOrdenamiento::radixSort;
            case "bucket":          return AlgoritmosOrdenamiento::bucketSort;
            default: throw new IllegalArgumentException("algoritmo desconocido: " + alg);
        }
    }

    static int[] cargar(String ruta) throws IOException {
        return Files.readAllLines(Path.of(ruta)).stream()
                .filter(l -> !l.isBlank()).mapToInt(l -> Integer.parseInt(l.trim())).toArray();
    }

    public static void main(String[] args) throws IOException {
        if (args.length < 4) {
            System.err.println("uso: java -cp out punto1.BenchmarkOrdenamiento <algoritmo> <random|asc|desc> <n> <repeticiones>");
            System.exit(2);
        }
        Sorter s = elegir(args[0]);
        String variante = args[1];
        int n = Integer.parseInt(args[2]);
        int reps = Integer.parseInt(args[3]);

        int[] original = cargar("datos_prueba/datos_" + n + "_" + variante + ".txt");
        int[] referencia = original.clone();
        Arrays.sort(referencia);

        long[] tiempos = new long[reps];
        try {
            int[] sub = Arrays.copyOf(original, Math.min(original.length, 10_000));
            for (int w = 0; w < 20; w++) s.sort(sub.clone());          // calentamiento JIT (a)
            int[] cal = original.clone();                               // calentamiento JIT (b)
            s.sort(cal);
            if (!Arrays.equals(cal, referencia)) {
                System.out.println("{\"ok\": false, \"error\": \"verificacion fallida\"}");
                return;
            }
            for (int r = 0; r < reps; r++) {
                int[] copia = original.clone();                         // copia fuera del tiempo
                long t0 = System.nanoTime();
                s.sort(copia);
                long t1 = System.nanoTime();
                if (!Arrays.equals(copia, referencia)) {                // verificación fuera del tiempo
                    System.out.println("{\"ok\": false, \"error\": \"verificacion fallida\"}");
                    return;
                }
                tiempos[r] = t1 - t0;
            }
        } catch (StackOverflowError e) {
            System.out.println("{\"ok\": false, \"error\": \"java.lang.StackOverflowError: "
                    + "desbordamiento de la pila de llamadas (recursion demasiado profunda)\"}");
            return;
        }
        StringBuilder sb = new StringBuilder("{\"ok\": true, \"tiempos_ns\": [");
        for (int i = 0; i < reps; i++) sb.append(i > 0 ? ", " : "").append(tiempos[i]);
        System.out.println(sb.append("]}"));
    }
}
