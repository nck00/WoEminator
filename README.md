# WoEminator

A few scripts to apply Weights of Evidence (and Frequency Ratio) to spatial data (landslides).

Comes with basic functions to ready your .shp and .tif files for calculation.

If you are looking for a more complete solution with a GUI you might like [LSAT](https://github.com/BGR-EGHA/LSAT).

# Recipes

A small collection of snippets to get you started (and for me to reuse).

## Convert to Array

### From Raster to Array

Default band = 1. If you want to use another band specify it as a second parameter of raster2Array.
The array will have the type of the raster.

```python
from toArray import raster2Array

raster_path = "path_to_raster"
array_raster = raster2Array(raster_path)
```

### From Shapefile to Array

Default no data = -9999. If you want to use another value specify it as the last parameter of vector2Array.
For good compability the value to write into the array should be an unique integer and >= 1.
The array type is always int16.

```python
from toArray import vector2Array

vector_path = "path_to_vector"
mask_raster_path = "path_to_mask_raster"
burn_field = "attribute_from_FAT_to_write_into_array"
array_vector = vector2Array(vector_path, mask_raster_path, burn_field)
```

## Convert to Raster

Default no data = -9999. If you want to use another value specify it as the second to last parameter of array2Raster.
Default raster type = gdal.GDT_Float32. If you want to use another type specify it as the last parameter of array2Raster.

```python
from toRaster import array2Raster

array = numpy_array
mask_raster_path = "path_to_mask_raster"
out_raster_path = "path_to_output_raster"
out_raster = array2Raster(array, mask_raster_path, out_raster_path)
```

## Full WoE Workflow - From gis files to averaged Weights raster
Uses all default values to create an averaged weights raster out of 50 subsamples of the training array and an input raster file.

```python
from arrayWork import readyArray4calc, replaceValuesInArray
import numpy as np
from randomize import getRandomArrays
from toArray import raster2Array, vector2Array
from toRaster import array2Raster
from woe import WoE

landslides_file = "path_to_vector"
attribute_to_burn_in = "attribute"
raster_file = r"path_to_raster"
output_file = "path_to_output_raster"

raster_array = raster2Array(raster_file)
ls_array = vector2Array(landslides_file, raster_file, attribute_to_burn_in)

ls_train_arrays, _ = getRandomArrays(ls_array, 50)
ls_train_arrays = [readyArray4calc(ls_train_array) for ls_train_array in ls_train_arrays]

weights = []
for ls_train_array in ls_train_arrays:
    tmp = WoE(raster_array, ls_train_array)
    weights.append(tmp.resultsTable["classWeight"])
weights_average = np.array(weights).mean(axis=0)

weights_array = replaceValuesInArray(raster_array, tmp.resultsTable["classValue"], weights_average)

array2Raster(weights_array, raster_file, output_file)
```
