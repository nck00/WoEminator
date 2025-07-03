import numpy as np
from sharedCalcFunctions import *


class FR:
    """After calling FR(raster, landslides, noData) FR.resultsTable contains the results of the
    calculation (see getResultsTableFR).
    """

    def __init__(self, rasterArray: np.ndarray, lsArray: np.ndarray, noData=-9999):
        lsTotalCount = getLandslideTotalCount(
            lsArray, noData, 0
        )  # 0 = noLandslideValue
        totalCount = getTotalCount(rasterArray, noData)
        totalStableCount = totalCount - lsTotalCount
        classValues = getClassValues(rasterArray, noData)
        self.resultsTable = self.getResultsTableFR(len(classValues))
        for i, classValue in enumerate(classValues):
            classArray = getClassArray(rasterArray, classValue, noData)
            self.resultsTable["classCount"][i] = getClassCount(classArray)
            self.resultsTable["lsClassCount"][i] = getLandslideClassCount(
                lsArray, classArray
            )
            self.resultsTable["stableClassCount"][i] = (
                self.resultsTable["classCount"][i]
                - self.resultsTable["lsClassCount"][i]
            )
            self.resultsTable["lsOutClassCount"][i] = (
                lsTotalCount - self.resultsTable["lsClassCount"][i]
            )
            self.resultsTable["stableOutClassCount"][i] = (
                totalStableCount - self.resultsTable["stableClassCount"][i]
            )
            self.resultsTable["classFrequencyRatio"][i] = self.getFrequencyRatio(
                self.resultsTable["lsClassCount"][i],
                self.resultsTable["classCount"][i],
                lsTotalCount,
                totalCount,
            )

    def getResultsTableFR(self, classArrayCount: int) -> np.ndarray:
        """Returns a Numpy Array, to be filled with the calculation results.
        The size of the of the array is based on the number of classes in the input Layer.
        """
        return np.zeros(
            shape=(classArrayCount,),
            dtype=[
                ("classValue", "f"),
                ("classCount", "i"),
                ("lsClassCount", "i"),
                ("stableClassCount", "i"),
                ("lsOutClassCount", "i"),
                ("stableOutClassCount", "i"),
                ("classFrequencyRatio", "f"),
            ],
        )

    def getFrequencyRatio(
        self, lsClassCount: int, classCount: int, lsTotalCount: int, totalCount: int
    ) -> float:
        """
        Calculates and returns the Frequncy Ratio for a class of raster.
             Landslide Pixels in Class / Total Pixels in class
        FR = -------------------------------------------------
             Total landslide Pixels / Total Pixels
        """
        return (lsClassCount / classCount) / (lsTotalCount / totalCount)


if __name__ == "__main__":
    import time
    import toArray
    import randomize
    import arrayWork

    t1 = time.perf_counter()
    lsArray = toArray.vector2Array(
        "testdata/landslides.shp", "testdata/AW3D30.tif", "number"
    )
    rasterArray = toArray.raster2Array("testdata/geology.tif")
    trainList, valList = randomize.getRandomArrays(lsArray, 1, 100)
    trainReadyForCalc = [*map(arrayWork.readyArray4calc, trainList)]
    print(trainReadyForCalc[0].all() == lsArray.all())
    for train in trainReadyForCalc:
        FRr = FR(rasterArray, train, -9999)
        print(FRr.resultsTable["classFrequencyRatio"])
    t2 = time.perf_counter()
    print(t2 - t1)
