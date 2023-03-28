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

def getClassArrayList(rasterArray, classValues: list, noData=-9999) -> list:
    """
    Returns a list with n arrays for n unique values in rasterArray.
    The return arrays will have 1 "trueValue" where the class is present, 0 "falseValue" elsewhere and
    -9999 for noData.
    """
    classArrayList = []
    for classValue in classValues:
        classArray = rasterArray.copy()
        conditions = [classArray == classValue, classArray == noData]
        choices = [1, -9999]
        classArray = np.select(conditions, choices, 0)
        classArrayList.append(classArray)
    return classArrayList

def getClassCount(classArray, trueValue=1) -> int:
    """Returns the amount of pixels in a classArray that are inside the class.
    Gets called by init.
    """
    return np.count_nonzero(classArray == trueValue)

def getLandslideClassCount(lsArray, classArray, trueValue=1) -> int:
    """Returns the amount of pixels with landslide inside the class."""
    return (np.logical_and(lsArray == 1, classArray == trueValue)).sum()
