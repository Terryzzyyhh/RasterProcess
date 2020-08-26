from osgeo import gdal_array, gdal
import numpy as np

img1 = gdal.Open("E:\ZYH_work\GF3_SAY_FSII_020842_E112.3_N28.5_20200725_L2_HH_L20004949931.tiff")
img2 = gdal.Open("E:\ZYH_work\GF3_SAY_FSII_020842_E112.3_N28.5_20200725_L2_HV_L20004949931.tiff")
prototype = img1
HH = img1.ReadAsArray()
HV = img2.ReadAsArray()
HH=HH.astype(float)
HV=HV.astype(float)

width = img1.RasterXSize
height = img1.RasterYSize
geo = img1.GetGeoTransform()
proj = img1.GetProjection()

HHrHV = (HV+HH)/ (HV-HH+1.1e-8)

driver = gdal.GetDriverByName("GTiff")
tods = driver.Create("E:\LayerStack.tif",width,height,3,gdal.GDT_Float64,options=["INTERLEAVE=PIXEL"])
tods.SetGeoTransform(geo)
tods.SetProjection(proj)

band1 = tods.GetRasterBand(1)
band1.WriteArray(HH)

band2 = tods.GetRasterBand(2)
band2.WriteArray(HV)

band3 = tods.GetRasterBand(3)
band3.WriteArray(HHrHV)




