from osgeo import gdal
import numpy as np

sen2 = gdal.Open(r"F:\DTHS2\2019.6S2\train_raster\T49RFM_20200512T030551_10m_C1.tif")
Mean=[]
Std=[]

for i in range(sen2.RasterCount):
    sen2_band=sen2.GetRasterBand(i+1)
    sen2_band_arry=sen2_band.ReadAsArray()
    Mean.append(np.mean(sen2_band_arry))
    Std.append(np.std(sen2_band_arry))
print(Mean)
print(Std)