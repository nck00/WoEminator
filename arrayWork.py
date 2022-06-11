import numpy as np

def readyArray4calc(inputArray: np.ndarray) -> np.ndarray:
    """Returns an array with each element not 0 or noData (-9999) replaced with 1.
    Used to convert the randomized Arrays into a better format for calculation.
    """
    inputArray[inputArray >= 1] = 1 # We expect each value > 1 to be a landslide
    return inputArray

def fillArrayWithRandomNoDataUntilPercent(inputArray: np.ndarray, landslide = 1, noLandslide = 0, percent = 30, noData = -9999, seed = 42) -> np.ndarray:
    """Returns a modified inputArray where noLandslide values are randomly replaced with noData
    until landslide values make up percent % of all elements in inputArray if the percentage of
    landslides is too low, else it randomly replaces landslides with noData until percent % of all
    elements in inputArray are landslides"""
    lsCount = np.count_nonzero(inputArray == landslide)
    nonLsCount = np.count_nonzero(inputArray == noLandslide)
    lsPercent = 100 / (lsCount + nonLsCount) * lsCount
    percentDifference = percent - lsPercent
    if percentDifference == 0: # precision landing
        return inputArray
    elif percentDifference < 0: # too many landslides -> add noData for landslide
        toReplace = landslide
        elementCountToModify = abs(nonLsCount - int(nonLsCount / ((100-percent) / 100 )) + lsCount)
    elif percentDifference > 0: # too few landslides  -> add noData for noLandslide
        toReplace = noLandslide
        elementCountToModify = abs(lsCount - int(lsCount / (percent / 100 )) + nonLsCount)
    rowCount, colCount = inputArray.shape
    np.random.seed(seed)
    while elementCountToModify:
        row = np.random.randint(0, rowCount)
        col = np.random.randint(0, colCount)
        if inputArray[row][col] == toReplace:
            inputArray[row][col] = noData
            elementCountToModify -= 1
    return inputArray

def fillWithNoDataKeepingValueDistribution(inputArray: np.ndarray, percent = 20, noData = -9999, seed = 42) -> np.ndarray:
    """Returns a modified inputArray where percent of all values in it are filled with noData, while
    keeping the original percentage distribution of the values. It will keep atleast one of each
    value in inputArray in the returned array.
    """
    values, counts = np.unique(inputArray, return_counts = True)
    if noData in values: # we don't care about noData
        index = np.where(values == noData)
        values = values[values != noData]
        counts = np.delete(counts, index)
    afterCounts = (counts * percent/100).astype("int")
    afterCounts[afterCounts == 0] = 1
    toReplace = counts - afterCounts
    indices = []
    for value in values:
        indice = np.where(inputArray == value)
        indices.append(indice) # indice[n][0] = x array; indice[n][1] = y array
    np.random.seed(seed)
    for i, value in enumerate(values):
        for replace in range(toReplace[i]):
            x = np.random.choice(indices[i])
            y = indices[0][1][np.where(x == indices[0][0])]
    
if __name__ == "__main__":
    import timeit
    import randomize
    trainlist, vallist = randomize.getRandomArrays(np.arange(900).reshape(30, 30), 100, noData=899)
    for train in trainlist:
        print(timeit.timeit("readyArray4calc(train)", globals=globals()))