import math
import numpy as np
from sharedCalcFunctions import *

class WoE:
    """After calling WoE(raster, landslides, noData) WoE.resultsTable contains the results of the
    calculation (see getResultsTableWoE).
    """
    def __init__(self, rasterArray: np.ndarray, lsArray: np.ndarray, noData=-9999):
        lsTotalCount = getLandslideTotalCount(lsArray, noData, 0)  # 0 = noLandslideValue
        totalCount = getTotalCount(rasterArray, noData)
        totalStableCount = totalCount - lsTotalCount
        classValues = getClassValues(rasterArray, noData)
        classArrayList, trueValue = getClassArrayListAndTrueValue(
            rasterArray, classValues, noData
        )
        self.resultsTable = self.getResultsTableWoE(len(classArrayList))
        for i, classArray in enumerate(classArrayList):
            self.resultsTable["classValue"][i] = classValues[i]
            self.resultsTable["classCount"][i] = getClassCount(classArray, trueValue)
            self.resultsTable["lsClassCount"][i] = getLandslideClassCount(
                lsArray, classArray, trueValue
            )
            self.resultsTable["stableClassCount"][i] = (
                self.resultsTable["classCount"][i] - self.resultsTable["lsClassCount"][i]
            )
            self.resultsTable["classPositiveWeight"][i] = self.getPositiveWeight(
                self.resultsTable["lsClassCount"][i],
                lsTotalCount,
                self.resultsTable["stableClassCount"][i],
                totalStableCount,
            )
            self.resultsTable["lsOutClassCount"][i] = (
                lsTotalCount - self.resultsTable["lsClassCount"][i]
            )
            self.resultsTable["stableOutClassCount"][i] = (
                totalStableCount - self.resultsTable["stableClassCount"][i]
            )
            self.resultsTable["classNegativeWeight"][i] = self.getNegativeWeight(
                self.resultsTable["lsOutClassCount"][i],
                lsTotalCount,
                self.resultsTable["stableOutClassCount"][i],
                totalStableCount,
            )
            self.resultsTable["classContrast"][i] = (
                self.resultsTable["classPositiveWeight"][i]
                - self.resultsTable["classNegativeWeight"][i]
            )
            self.resultsTable["classPositiveVariance"][i] = self.getClassPositiveVariance(
                self.resultsTable["lsClassCount"][i],
                self.resultsTable["stableClassCount"][i],
            )
            self.resultsTable["classNegativeVariance"][i] = self.getClassNegativeVariance(
                self.resultsTable["lsOutClassCount"][i],
                self.resultsTable["stableOutClassCount"][i],
            )
        totalNegativeWeight = sum(self.resultsTable["classNegativeWeight"])
        totalNegativeVariance = sum(self.resultsTable["classNegativeVariance"])
        for i in range(len(classArrayList)):
            self.resultsTable["classWeight"][i] = self.getWeight(
                self.resultsTable["classPositiveWeight"][i],
                totalNegativeWeight,
                self.resultsTable["classNegativeWeight"][i],
            )
            self.resultsTable["classVariance"][i] = self.getVariance(
                self.resultsTable["classPositiveVariance"][i],
                totalNegativeVariance,
                self.resultsTable["classNegativeVariance"][i],
            )

    def getResultsTableWoE(self, classArrayCount: int) -> np.ndarray:
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
                ("classPositiveWeight", "f"),
                ("classNegativeWeight", "f"),
                ("lsOutClassCount", "i"),
                ("stableOutClassCount", "i"),
                ("classContrast", "f"),
                ("classPositiveVariance", "f"),
                ("classNegativeVariance", "f"),
                ("classWeight", "f"),
                ("classVariance", "f"),
            ],
        )

    def getPositiveWeight(
        self,
        lsClassCount: int,
        lsTotalCount: int,
        stableClassCount: int,
        totalStableCount: int,
    ) -> float:
        """Returns the positive Weight of a class.
        W⁺ = ln(P(Class | Landslide) / P(Class | no Landslide))
        P(Class | Landslide): P (Class ∩ Landslide) / P(Landslide)
        P(Class | no Landslide): P (Class ∩ no Landslide) / P(no Landslide)
        """
        if lsClassCount:
            return math.log((lsClassCount / lsTotalCount) / (stableClassCount / totalStableCount))
        else: # no landslides in class
            return 0

    def getNegativeWeight(
        self,
        lsOutClassCount: int,
        lsTotalCount: int,
        stableOutClassCount: int,
        totalStableCount: int,
    ) -> float:
        """Returns the negative Weight of a class.
        W⁻ = ln(P(not Class | Landslide) / P(not Class | no Landslide))
        P(not Class | Landslide): P (not Class ∩ Landslide) / P(Landslide)
        P(not Class | no Landslide): P (not Class ∩ no Landslide) / P(no Landslide)
        """
        return math.log((lsOutClassCount / lsTotalCount) / (stableOutClassCount / totalStableCount))

    def getClassPositiveVariance(self, lsClassCount: int, stableClassCount: int) -> float:
        """Returns the Variance of the positive Weight.
        σ²(W⁺) = 1 / (Class ∩ Landslide) + 1 / (Class ∩ no Landslide)
        """
        if lsClassCount:
            return 1 / lsClassCount + 1 / stableClassCount
        else: # no landslides in class
            return 0

    def getClassNegativeVariance(self, lsOutClassCount: int, stableOutClassCount: int) -> float:
        """Returns the Variance of the positive Weight.
        σ²(W⁻) = 1 / (not Class ∩ Landslide) + 1 / (not Class ∩ no Landslide)
        """
        return 1 / lsOutClassCount + 1 / stableOutClassCount

    def getWeight(
        self,
        positiveClassWeight: float,
        totalNegativeWeight: float,
        negativeClassWeight: float,
    ) -> float:
        """Returns the Weight of Evidence for a class.
        W = W⁺ + ΣW⁻ - W⁻
        W⁺: Positive Weight of the class
        ΣW⁻: Sum of all negatie Weights
        W⁻: Negative Weight of the class
        """
        return positiveClassWeight + totalNegativeWeight - negativeClassWeight

    def getVariance(
        self,
        positiveClassVariance: float,
        totalNegativeVariance: float,
        negativeClassVariance: float,
    ) -> float:
        """Returns the Variance for a class.
        σ² = σ²(W⁺) + Σσ²(W⁻) - σ²(W⁻)
        σ²(W⁺): Positive Variance of the class
        Σσ²(W⁻): Sum of all negative Variances
        σ²(W⁻): Negative Variance of the class
        """
        return positiveClassVariance + totalNegativeVariance - negativeClassVariance


if __name__ == "__main__":
    import time
    import toArray
    import randomize
    import arrayWork
    t1 = time.perf_counter()
    lsArray = toArray.vector2Array("testdata/landslides.shp", "testdata/AW3D30.tif", "number")
    rasterArray = toArray.raster2Array("testdata/geology.tif")
    trainList, valList = randomize.getRandomArrays(lsArray, 1, 100)
    trainReadyForCalc = [*map(arrayWork.readyArray4calc, trainList)]
    print(trainReadyForCalc[0].all() == lsArray.all())
    for train in trainReadyForCalc:
        WoEr = WoE(rasterArray, train, -9999)
        print(WoEr.resultsTable["classWeight"])
    t2 = time.perf_counter()
    print(t2 - t1)