from zipfile import ZipFile
import os
import sys
import multiprocessing
# import tifffile as tiff
# from skimage import io
from osgeo import gdal
import glob
import shutil
# import time
import re


class Sentinel_pre_com:
    """哨兵影像预处理，拼接"""

    def __init__(self, zip_dir, script_path, unzip_dir=None, resolution=10, process_dir=None, log=None):
        """
        :param zip_dir:
        :param unzip_dir:
        :param resolution:
        :param process_dir: 存放处理后文件的目录
        :log 存放log的路径
        """
        self.script_path = script_path
        self.zipdir = zip_dir
        self.unzip_dir = unzip_dir
        # 存放解压文件的目录必须为空
        self.resolution = resolution
        if process_dir is None:
            self.process_dir = os.path.join(self.zipdir, 'process_temp')
            if not os.path.exists(self.process_dir):
                os.mkdir(self.process_dir)
        else:
            self.process_dir = process_dir
            if not os.path.exists(self.process_dir):
                os.mkdir(self.process_dir)
        if log:
            self.log = log
        else:
            self.log = os.path.join(zip_dir, "log.txt")
        if self.unzip_dir is None:
            self.unzip_dir = os.path.join(self.zipdir, 'temp_unzip')

    def unzipfile(self):
        """
        输入zip所在文件目录和指定的解压目录
        解压下载的哨兵2zip文件到当前文件夹
        :return:
        """
        if os.path.exists(self.unzip_dir):
            shutil.rmtree(self.unzip_dir)
        os.mkdir(self.unzip_dir)
        # zipdir中的所有文件
        files = os.listdir(self.zipdir)
        # 找到zip格式文件
        zip_file_ge = filter(lambda x: x.endswith(".zip"), files)
        zip_files = [*zip_file_ge]
        if zip_files:
            for file in zip_files:
                file = os.path.join(self.zipdir, file)
                if os.path.isfile(file):
                    tounzip = ZipFile(file, "r")
                    print(f"解压文件: {file}")
                    tounzip.extractall(self.unzip_dir)
                    print(f"解压完成: {file}")
                    tounzip.close()
        else:
            assert False, "没有zip文件"

    def preprocess(self, safe_file):
        """
        使用多进程 调用sen2cor脚本处理哨兵影像
        """
        cmd = f"{self.script_path} --resolution={self.resolution} --output_dir {self.process_dir} {safe_file} "
        print("---------preprocess {}------------".format(safe_file))
        os.system(cmd)

    def combination_bands_jp2(self, out_dir=None, bands=[2, 3, 4, 8]):
        """
        波段融合
        out_file:输出文件
        bands：波段列表
        :return:
        """
        if out_dir is None:
            # print(self.zipdir)
            out_dir = os.path.join(self.zipdir, "processed_files")
            # print("out", out_dir)
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        bands_num = len(bands)  # 波段数
        file_names = os.listdir(self.process_dir)
        file_pathes = [os.path.join(self.process_dir, file_name) for file_name in file_names]
        print(file_pathes)
        # filepath类似E:\GDAL_docs\gdal_sentinel\process_temp\S2A_MSIL2A_20200518T032541_N9999_R018_T49SCA_20200721T011900.SAFE
        seperator = os.sep
        imgs = [
            file_path + f"{seperator}*{seperator}*{seperator}IMG_DATA{seperator}R{self.resolution}m" + os.sep + "*B0{}*"
            for file_path in file_pathes]

        for img in imgs:
            first_band = bands[0]
            print(img.format(first_band))
            try:
                first_band = glob.glob(img.format(first_band))[0]  # 文件路径
            except IndexError as e:
                print(f"Not found {img}".format(first_band))
                print(e)
                continue
            out_name = re.search(r"(.*)?B.*_(\d+m)", first_band.split(os.sep)[-1]).groups()
            out_name = "".join(out_name)
            out_name = out_name + '.tif'
            print("**********************combinating {}**********************".format(out_name))
            # print(first_band)
            # open first bands
            first_band_ds = gdal.Open(first_band)
            if first_band_ds:
                print("open successfully")
                driver = gdal.GetDriverByName("GTiff")

                out_path = os.path.join(out_dir, out_name)
                out = driver.Create(out_path, first_band_ds.RasterXSize, first_band_ds.RasterYSize, bands_num,
                                    gdal.GDT_Int16)
                out_first_band = out.GetRasterBand(1)
                out_first_band.WriteArray(first_band_ds.ReadAsArray())
                # iter 3, 4, 8 bands
                for band_index in range(1, bands_num):
                    # 根据band编号，找到对应band的图片文件。
                    res_path = glob.glob(img.format(bands[band_index]))[0]
                    band_ds = gdal.Open(res_path)
                    out_band = out.GetRasterBand(band_index + 1)
                    out_band.WriteArray(band_ds.ReadAsArray())
                out.SetProjection(first_band_ds.GetProjection())
                out.SetGeoTransform(first_band_ds.GetGeoTransform())
                out.FlushCache()
                print("**********************done {}**********************".format(out_name))

    def delete_temp_files(self):
        files = os.listdir(self.zipdir)
        # 找到zip格式文件
        zip_file_ge = filter(lambda x: x.endswith(".zip"), files)
        zip_files = [*zip_file_ge]
        out_dir = os.path.join(self.zipdir, "processed_files")

        if os.path.exists(out_dir):
            processed_files = os.listdir(out_dir)
            print(zip_files)
            if len(zip_files) == len(processed_files):
                print("delete temp zip")
                shutil.rmtree(self.unzip_dir)  # 删除解压的临时文件
                # print("delete preprocessed files")
                # shutil.rmtree(self.process_dir)  # 删除预处理后的临时文件
                print("------------delete done-------------------")
            else:
                print("number of zipfile != number of combinated files, would not delete files now")
        else:
            print("processed not complete, would not delete file now")


