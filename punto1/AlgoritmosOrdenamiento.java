package punto1;

import java.util.ArrayList;
import java.util.Arrays;

/**
 * Punto 1 - Algoritmos de ordenamiento (Java, lenguaje compilado).
 *
 * Fuentes (GeeksforGeeks), misma lógica que la versión Python (punto1/algoritmos_ordenamiento.py):
 *   Insertion Sort        https://www.geeksforgeeks.org/dsa/insertion-sort-algorithm/
 *   Dual-Pivot QuickSort  https://www.geeksforgeeks.org/dsa/dual-pivot-quicksort/
 *   Merge Sort            https://www.geeksforgeeks.org/dsa/merge-sort/
 *   Heap Sort             https://www.geeksforgeeks.org/dsa/heap-sort/
 *   Radix Sort            https://www.geeksforgeeks.org/dsa/radix-sort/
 *   Bucket Sort           https://www.geeksforgeeks.org/dsa/bucket-sort-2/
 *                         (adaptado a enteros: n cubetas, índice proporcional al valor)
 *
 * Todas las funciones ordenan el arreglo IN SITU.
 */
public class AlgoritmosOrdenamiento {

    // ------------------------------------------------------------- Insertion
    public static void insertionSort(int[] arr) {
        int n = arr.length;
        for (int i = 1; i < n; ++i) {
            int key = arr[i];
            int j = i - 1;
            while (j >= 0 && arr[j] > key) {
                arr[j + 1] = arr[j];
                j = j - 1;
            }
            arr[j + 1] = key;
        }
    }

    // -------------------------------------------------- Dual-Pivot QuickSort
    // Pivotes: primer elemento (p) y último elemento (q), con p <= q.
    public static void swap(int[] arr, int i, int j) {
        int t = arr[i]; arr[i] = arr[j]; arr[j] = t;
    }

    public static int[] partition(int[] arr, int low, int high) {
        if (arr[low] > arr[high]) swap(arr, low, high);
        int j = low + 1, k = low + 1, g = high - 1;
        int p = arr[low], q = arr[high];
        while (k <= g) {
            if (arr[k] < p) {                       // va a la parte izquierda
                swap(arr, k, j);
                j++;
            } else if (arr[k] >= q) {               // va a la parte derecha
                while (arr[g] > q && k < g) g--;
                swap(arr, k, g);
                g--;
                if (arr[k] < p) {
                    swap(arr, k, j);
                    j++;
                }
            }
            k++;
        }
        j--;
        g++;
        swap(arr, low, j);                          // pivotes a su posición final
        swap(arr, high, g);
        return new int[]{j, g};
    }

    public static void dualPivotQuickSort(int[] arr, int low, int high) {
        if (low < high) {
            int[] piv = partition(arr, low, high);
            dualPivotQuickSort(arr, low, piv[0] - 1);
            dualPivotQuickSort(arr, piv[0] + 1, piv[1] - 1);
            dualPivotQuickSort(arr, piv[1] + 1, high);
        }
    }

    public static void dualPivotQuickSort(int[] arr) { dualPivotQuickSort(arr, 0, arr.length - 1); }

    // ----------------------------------------------------------------- Merge
    public static void merge(int[] arr, int left, int mid, int right) {
        int n1 = mid - left + 1, n2 = right - mid;
        int[] L = new int[n1], R = new int[n2];
        for (int i = 0; i < n1; i++) L[i] = arr[left + i];
        for (int j = 0; j < n2; j++) R[j] = arr[mid + 1 + j];
        int i = 0, j = 0, k = left;
        while (i < n1 && j < n2) {
            if (L[i] <= R[j]) arr[k++] = L[i++];
            else              arr[k++] = R[j++];
        }
        while (i < n1) arr[k++] = L[i++];
        while (j < n2) arr[k++] = R[j++];
    }

    public static void mergeSort(int[] arr, int left, int right) {
        if (left < right) {
            int mid = left + (right - left) / 2;
            mergeSort(arr, left, mid);
            mergeSort(arr, mid + 1, right);
            merge(arr, left, mid, right);
        }
    }

    public static void mergeSort(int[] arr) { mergeSort(arr, 0, arr.length - 1); }

    // ------------------------------------------------------------------ Heap
    public static void heapify(int[] arr, int n, int i) {
        int largest = i, l = 2 * i + 1, r = 2 * i + 2;
        if (l < n && arr[l] > arr[largest]) largest = l;
        if (r < n && arr[r] > arr[largest]) largest = r;
        if (largest != i) {
            swap(arr, i, largest);
            heapify(arr, n, largest);
        }
    }

    public static void heapSort(int[] arr) {
        int n = arr.length;
        for (int i = n / 2 - 1; i >= 0; i--) heapify(arr, n, i);   // construir max-heap
        for (int i = n - 1; i > 0; i--) {                           // extraer el máximo
            swap(arr, 0, i);
            heapify(arr, i, 0);
        }
    }

    // ----------------------------------------------------------------- Radix
    // LSD, base 10, con Counting Sort estable por dígito.
    public static void countSort(int[] arr, int exp) {
        int n = arr.length;
        int[] output = new int[n];
        int[] count = new int[10];
        for (int i = 0; i < n; i++) count[(arr[i] / exp) % 10]++;
        for (int i = 1; i < 10; i++) count[i] += count[i - 1];
        for (int i = n - 1; i >= 0; i--) {
            int d = (arr[i] / exp) % 10;
            output[count[d] - 1] = arr[i];
            count[d]--;
        }
        System.arraycopy(output, 0, arr, 0, n);
    }

    public static void radixSort(int[] arr) {
        if (arr.length == 0) return;
        int m = Arrays.stream(arr).max().getAsInt();
        for (long exp = 1; m / exp > 0; exp *= 10) countSort(arr, (int) exp);
    }

    // ---------------------------------------------------------------- Bucket
    // Número de cubetas: n (una por elemento).
    // Cubeta del valor x: idx = (x - min) * n / (max - min + 1)  -> 0 .. n-1
    // Cada cubeta (ArrayList, como en GeeksforGeeks) se ordena con Insertion Sort
    // y luego se concatenan en orden.
    public static void insertionSortList(ArrayList<Integer> b) {
        for (int i = 1; i < b.size(); i++) {
            int key = b.get(i);
            int j = i - 1;
            while (j >= 0 && b.get(j) > key) {
                b.set(j + 1, b.get(j));
                j--;
            }
            b.set(j + 1, key);
        }
    }

    @SuppressWarnings("unchecked")
    public static void bucketSort(int[] arr) {
        int n = arr.length;
        if (n <= 1) return;
        int mn = Arrays.stream(arr).min().getAsInt();
        int mx = Arrays.stream(arr).max().getAsInt();
        long rango = (long) mx - mn + 1;
        ArrayList<Integer>[] buckets = new ArrayList[n];
        for (int i = 0; i < n; i++) buckets[i] = new ArrayList<>();
        for (int x : arr) buckets[(int) ((long) (x - mn) * n / rango)].add(x);
        for (ArrayList<Integer> b : buckets) insertionSortList(b);
        int idx = 0;
        for (ArrayList<Integer> b : buckets)
            for (int x : b) arr[idx++] = x;
    }
}
