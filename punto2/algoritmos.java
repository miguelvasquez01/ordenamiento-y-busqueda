package punto2;

public class algoritmos {
    
    // Function to search for an element in the array
    static int linear_search(int[] arr, int x) {

        // Iterate over the array to find x
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] == x) {
                return i;
            }
        }

        return -1;
    }

    static int binarySearch(int arr[], int x) {
        int low = 0, high = arr.length - 1;
        while (low <= high) {
            int mid = low + (high - low) / 2;

            // Check if x is present at mid
            if (arr[mid] == x)
                return mid;

            // If x greater, ignore left half
            if (arr[mid] < x)
                low = mid + 1;

            // If x is smaller, ignore right half
            else
                high = mid - 1;
        }

        // If we reach here, then element was
        // not present
        return -1;
    }

    static boolean ternarySearch(int[] arr, int x) {
        int l = 0;
        int r = arr.length - 1;

        while (l <= r) {
            
            // Split array portion into 3 parts
            int mid1 = l + (r - l) / 3;
            int mid2 = r - (r - l) / 3;

            if (arr[mid1] == x || arr[mid2] == x) {
                return true;
            }

            if (x < arr[mid1]) {
                r = mid1 - 1;
            } else if (x > arr[mid2]) {
                l = mid2 + 1;
            } else {
                l = mid1 + 1;
                r = mid2 - 1;
            }
        }

        return false;
    }

    public static int jumpSearch(int[] arr, int x)  
    {
        int n = arr.length;

        // Finding block size to be jumped
        int step = (int)Math.floor(Math.sqrt(n));

        // Finding the block where element is
        // present (if it is present)
        int prev = 0;
        for (int minStep = Math.min(step, n)-1; arr[minStep] < x; minStep = Math.min(step, n)-1)
        {
            prev = step;
            step += (int)Math.floor(Math.sqrt(n));
            if (prev >= n)
                return -1;
        }

        // Doing a linear search for x in block
        // beginning with prev.
        while (arr[prev] < x)
        {
            prev++;

            // If we reached next block or end of
            // array, element is not present.
            if (prev == Math.min(step, n))
                return -1;
        }

        // If element is found
        if (arr[prev] == x)
            return prev;

        return -1;
    }

    // If x is present in arr[0..n-1], then returns
    // index of it, else returns -1.
    public static int interpolationSearch(int arr[], int lo,
                                          int hi, int x)
    {
        int pos;

        // Since array is sorted, an element
        // present in array must be in range
        // defined by corner
        if (lo <= hi && x >= arr[lo] && x <= arr[hi]) {

            // Avoid division by zero when all values in range are equal
            if (arr[hi] == arr[lo])
                return lo;

            // Probing the position with keeping
            // uniform distribution in mind.
            // (multiply before dividing, using long to avoid overflow;
            // otherwise integer division yields 0)
            pos = lo
                  + (int)(((long)(hi - lo) * (x - arr[lo]))
                          / (arr[hi] - arr[lo]));

            // Condition of target found
            if (arr[pos] == x)
                return pos;

            // If x is larger, x is in right sub array
            if (arr[pos] < x)
                return interpolationSearch(arr, pos + 1, hi,
                                           x);

            // If x is smaller, x is in left sub array
            if (arr[pos] > x)
                return interpolationSearch(arr, lo, pos - 1,
                                           x);
        }
        return -1;
    }

    // Returns position of 
    // first occurrence of
    // x in array
    public static int exponential_search(int[] arr, int x) {
        int n = arr.length;
        
        if (n == 0)
            return -1;
        
        // Find range for binary search by repeatedly doubling i
        int i = 1;
        while (i < n && arr[i] < x)
            i *= 2;
        
        // Perform binary search on the range [i/2, min(i, n-1)]
        int left = i / 2;
        int right = Math.min(i, n - 1);
        
        while (left <= right) {
            int mid = (left + right) / 2;  // finding mid
            
            if (arr[mid] == x)
                return mid;
            else if (arr[mid] < x)
                left = mid + 1;
            else
                right = mid - 1;
        }
        
        return -1;
    }
}
