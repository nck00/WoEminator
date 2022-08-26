import numpy as np
from osgeo import gdal


def array2Raster(array: np.ndarray, maskRasterPath: str, outRasterPath: str, noData=-9999,
                 gdalType=gdal.GDT_Float32) -> str:
    """Returns outRasterPath, the path to the new .tif file.
    array is the numpy array you want to save as a .tif file
    maskRasterPath is an existing .tif file from which we take spatial information
    noData is the value in array that we treat as no Data in the resulting .tif file
    gdalType is the GDAL pixel data type to use for the resulting .tif"""
    maskRaster = gdal.Open(maskRasterPath)
    outRaster = gdal.GetDriverByName("Gtiff").Create(outRasterPath, maskRaster.RasterXSize, maskRaster.RasterYSize, 1,
                                                     gdalType)
    outRaster.SetProjection(maskRaster.GetProjection())
    outRaster.SetGeoTransform(maskRaster.GetGeoTransform())
    outRaster.GetRasterBand(1).SetNoDataValue(noData)
    outRaster.GetRasterBand(1).WriteArray(array)
    return outRasterPath


if __name__ == "__main__":
    from toArray import *
    array = vector2Array("testdata/landslides.shp", "testdata/AW3D30.tif", "number")
    maskRasterPath = "testdata/AW3D30.tif"
    array2Raster(array, maskRasterPath, "out.tif")
