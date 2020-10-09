from osgeo import gdal
import tifffile as tif
import numpy as np
import glob
import os
import shutil
from tqdm import tqdm
import multiprocessing

def convert(file):
    #D:\Agriculture\Project\xinjiang\bohu_county\processed_files\T45TVG_20190812T050701_10m.tif
    ds_gdal = gdal.Open(file)
    ds = tif.imread(file)

    print(ds.shape)
    # print(ds.max())

    b = ds[:, :, 0]
    g = ds[:, :, 1]
    r = ds[:, :, 2]
    nir = ds[:,:,3]

    # nir = ds[:, :, 3]
    b = b.astype(np.float32)
    g = g.astype(np.float32)
    r = r.astype(np.float32)
    nir=nir.astype(np.float32)

    # out[...,2] = i,"D:\Agriculture\Project\xinjiang\october\T45TVG_20190812T050701_10m_hsi.tif"
    save = file.replace('.tif', '') + "_his.tif"
    
    driver = gdal.GetDriverByName("GTiff")
    out = driver.Create(save, ds_gdal.RasterXSize, ds_gdal.RasterYSize, 4, gdal.GDT_Float32)

    # out = np.zeros(shape=(ds.shape[0], ds.shape[1], 3))
    i = (r + g + b) / 3

    s = 1 - 3 * np.minimum(np.minimum(r, b), g) / (r + g + b + 1e-7)

    tem0 = ((r - g) + (r - b)) / 2
    # dd = r -g
    # dd = dd.astype(np.float32)
    # print((r-g)**2)

    tem1 = np.sqrt((r - g) ** 2 + (r - b) * (g - b))
    # print(tem1)
    tem = tem0 / (tem1 + 1e-7)
    theta = np.arccos(tem)
    # G>=B h=θ
    # g<b h=2pi - θ
    h = theta.copy()

    h[g < b] = 2 * np.pi - theta[g < b]
    h = h / (2*np.pi)
    h[s == 0] = 0
    print(h)

    ndvi=(nir-r)/(nir+r+1e-7)

    h_band = out.GetRasterBand(1)
    h_band.WriteArray(h)
    s_band = out.GetRasterBand(2)
    s_band.WriteArray(s)
    i_band = out.GetRasterBand(3)
    i_band.WriteArray(i)
    ndvi_band = out.GetRasterBand(4)
    ndvi_band.WriteArray(ndvi)

    out.SetProjection(ds_gdal.GetProjection())
    out.SetGeoTransform(ds_gdal.GetGeoTransform())
    out.FlushCache()

    # tif.imsave(save, out)
def pro(dir):
    s2 = os.getcwd()
    os.chdir(s2+"\\"+dir)
    filenames = glob.glob("*_10m.tif")
    for file in tqdm(filenames):
        convert(s2+"\\"+dir+"\\"+file)

if __name__ == '__main__':
    s2 = os.getcwd()
    dirs = os.listdir(s2)
    print(dirs[2:])
    pool = multiprocessing.Pool(2)
    pool.map(pro,dirs[2:])
    pool.close()
    pool.join()