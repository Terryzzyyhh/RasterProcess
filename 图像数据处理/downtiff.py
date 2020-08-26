"""
目标：提供一个函数能够从网上下载资源
输入：
    url列表
    保存路径
输出：
    保存到指定路径中的文件
要求：
    能够实现下载过程，即从0%到100%可视化
"""
# =====================================================
import urllib.request
import os
import sys


def download_and_extract(filepath, save_dir):
    """根据给定的URL地址下载文件
    Parameter:
        filepath: list 文件的URL路径地址
        save_dir: str  保存路径
    Return:
        None
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    for url, index in zip(filepath, range(len(filepath))):
        filename = url.split('/')[-1]
        save_path = os.path.join(save_dir, filename)
        urllib.request.urlretrieve(url, save_path)
        sys.stdout.write('\r>> Downloading %.1f%%' % (float(index + 1) / float(len(filepath)) * 100.0))
        sys.stdout.flush()
    print('\nSuccessfully downloaded')


def _get_file_urls(file_url_txt):
    """根据URL路径txt文件，获取URL地址列表
    Parameter:
        file_url_txt: str  txt文件本地路径
    Return:
        filepath: list  URL列表
    """
    filepath = []
    file = open(file_url_txt, 'r')
    for line in file.readlines():
        line = line.strip()
        filepath.append(line)
    file.close()
    return filepath


if __name__ == '__main__':
    file_url_txt = r'F:\影像下载\4943586735-download.txt'
    save_dir = 'F:\影像下载\洞庭湖哨兵一号'
    filepath = _get_file_urls(file_url_txt)
    download_and_extract(filepath, save_dir)