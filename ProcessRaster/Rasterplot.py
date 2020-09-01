import rasterio
from matplotlib import pyplot
from rasterio.plot import show

src = rasterio.open(r"E:\xinjiang\kelamayi_s2\proccessed_files\T45TUK_20200710T051651_10m.tif")
'''pyplot.imshow(src.read(1), cmap='CMRmap')
pyplot.show()'''


show(src.read([1,2,3]),transform=src.transform)
