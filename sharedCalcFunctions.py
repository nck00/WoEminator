import numpy as np

# Basic Functions used by both WoE and FR.


def getLandslideTotalCount(lsArray: np.ndarray, noData: int, nols: int) -> int:
    """Returns the total amount of landslidepixels.
    Gets called by init
    Expects everything besides nols and noData to be a landslide pixel.
    """
    return ((lsArray != noData) & (lsArray != nols)).sum()


def getTotalCount(rasterArray, noData: int) -> int:
    """Returns the total amount of pixel in raster excluding noData.
    Gets called by init.
    """
    return np.count_nonzero(rasterArray != noData)


def getClassValues(rasterArray: np.ndarray, noData) -> np.ndarray:
    """Returns a numpy array with unique values in rasterArray, discarding noData"""
    classValues = np.unique(rasterArray)
    # we dont care about noData
    if noData in classValues:
        classValues = classValues[classValues != noData]
    return classValues


def getClassArray(rasterArray, classValue: float, noData=-9999) -> np.ndarray:
    """
    Returns a numpy array based on rasterArray.
    The return array will have 1 "trueValue" where classValue is present,
    0 "falseValue" elsewhere and -9999 for noData.
    """
    classArray = rasterArray.copy()
    conditions = [classArray == classValue, classArray == noData]
    choices = [1, -9999]
    classArray = np.select(conditions, choices, 0)
    return classArray


def getClassCount(classArray, trueValue=1) -> int:
    """Returns the amount of pixels in a classArray that are inside the class.
    Gets called by init.
    """
    return np.count_nonzero(classArray == trueValue)


def getLandslideClassCount(lsArray, classArray, trueValue=1) -> int:
    """Returns the amount of pixels with landslide inside the class."""
    return (np.logical_and(lsArray == 1, classArray == trueValue)).sum()
