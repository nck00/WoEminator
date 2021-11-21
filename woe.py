import math
import numpy as np

class WoE:
    """After calling WoE(raster, landslides, noData) WoE.resultsTable contains the results of the
    calculation (see getResultsTableWoE).
    """
    # TODO simplify some function calls e.g. Variance
    # TODO check heatmap
    def __init__(self, rasterArray: np.ndarray, lsArray: np.ndarray, noData=-9999):
        lsTotalCount = self.getLandslideTotalCount(lsArray, noData, 0)  # 0 = noLandslideValue
        totalCount = self.getTotalCount(rasterArray, noData)
        totalStableCount = totalCount - lsTotalCount
        classValues = self.getClassValues(rasterArray, noData)
        classArrayList, trueValue = self.getClassArrayListAndTrueValue(
            rasterArray, classValues, noData
        )
        self.resultsTable = self.getResultsTableWoE(len(classArrayList))
        for i, classArray in enumerate(classArrayList):
            self.resultsTable["classValue"][i] = classValues[i]
            self.resultsTable["classCount"][i] = self.getClassCount(classArray, trueValue)
            self.resultsTable["lsClassCount"][i] = self.getLandslideClassCount(
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

    def getLandslideTotalCount(self, lsArray: np.ndarray, noData: int, nols: int) -> int:
        """Returns the total amount of landslidepixels.
        Gets called by init
        Expects everything besides nols and noData to be a landslide pixel.
        """
        return ((lsArray != noData) & (lsArray != nols)).sum()

    def getTotalCount(self, rasterArray, noData: int) -> int:
        """Returns the total amount of pixel in raster excluding noData.
        Gets called by init.
        """
        return np.count_nonzero(rasterArray != noData)

    def getClassValues(self, rasterArray: np.ndarray, noData) -> np.ndarray:
        """Returns the"""
        classValues = np.unique(rasterArray)
        # we dont care about noData
        if noData in classValues:
            classValues = classValues[classValues != noData]
        return classValues

    def getClassArrayListAndTrueValue(self, rasterArray, classValues: list, noData=-9999) -> tuple:
        """
        Returns a tuple: 1. list with n arrays for n unique values in rasterArray and the trueValue.
        The return arrays will have trueValue where the class is present, falseValue elsewhere and
        -9999 for noData.
        By returning the trueValue we can use it later and not array.max() saving time.
        """
        classArrayList = list()
        trueValue, falseValue = self._getBoolValues(classValues)
        for classValue in classValues:
            classArray = rasterArray.copy()
            classArray[classArray == classValue] = trueValue
            classArray[classArray == noData] = -9999
            classArray[(classArray != -9999) & (classArray != trueValue)] = falseValue
            classArrayList.append(classArray)
        return (classArrayList, trueValue)

    def _getBoolValues(self, values: np.ndarray) -> tuple:
        """Returns a tuple of two integers representing presence and absence of a class.
        Gets called by getClassArrayList.
        If 1 and 0 is not in values we use 1 to indicate the presence of a specific class else use
        max + 1. If 0 and 1 not in values we use 0 to indicate lack of the class, else use min - 1.
        """
        if 1 not in values and 0 not in values:
            trueValue = 1
            falseValue = 0
        else:
            trueValue = int(values.max()) + 1
            falseValue = int(values.min()) - 1
        return (trueValue, falseValue)

    def getResultsTableWoE(self, classArrayCount: int) -> np.ndarray:
        """Returns a Numpy Array, to be filled with the calculation results.
        The size of the of the array is based on the number of classes in the input Layer
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

    def getClassCount(self, classArray, trueValue: int) -> int:
        """Returns the amount of pixels in a classArray that are inside the class.
        Gets called by init.
        """
        return np.count_nonzero(classArray == trueValue)

    def getLandslideClassCount(self, lsArray, classArray, trueValue: int) -> int:
        """Returns the amount of pixels with landslide inside the class."""
        return (np.logical_and(lsArray == 1, classArray == trueValue)).sum()

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
        # TODO: Handle 0 values
        return math.log((lsClassCount / lsTotalCount) / (stableClassCount / totalStableCount))

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
        # TODO: Handle 0 values
        return math.log((lsOutClassCount / lsTotalCount) / (stableOutClassCount / totalStableCount))

    def getClassPositiveVariance(self, lsClassCount: int, stableClassCount: int) -> float:
        """Returns the Variance of the positive Weight.
        σ²(W⁺) = 1 / (Class ∩ Landslide) + 1 / (Class ∩ no Landslide)
        """
        return 1 / lsClassCount + 1 / stableClassCount

    def getClassNegativeVariance(self, lsOutClassCount: int, stableOutClassCount: int) -> float:
        """Returns the Variance of the positive Weight.
        σ²(W⁻) = 1 / (Class ∩ Landslide) + 1 / (Class ∩ no Landslide)
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
    rasterArray = toArray.raster2Array("testdata/Geology.tif")
    trainList, valList = randomize.getRandomArrays(lsArray, 100)
    trainReadyForCalc = [*map(arrayWork.readyArray4calc, trainList)]
    # for train in trainReadyForCalc:
        # WoEr = WoE(rasterArray, train, -9999)
        # print(WoEr.resultsTable["classWeight"])
    t2 = time.perf_counter()
    print(t2 - t1)