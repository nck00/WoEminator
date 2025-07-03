import numpy as np


def getRandomArrays(
    inputArray: np.ndarray, count: int, percent=80, seed=42, noData=-9999
) -> tuple:
    """Returns a tuple of two lists:
    1. List of count Numpy Arrays with each a percent of inputArray (Training).
    2. List of count Numpy Arrays with each 100-percent of inputArray (Validation).
    Expects inputArray to be a Numpy array with 1 to n each indicating an individual landslide.
    0 means no landslide and noData no value.
    """
    values = np.unique(inputArray)
    if noData in values:  # We don't care about noData
        values = values[values != noData]
    if 0 in values:  # We only shuffle the landslides
        values = values[values != 0]
    lsCount = len(values)
    lsCountInTrainArray = int(
        round(lsCount / 100 * percent)
    )  # without round int() rounds down.
    lsCountInValArray = lsCount - lsCountInTrainArray
    trainArrays = []
    valArrays = []
    np.random.seed(seed)
    for i in range(count):
        trainValues = np.random.choice(values, size=lsCountInTrainArray, replace=False)
        valValues = np.setdiff1d(
            values, trainValues
        )  # Val = Values in values but not in train
        trainArray = inputArray.copy()
        np.put(
            trainArray, valValues, [0]
        )  # Replaces all valValues with 0 for TrainArray in place.
        valArray = inputArray.copy()
        np.put(
            valArray, trainValues, [0]
        )  # Replaces all trainValues with 0 for ValArray in place.
        trainArrays.append(trainArray)
        valArrays.append(valArray)
    return (trainArrays, valArrays)


if __name__ == "__main__":
    import timeit

    x = timeit.timeit(
        "getRandomArray(np.arange(815262).reshape(826, 987), 100, noData=899)",
        globals=globals(),
        number=1,
    )
    print(x)
