# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 13:41:22 2014
@author: Kyle Ellefsen

This file can open a Flika excel file and delete duplicate puffs.  Duplicate puffs are considered those with the same time point and within 1 pixel of each other.
Uncomment the last lines to save and close the workbook
This site has a guide for manipulating excel sheets with win32com: http://pythonexcels.com/python-excel-mini-cookbook/
"""

from __future__ import (absolute_import, division,print_function, unicode_literals)
from future.builtins import (bytes, dict, int, list, object, range, str, ascii, chr, hex, input, next, oct, open, pow, round, super, filter, map, zip)
import numpy as np
import win32com.client
from win32com.client import constants
from pyqtgraph import plot, show


##############################################################################
#######                     THESE ARE THE VARIABLES YOU CAN SET    ###########
##############################################################################

filename="C:\\Users\\George\\Desktop\\File_with_duplicates.xlsx"

##############################################################################

excel = win32com.client.Dispatch("Excel.Application")
excel.Visible = True
workbook = excel.Workbooks.Open(filename)
sheet = workbook.Worksheets('Sheet1')

header=np.array(sheet.Rows(1).Value[0])
nCols=np.max(np.argwhere(header.astype(np.bool)))+1
nPuffs=np.max(np.argwhere(np.array(sheet.Columns(1).Value).astype(np.bool)))
header=header[:nCols]
puff_info=[]
for row in np.arange(nPuffs)+2:
    puff=np.array(sheet.Rows(int(row)).Value[0][:nCols])
    puff_info.append(dict(zip(header,puff)))
    
marked_for_deletion=[]
x0,y0=[0,0]
for i,puff in enumerate(puff_info):
    x1,y1=puff['x'],puff['y']
    if np.sqrt((x1-x0)**2+(y1-y0)**2)<1:
        marked_for_deletion.append(i+1)
    x0,y0=x1,y1
marked_for_deletion.reverse()
for i in marked_for_deletion:
    sheet.Rows(i).Delete()
#END
