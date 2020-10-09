from osgeo import gdal
import numpy as np

sen2 = gdal.Open(r"F:\整理\20200727-1-1.tif")
Mean=[]
Std=[]

for i in range(sen2.RasterCount):
    sen2_band=sen2.GetRasterBand(i+1)
    sen2_band_arry=sen2_band.ReadAsArray()
    Mean.append(np.mean(sen2_band_arry))
    Std.append(np.std(sen2_band_arry))
print(Mean)
print(Std)
