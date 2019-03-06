# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 11:08:35 2015

@author: George
"""


from __future__ import (absolute_import, division,print_function, unicode_literals)
#from future.builtins import (bytes, dict, int, list, object, range, str, ascii, chr, hex, input, next, oct, open, pow, round, super, filter, map, zip)
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
#import win32com.client
#from win32com.client import constants
import time
from pylab import rcParams
######## Set filenammes & variables ###########################################
#imageName  = 'J:\\WORK\\STORM_After-Cellights-and-Calcium-Imaging\\COS-CellLights-Red_ER\\150717\\150717_cos_celllights-er-rfp_5umcal520_1umip3_1umegta_uv-flash-ER_before_calcium-imaging_average.tif'
#imageName  = 'J:\\WORK\\STORM_After-Cellights-and-Calcium-Imaging\\COS-CellLights-Red_ER\\150717\\150717_cos_celllights-er-rfp_5umcal520_1umip3_1umegta_uv-flash-ER_before_calcium-imaging_average_divided-by-low-pass.tif'
#puffFileName = 'J:\\WORK\\STORM_After-Cellights-and-Calcium-Imaging\\COS-CellLights-Red_ER\\150717\\150717_cos_celllights-er-rfp_5umcal520_1umip3_1umegta_uv-flash-calcium-imaging_FLIKA_XY.txt'
#STORMFileName = 'J:\\WORK\\STORM_After-Cellights-and-Calcium-Imaging\\COS-CellLights-Red_ER\\150717\\150717_Cos_STORM_IP3R1-NTerm-A405-A647_test2_filtered-5in100.txt'

imageName  = 'J:\\WORK\\STORM_After-Cellights-and-Calcium-Imaging\\COS-CellLights-Red_ER\\150723\\150723_cos_celllights-er-rfp_5umcal520_1umip3_1umegta_uv-flash-ER_after_Calicum-imaging_before-Fix-Average.tif'
puffFileName = 'J:\\WORK\\STORM_After-Cellights-and-Calcium-Imaging\\COS-CellLights-Red_ER\\150723\\150723_cos_celllights-er-rfp_5umcal520_1umip3_1umegta_uv-flash_Calicum-imaging_FLIKA_XY.txt'
#STORMFileName = 'J:\\WORK\\STORM_After-Cellights-and-Calcium-Imaging\\COS-CellLights-Red_ER\\150723\\150723_Cos_STORM_KDEL_Cy3-A647_001.txt'
#STORMFileName = 'J:\\WORK\\STORM_After-Cellights-and-Calcium-Imaging\\COS-CellLights-Red_ER\\150723\\150723_Cos_STORM_IP3R1_AB5882_Cy3-A647_005.txt'
STORMFileName = 'J:\\WORK\\STORM_After-Cellights-and-Calcium-Imaging\\COS-CellLights-Red_ER\\150723\\150723_Cos_STORM_IP3R1_AB5882_Cy3-A647_ALL.txt'

scaleFactor = 2 ##for FLIKA performed with pixel bining
scaleFactor2 = 160  ##160 nm / pixel

####### Plot Image ############################################################
rcParams['figure.figsize'] = 11, 11

im = plt.imread(imageName)
implot = plt.imshow(im, cmap=cm.Greys_r, interpolation = 'nearest')


################### extract puff coordinates ##################################

######### For excel files - sometimes works!!! ######
#def extractPuffData(data_name, puffFileName, scaleFactor):
#    excel = win32com.client.Dispatch("Excel.Application")
#    #excel.Visible = True
#    workbook = excel.Workbooks.Open(puffFileName)
#    sheet = workbook.Worksheets('Puff Data')
#    
#    header=np.array(sheet.Rows(1).Value[0])
#    nCols=np.max(np.argwhere(header.astype(np.bool)))+1
#    nPuffs=np.max(np.argwhere(np.array(sheet.Columns(1).Value).astype(np.bool)))
#    header=header[:nCols]
#    puff_info=[]
#    
#    for row in np.arange(nPuffs)+2:
#        puff=np.array(sheet.Rows(int(row)).Value[0][:nCols])
#        puff_info.append(dict(zip(header,puff)))
#    
#    puff_data = []
#    
#    for i,puff in enumerate(puff_info):
#        puff_data.append(puff[data_name]*scaleFactor)
#        
#    
#    excel.Application.Quit()
#    return puff_data
#
#puffX = extractPuffData('x', puffFileName, scaleFactor)
#puffY = extractPuffData('y', puffFileName, scaleFactor)

puffX = np.loadtxt(puffFileName,skiprows=1,usecols=(0,))
puffY = np.loadtxt(puffFileName,skiprows=1,usecols=(1,))

puffX = np.multiply(puffX, scaleFactor)
puffY = np.multiply(puffY, scaleFactor)


##################### Make Scatter plot #######################################
# put a blue dot at (10, 20)
#plt.scatter([10], [20])

# put a red dot, size 40, at 2 locations:
#plt.scatter(x=[30, 40], y=[50, 60], c='r', s=40)


######################## Initial scatter plot #################################

#plt.scatter(STORMX,STORMY, c='r', edgecolor ='', s=1)
plt.scatter(puffX,puffY, c ='y', s =20)
plt.draw()
time.sleep(1)






