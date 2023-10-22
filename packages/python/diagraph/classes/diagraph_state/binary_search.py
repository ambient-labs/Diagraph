def binary_search(arr: list, x: int | float, high=None, low=0) -> int | None:
    if len(arr) == 0:
        return None
    if high is None:
        high = len(arr) - 1

    closest_previous = None

    while low <= high:
        mid = (high + low) // 2

        if arr[mid] == x:
            return mid
        if arr[mid] < x:
            closest_previous = mid
            low = mid + 1
        else:
            high = mid - 1

    return closest_previous
