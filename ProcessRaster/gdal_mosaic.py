from osgeo import gdal
import os
import glob
import math
from tqdm import tqdm
#获取影像的左上角和右下角坐标
def GetExtent(in_fn):
    ds=gdal.Open(in_fn)
    geotrans=list(ds.GetGeoTransform())
    xsize=ds.RasterXSize 
    ysize=ds.RasterYSize
    min_x=geotrans[0]
    max_y=geotrans[3]
    max_x=geotrans[0]+xsize*geotrans[1]
    min_y=geotrans[3]+ysize*geotrans[5]
    ds=None
    return min_x,max_y,max_x,min_y
path=r"F:\Liaodong\mosaic"
os.chdir(path)

#如果存在同名影像则先删除
if os.path.exists('mosaiced_image.tif'):
    os.remove('mosaiced_image.tif')
in_files=glob.glob("*.tif")
in_fn=in_files[0]

#获取待镶嵌栅格的最大最小的坐标值
min_x,max_y,max_x,min_y=GetExtent(in_fn)
for in_fn in in_files[1:]:
    minx,maxy,maxx,miny=GetExtent(in_fn)
    min_x=min(min_x,minx)
    min_y=min(min_y,miny)
    max_x=max(max_x,maxx)
    max_y=max(max_y,maxy)
    
#计算镶嵌后影像的行列号
in_ds=gdal.Open(in_files[0])
geotrans=list(in_ds.GetGeoTransform())
width=geotrans[1]
height=geotrans[5]

columns=math.ceil((max_x-min_x)/width)
rows=math.ceil((max_y-min_y)/(-height))
in_band=in_ds.GetRasterBand(1)

driver=gdal.GetDriverByName('GTiff')
out_ds=driver.Create('mosaiced_image.tif',columns,rows,1,in_band.DataType)
out_ds.SetProjection(in_ds.GetProjection())
geotrans[0]=min_x
geotrans[3]=max_y
out_ds.SetGeoTransform(geotrans)
out_band=out_ds.GetRasterBand(1)
#定义仿射逆变换
inv_geotrans=gdal.InvGeoTransform(geotrans)
#开始逐渐写入
for in_fn in tqdm(in_files):
    in_ds=gdal.Open(in_fn)
    in_gt=in_ds.GetGeoTransform()
    #仿射逆变换
    offset=gdal.ApplyGeoTransform(inv_geotrans,in_gt[0],in_gt[3])
    x,y=map(int,offset)
    print(x,y)
    trans=gdal.Transformer(in_ds,out_ds,[])#in_ds是源栅格，out_ds是目标栅格
    success,xyz=trans.TransformPoint(False,0,0)#计算in_ds中左上角像元对应out_ds中的行列号
    x,y,z=map(int,xyz)
    print(x,y,z)
    data=in_ds.GetRasterBand(1).ReadAsArray()
    out_band.WriteArray(data,x,y)#x，y是开始写入时左上角像元行列号
del in_ds,out_band,out_ds