import numpy as np

def readyArray4calc(inputArray: np.ndarray) -> np.ndarray:
    """Returns an array with each element not 0 or noData (-9999) replaced with 1.
    Used to convert the randomized Arrays into a better format for calculation.
    """
    inputArray[inputArray >= 1] = 1 # We expect each value > 1 to be a landslide
    return inputArray

def fillArrayWithRandomNoDataUntilPercent(inputArray: np.ndarray, landslide = 1, noLandslide = 0, percent = 30, noData = -9999) -> np.ndarray:
    """Returns a modified inputArray where noLandslide values are randomly replaced with noData
    until landslide values make up percent % of all elements in inputArray if the percentage of
    landslides is too low, else it randomly replaces landslides with noData until percent % of all
    elements in inputArray are landslide"""
    lsCount = np.count_nonzero(inputArray == landslide)
    nonLsCount = np.count_nonzero(inputArray == noLandslide)
    lsPercent = 100 / (lsCount + nonLsCount) * lsCount
    percentDifference = percent - lsPercent
    elementCountToModify = (lsCount + nonLsCount) * abs(percentDifference) / 100
    if percentDifference < 0: # too many landslides
        pass
    elif percentDifference > 0: # too few landslides
        print(f"{elementCountToModify = }")
    else:
        return inputArray

if __name__ == "__main__":
    import timeit
    import randomize
    trainlist, vallist = randomize.getRandomArrays(np.arange(900).reshape(30, 30), 100, noData=899)
    for train in trainlist:
        print(timeit.timeit("readyArray4calc(train)", globals=globals()))