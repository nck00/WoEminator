import numpy as np
from osgeo import gdal


def array2Raster(array: np.ndarray, maskRasterPath: str, outRasterPath: str, noData=-9999,
                 gdalType=gdal.GDT_Float32) -> str:
    """Returns true if the raster file was correctly written to outPath."""
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
