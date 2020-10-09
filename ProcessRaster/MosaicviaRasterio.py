import rasterio
from rasterio.merge import merge
import glob
import os
#"E:\xinjiang\kelamayi_s2\proccessed_files"
dir =r"F:\shaya_t_l\raster\阿克苏市"
os.chdir(dir)

#如果存在同名影像则先删除
if os.path.exists('mosaiced_image.tif'):
    os.remove('mosaiced_image.tif')
out_fp=dir+"\\"+"mosaiced_image.tif"

in_files=glob.glob("*_his_prj.tif")
src_files_to_mosaic = []
for in_file in in_files:
    imgpath=dir+"\\"+in_file
    src = rasterio.open(imgpath)
    src_files_to_mosaic.append(src)

mosaic, out_trans = merge(src_files_to_mosaic)

with rasterio.open(dir+"\\"+in_files[0]) as src:
    out_meta = src.meta.copy()

out_meta.update({"driver": "GTiff",
                 "height": mosaic.shape[1],
                 "width": mosaic.shape[2],
                 "transform": out_trans})
with rasterio.open(out_fp, "w", **out_meta) as dest:
    dest.write(mosaic)