def main(zipdir, n_jobs=4):
    script = "C:\Sen2Cor-02.08.00-win64\L2A_Process.bat"
    sent = Sentinel_pre_com(zipdir, script_path=script)
    sent.unzipfile()  # 解压zip
    print(sent.unzip_dir)
    unzip_dir = sent.unzip_dir
    # if unzip_dir is None:
    #     unzip_dir = os.path.join(zipdir, "temp_unzip")
    process_files = os.listdir(unzip_dir)
    process_files = [os.path.join(unzip_dir, process_file) for process_file in process_files]
    print(process_files)
    print("----------------辐射定标和大气矫正............")
    # log = open(sent.log, 'a')
    pool = multiprocessing.Pool(n_jobs)
    pool.map(sent.preprocess, process_files)
    pool.close()
    pool.join()
    print("******************starting combinate bands*******************")
    # 默认bands=[2, 3, 4, 8]。融合10米分辨率条带
    sent.combination_bands_jp2()
    # log.close()
    sent.delete_temp_files() # 删除临时文件


if __name__ == '__main__':
    # zipdir = os.getcwd()  # 压缩文件所在目录。保证目录里只有sentinel影像的zip文件
    to_preprocessed_dirs = ["pishan_county", "qiemo_county", "ruoqiang_county", "manasi_county", "minfeng_county"]
    zipbasedir = r"E:\xinjiang\{}"
    for process_dir in to_preprocessed_dirs:
        zipdir = zipbasedir.format(process_dir)
        script = "E:\ZYH_work\Sentinel\Sen2Cor-02.08.00-win64\Sen2Cor-02.08.00-win64\L2A_Process.bat"
        sent = Sentinel_pre_com(zipdir, script_path=script)
        sent.unzipfile()  # 解压zip
        print(sent.unzip_dir)
        unzip_dir = sent.unzip_dir
        process_files = os.listdir(unzip_dir)
        process_files = [os.path.join(unzip_dir, process_file) for process_file in process_files]
        print(process_files)
        print("----------------辐射定标和大气矫正............")
        # log = open(sent.log, 'a')
        pool = multiprocessing.Pool(5)
        pool.map(sent.preprocess, process_files)
        pool.close()
        pool.join()
        print("******************starting combinate bands*******************")
        # 默认bands=[2, 3, 4, 8]。融合10米分辨率条带
        sent.combination_bands_jp2()
        # log.close()
        sent.delete_temp_files()

