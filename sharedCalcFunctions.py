import math
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

def getClassArrayListAndTrueValue(rasterArray, classValues: list, noData=-9999) -> tuple:
    """
    Returns a tuple: 1. list with n arrays for n unique values in rasterArray and the trueValue.
    The return arrays will have trueValue where the class is present, falseValue elsewhere and
    -9999 for noData.
    By returning the trueValue we can use it later and not array.max() saving time.
    """
    classArrayList = []
    trueValue, falseValue = _getBoolValues(classValues)
    for classValue in classValues:
        classArray = rasterArray.copy()
        classArray[classArray == classValue] = trueValue
        classArray[classArray == noData] = -9999
        classArray[(classArray != -9999) & (classArray != trueValue)] = falseValue
        classArrayList.append(classArray)
    return (classArrayList, trueValue)

def _getBoolValues(values: np.ndarray) -> tuple:
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

def getClassCount(classArray, trueValue: int) -> int:
    """Returns the amount of pixels in a classArray that are inside the class.
    Gets called by init.
    """
    return np.count_nonzero(classArray == trueValue)

def getLandslideClassCount(lsArray, classArray, trueValue: int) -> int:
    """Returns the amount of pixels with landslide inside the class."""
    return (np.logical_and(lsArray == 1, classArray == trueValue)).sum()
