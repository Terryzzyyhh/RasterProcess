from osgeo import gdal
import numpy as np
import glob
import os
from tqdm import tqdm
#文件夹下的波段个数要一致

def cal_mean_std(in_files):
    Mean = []
    Std = []

    for num in tqdm(range(bandnum)):
        big_arry =np.zeros(shape=(1,lenth))
        mean=0
        std=0
        for in_file in tqdm(in_files):
            img = gdal.Open(in_file)
            band=img.GetRasterBand(num+1)
            band_arry = band.ReadAsArray()
            band_arry_flatten=band_arry.flatten()
            big_arry=np.append(big_arry,band_arry_flatten)

        index=range(0,lenth)
        big_arry=np.delete(big_arry,index)
        mean = np.mean(big_arry)
        std = np.std(big_arry)
        Mean.append(mean)
        Std.append(std)
    return  Mean,Std

dir =r"D:\akesu_his"
os.chdir(dir)
in_files=glob.glob("*_his.tif")
tif=gdal.Open(in_files[0])
lenth= tif.RasterXSize*tif.RasterYSize
bandnum=tif.RasterCount#获取波段数
Mean,Std=cal_mean_std(in_files)

print("Mean:",Mean)
print("Std:",Std)