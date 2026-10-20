"""
Punto 1 - Algoritmos de ordenamiento (Python, lenguaje interpretado).

Fuentes (GeeksforGeeks), misma lógica que la versión Java (punto1/AlgoritmosOrdenamiento.java):
  Insertion Sort        https://www.geeksforgeeks.org/dsa/insertion-sort-algorithm/
  Dual-Pivot QuickSort  https://www.geeksforgeeks.org/dsa/dual-pivot-quicksort/
  Merge Sort            https://www.geeksforgeeks.org/dsa/merge-sort/
  Heap Sort             https://www.geeksforgeeks.org/dsa/heap-sort/
  Radix Sort            https://www.geeksforgeeks.org/dsa/radix-sort/
  Bucket Sort           https://www.geeksforgeeks.org/dsa/bucket-sort-2/
                        (adaptado a enteros: n cubetas, índice proporcional al valor)

Todas las funciones ordenan la lista IN SITU (modifican la lista recibida).
"""


# ----------------------------------------------------------------- Insertion
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


# ------------------------------------------------- Dual-Pivot QuickSort
# Pivotes: primer elemento (p) y último elemento (q), con p <= q.
def _partition(arr, low, high):
    if arr[low] > arr[high]:
        arr[low], arr[high] = arr[high], arr[low]
    j = k = low + 1
    g = high - 1
    p = arr[low]
    q = arr[high]
    while k <= g:
        if arr[k] < p:                      # va a la parte izquierda
            arr[k], arr[j] = arr[j], arr[k]
            j += 1
        elif arr[k] >= q:                   # va a la parte derecha
            while arr[g] > q and k < g:
                g -= 1
            arr[k], arr[g] = arr[g], arr[k]
            g -= 1
            if arr[k] < p:
                arr[k], arr[j] = arr[j], arr[k]
                j += 1
        k += 1
    j -= 1
    g += 1
    arr[low], arr[j] = arr[j], arr[low]     # coloca los pivotes en su posición final
    arr[high], arr[g] = arr[g], arr[high]
    return j, g


def _dual_pivot_quick_sort(arr, low, high):
    if low < high:
        lp, rp = _partition(arr, low, high)
        _dual_pivot_quick_sort(arr, low, lp - 1)
        _dual_pivot_quick_sort(arr, lp + 1, rp - 1)
        _dual_pivot_quick_sort(arr, rp + 1, high)


def dual_pivot_quick_sort(arr):
    _dual_pivot_quick_sort(arr, 0, len(arr) - 1)


# ------------------------------------------------------------------- Merge
def _merge(arr, left, mid, right):
    L = arr[left:mid + 1]
    R = arr[mid + 1:right + 1]
    n1, n2 = len(L), len(R)
    i = j = 0
    k = left
    while i < n1 and j < n2:
        if L[i] <= R[j]:
            arr[k] = L[i]
            i += 1
        else:
            arr[k] = R[j]
            j += 1
        k += 1
    while i < n1:
        arr[k] = L[i]
        i += 1
        k += 1
    while j < n2:
        arr[k] = R[j]
        j += 1
        k += 1


def _merge_sort(arr, left, right):
    if left < right:
        mid = left + (right - left) // 2
        _merge_sort(arr, left, mid)
        _merge_sort(arr, mid + 1, right)
        _merge(arr, left, mid, right)


def merge_sort(arr):
    _merge_sort(arr, 0, len(arr) - 1)


# -------------------------------------------------------------------- Heap
def _heapify(arr, n, i):
    largest = i
    l = 2 * i + 1
    r = 2 * i + 2
    if l < n and arr[l] > arr[largest]:
        largest = l
    if r < n and arr[r] > arr[largest]:
        largest = r
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        _heapify(arr, n, largest)


def heap_sort(arr):
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):     # construir max-heap
        _heapify(arr, n, i)
    for i in range(n - 1, 0, -1):           # extraer el máximo uno a uno
        arr[0], arr[i] = arr[i], arr[0]
        _heapify(arr, i, 0)


# ------------------------------------------------------------------- Radix
# LSD, base 10, con Counting Sort estable por dígito.
def _counting_sort(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10
    for i in range(n):
        count[(arr[i] // exp) % 10] += 1
    for i in range(1, 10):
        count[i] += count[i - 1]
    for i in range(n - 1, -1, -1):
        d = (arr[i] // exp) % 10
        output[count[d] - 1] = arr[i]
        count[d] -= 1
    for i in range(n):
        arr[i] = output[i]


def radix_sort(arr):
    if not arr:
        return
    m = max(arr)
    exp = 1
    while m // exp > 0:
        _counting_sort(arr, exp)
        exp *= 10


# ------------------------------------------------------------------ Bucket
# Número de cubetas: n (una por elemento).
# Cubeta del valor x: idx = (x - min) * n // (max - min + 1)  -> 0 .. n-1
# Cada cubeta se ordena con Insertion Sort y luego se concatenan en orden.
def _insertion_sort_list(b):
    for i in range(1, len(b)):
        key = b[i]
        j = i - 1
        while j >= 0 and b[j] > key:
            b[j + 1] = b[j]
            j -= 1
        b[j + 1] = key


def bucket_sort(arr):
    n = len(arr)
    if n <= 1:
        return
    mn = min(arr)
    mx = max(arr)
    rango = mx - mn + 1
    buckets = [[] for _ in range(n)]
    for x in arr:
        buckets[(x - mn) * n // rango].append(x)
    for b in buckets:
        _insertion_sort_list(b)
    idx = 0
    for b in buckets:
        for x in b:
            arr[idx] = x
            idx += 1


ALGORITMOS = {
    "insertion": insertion_sort,
    "dualpivot_quick": dual_pivot_quick_sort,
    "merge": merge_sort,
    "heap": heap_sort,
    "radix": radix_sort,
    "bucket": bucket_sort,
}
