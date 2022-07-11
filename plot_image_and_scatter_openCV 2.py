# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 11:08:35 2015

@author: George
"""


from __future__ import (absolute_import, division,print_function, unicode_literals)
from future.builtins import (bytes, dict, int, list, object, range, str, ascii, chr, hex, input, next, oct, open, pow, round, super, filter, map, zip)
import cv2
import matplotlib.pyplot as plt
#import matplotlib.image as mpimg
import numpy as np
import win32com.client
from win32com.client import constants

imageName  = 'J:\\WORK\\STORM_After-Cellights-and-Calcium-Imaging\\COS-CellLights-Red_ER\\150717\\150717_cos_celllights-er-rfp_5umcal520_1umip3_1umegta_uv-flash-ER_before_calcium-imaging_average.tif'
#imageName  = 'J:\\WORK\\STORM_After-Cellights-and-Calcium-Imaging\\COS-CellLights-Red_ER\\150717\\150717_cos_celllights-er-rfp_5umcal520_1umip3_1umegta_uv-flash-ER_before_calcium-imaging_average_divided-by-low-pass.tif'
puffFileName = 'J:\\WORK\\STORM_After-Cellights-and-Calcium-Imaging\\COS-CellLights-Red_ER\\150717\\150717_cos_celllights-er-rfp_5umcal520_1umip3_1umegta_uv-flash-calcium-imaging_FLIKA.xlsx'
STORMFileName = 'J:\\WORK\\STORM_After-Cellights-and-Calcium-Imaging\\COS-CellLights-Red_ER\\150717\\150717_Cos_STORM_IP3R1-NTerm-A405-A647_test2_filtered-5in100.txt'

scaleFactor = 2 ##for FLIKA performed with pixel bining
scaleFactor2 = 160  ##160 nm / pixel

image = cv2.imread(imageName)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
implot = plt.imshow(gray_image, cmap=plt.get_cmap('hot'), interpolation='nearest', vmin=0, vmax=1)

###################extract puff coordinates##########################################
excel = win32com.client.Dispatch("Excel.Application")
#excel.Visible = True
workbook = excel.Workbooks.Open(puffFileName)
sheet = workbook.Worksheets('Puff Data')

header=np.array(sheet.Rows(1).Value[0])
nCols=np.max(np.argwhere(header.astype(np.bool)))+1
nPuffs=np.max(np.argwhere(np.array(sheet.Columns(1).Value).astype(np.bool)))
header=header[:nCols]
puff_info=[]

for row in np.arange(nPuffs)+2:
    puff=np.array(sheet.Rows(int(row)).Value[0][:nCols])
    puff_info.append(dict(zip(header,puff)))

puffX,puffY=[],[]

for i,puff in enumerate(puff_info):
    puffX.append(puff['x']*scaleFactor)
    puffY.append(puff['y']*scaleFactor)

excel.Application.Quit()

#######################extract STORM coordinates######################################
STORMX = np.loadtxt(STORMFileName,skiprows=1,usecols=(3,))
STORMY = np.loadtxt(STORMFileName,skiprows=1,usecols=(4,))

STORMX = np.divide(STORMX,scaleFactor2)
STORMY = np.divide(STORMY,scaleFactor2)
######################################################################################
# put a blue dot at (10, 20)
#plt.scatter([10], [20])

# put a red dot, size 40, at 2 locations:
#plt.scatter(x=[30, 40], y=[50, 60], c='r', s=40)

plt.scatter(STORMX,STORMY, c='r', s=1)
plt.scatter(puffX,puffY, c ='y', s =20)

#plt.axis("off")
plt.show()
