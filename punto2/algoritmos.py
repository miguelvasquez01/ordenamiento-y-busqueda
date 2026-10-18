import math


def linear_search(arr, x):
    n = len(arr)
    
    # Iterate over the array in order to
    # find the key x
    for i in range(0, n):
        if (arr[i] == x):
            return i
    return -1

def binarySearch(arr, x):
    low = 0
    high = len(arr) - 1
    while low <= high:

        mid = low + (high - low) // 2

        # Check if x is present at mid
        if arr[mid] == x:
            return mid

        # If x is greater, ignore left half
        elif arr[mid] < x:
            low = mid + 1

        # If x is smaller, ignore right half
        else:
            high = mid - 1

    # If we reach here, then the element
    # was not present
    return -1

def ternarySearch(arr, x):
    l = 0
    r = len(arr) - 1

    while l <= r:
        
        # Split array portion into 3 parts
        mid1 = l + (r - l) // 3
        mid2 = r - (r - l) // 3

        if arr[mid1] == x or arr[mid2] == x:
            return True

        if x < arr[mid1]:
            r = mid1 - 1
        elif x > arr[mid2]:
            l = mid2 + 1
        else:
            l = mid1 + 1
            r = mid2 - 1

    return False

def jumpSearch( arr , x , n ):
    
    # Finding block size to be jumped
    step = int(math.sqrt(n))
    
    # Finding the block where element is
    # present (if it is present)
    prev = 0
    while arr[min(step, n)-1] < x:
        prev = step
        step += int(math.sqrt(n))
        if prev >= n:
            return -1
    
    # Doing a linear search for x in 
    # block beginning with prev.
    while arr[prev] < x:
        prev += 1
        
        # If we reached next block or end 
        # of array, element is not present.
        if prev == min(step, n):
            return -1
    
    # If element is found
    if arr[prev] == x:
        return prev
    
    return -1

def interpolationSearch(arr, lo, hi, x):

    # Since array is sorted, an element present
    # in array must be in range defined by corner
    if (lo <= hi and x >= arr[lo] and x <= arr[hi]):

        # Avoid division by zero when all values in range are equal
        if arr[hi] == arr[lo]:
            return lo

        # Probing the position with keeping
        # uniform distribution in mind.
        # (multiply before dividing; otherwise integer division yields 0)
        pos = lo + ((hi - lo) * (x - arr[lo]) //
                    (arr[hi] - arr[lo]))

        # Condition of target found
        if arr[pos] == x:
            return pos

        # If x is larger, x is in right subarray
        if arr[pos] < x:
            return interpolationSearch(arr, pos + 1,
                                       hi, x)

        # If x is smaller, x is in left subarray
        if arr[pos] > x:
            return interpolationSearch(arr, lo,
                                       pos - 1, x)
    return -1

def exponential_search(arr, x):
    n = len(arr)
    if n == 0:
        return -1

    # Find range for binary search by repeatedly doubling i
    i = 1
    while i < n and arr[i] < x:
        i *= 2

    # Perform binary search on the range [i/2, min(i, n-1)]
    left = i // 2
    right = min(i, n-1)

    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == x:
            return mid
        elif arr[mid] < x:
            left = mid + 1
        else:
            right = mid - 1

    return -1