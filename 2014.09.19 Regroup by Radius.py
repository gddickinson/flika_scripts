# -*- coding: utf-8 -*-
"""
Created on Thu Sep 18 13:41:22 2014
@author: Kyle Ellefsen

This file can open a Flika excel file regroup all the puffs into sites based on a different radius, and insert all the new data into a new sheet called 'Regrouped Puff Data'.  If a sheet with that name already exists, delete it before running this script.
There are two variables that are important to set.  One is the filename, and the other is the radius.
Uncomment the last lines to save and close the workbook
This site has a guide for manipulating excel sheets with win32com: http://pythonexcels.com/python-excel-mini-cookbook/
"""

from __future__ import (absolute_import, division,print_function, unicode_literals)
from future.builtins import (bytes, dict, int, list, object, range, str, ascii, chr, hex, input, next, oct, open, pow, round, super, filter, map, zip)
import numpy as np
import win32com.client
from pyqtgraph import plot, show


##############################################################################
#######                     THESE ARE THE VARIABLES YOU CAN SET    ###########
##############################################################################

filename="C:\\Users\\George\\Desktop\\Regrouped_puffs\\110826_SY5Y_1uMIP3_1uMFluo4_5uMEGTA_200msFlash_FullPower_22C_003.xlsx"
radius=3

##############################################################################






def groupSites(puff_info,radius=np.sqrt(2)):
    distances=np.zeros((nPuffs,nPuffs))
    for i in np.arange(nPuffs):
        x0,y0=(puff_info[i]['x'],puff_info[i]['y'])
        for j in np.arange(nPuffs):
            x1,y1=(puff_info[j]['x'],puff_info[j]['y'])
            distances[i,j]=np.sqrt((x1-x0)**2+(y1-y0)**2)
    distances=distances<=radius
    sites=[]
    sitesAdded=set()
    for i in np.arange(nPuffs):
        p=set([s[0] for s in np.argwhere(distances[i])])
        if len(p.intersection(sitesAdded))==0:
            sites.append(p)
            sitesAdded=sitesAdded.union(p)
        else:
            idx=[sites.index(site) for site in sites if len(site.intersection(p))>0][0]
            sites[idx]=sites[idx].union(p)
            sitesAdded=sitesAdded.union(p)
    i=1
    new_puff_info=[]
    for site in sites:
        puffs=[puff_info[s] for s in site]
        sitex,sitey=np.mean(np.array([np.array([p['x'],p['y']]) for p in puffs]),0)
        maxAmp=np.max([p['Amplitude'] for p in puffs])
        meanAmp=np.mean([p['Amplitude'] for p in puffs])
        ## this part fits a line through all the amplitudes of the 
        amp_vs_time=np.array([np.array([p['t_peak'],p['Amplitude']]) for p in puffs])
        y=amp_vs_time[:,1]
        x=amp_vs_time[:,0]
        A = np.vstack([x, np.ones(len(x))]).T
        m, b = np.linalg.lstsq(A, y)[0]
        #p=plot(x, y,pen=None, symbol='o')
        #p.plot(x, m*x + b)

        for puff in puffs:
            puff['Group #']=i
            puff['Group x']=sitex
            puff['Group y']=sitey
            puff['No. Events']=len(puffs)
            puff['Max Amp']=maxAmp
            puff['Amplitude Normalized by Site Mean']=puff['Amplitude']/meanAmp
            puff['Amplitude Normalized by Fitted Line']=puff['Amplitude']/(m*puff['t_peak']+b)
            new_puff_info.append(puff)
        i+=1
    return new_puff_info


excel = win32com.client.Dispatch("Excel.Application")
excel.Visible = True
workbook = excel.Workbooks.Open(filename)
sheet = workbook.Worksheets('Puff Data') #workbook.Worksheets(1) #workbook.Sheets('Sheet1').Select(); sheet = xlApp.ActiveSheet
header=np.array(sheet.Rows(1).Value[0])
nCols=np.max(np.argwhere(header.astype(np.bool)))+1
nPuffs=np.max(np.argwhere(np.array(sheet.Columns(1).Value).astype(np.bool)))
header=header[:nCols]
puff_info=[]
for row in np.arange(nPuffs)+2:
    puff=np.array(sheet.Rows(int(row)).Value[0][:nCols])
    puff_info.append(dict(zip(header,puff)))
    
puff_info=groupSites(puff_info,radius)

sheet=workbook.Worksheets.Add()
sheet.Name="Puff Data radius {}".format(radius)
header=list(header)
header.append('Amplitude Normalized by Site Mean')
header.append('Amplitude Normalized by Fitted Line')
for j in np.arange(len(header)):
    sheet.Cells(1,j+1).Value=header[j]
for i in np.arange(nPuffs):
    for j in np.arange(len(header)):
        sheet.Cells(int(i)+2,int(j)+1).Value=puff_info[i][header[j]]
    



workbook.Save()
workbook.Close()
excel.Quit()
















