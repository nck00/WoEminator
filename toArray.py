from osgeo import gdal, ogr
import numpy as np


def vector2Array(vectorPath: str, maskRasterPath: str, burnField: str, noData=-9999):
    # TODO: Fix losing small polygons (ALL_TOUCHED broken?)
    """Returns an array of the vector at vectorPath inside the maskRaster a maskRastPath.
    burnField should be unique integer for each Feauture > 0.
    0 means there is no shape in that location. noData indicates that it is outside the mask
    raster (Array has to be rectangular).
    First we create a temporary Raster in memory and then return its Array.
    """
    maskHandle = gdal.Open(maskRasterPath, gdal.GA_ReadOnly)
    vector = ogr.Open(vectorPath)
    vectorLayer = vector.GetLayer()
    xRes = maskHandle.RasterXSize
    yRes = maskHandle.RasterYSize
    xMin, xSize, _, yMax, _, ySize = maskHandle.GetGeoTransform()  # _ are always 0
    tmpRaster = gdal.GetDriverByName("MEM").Create("", xRes, yRes, 1, gdal.GDT_Int16)
    # tmpRaster = gdal.GetDriverByName("GTiff").Create("testls.tif", xRes, yRes, gdal.GDT_Int16)
    # If we write to a file it will lack the the Projection Information, but it is not
    # necessary for calculation with array data. If necessary use:
    # tmpRaster.SetProjection(maskHandle.GetProjection())
    tmpRaster.SetGeoTransform((xMin, xSize, 0, yMax, 0, ySize))
    band = tmpRaster.GetRasterBand(1)
    band.SetNoDataValue(noData)
    # gdal.RasterizeLayer(tmpRaster, [1], vectorLayer, options = [f"ATTRIBUTE={burnField}", "outputType=gdal.GDT_Int16", "ALL_TOUCHED=TRUE"])
    gdal.RasterizeLayer(tmpRaster, [1], vectorLayer, options=[f"ATTRIBUTE={burnField}"])
    return band.ReadAsArray()


def raster2Array(rasterPath: str, bandNr=1) -> np.ndarray:
    """Returns a Numpy Array of the raster at rasterPath of band bandNr."""
    handle = gdal.Open(rasterPath, gdal.GA_ReadOnly)
    return handle.GetRasterBand(bandNr).ReadAsArray()


if __name__ == "__main__":
    import time

    t1 = time.perf_counter()
    x = vector2Array("testdata/landslides.shp", "testdata/AW3D30.tif", "number")
    t2 = time.perf_counter()
    print(t2 - t1)
