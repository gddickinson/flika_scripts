# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 15:32:27 2014

@author: Kyle Ellefsen
"""

from xlrd import open_workbook
import numpy as np
from pyqtgraph import plot




worksheet = open_workbook('flika_test.xls')
puff_data=worksheet.sheet_by_name('Puff Data')
nPuffs = puff_data.nrows-1
puffs=[]

###############################################################################
#### FIRST, GO THROUGH THE 'PUFF DATA' SHEET AND GET ALL THE TIME INFORMATION
###############################################################################
for i in np.arange(nPuffs)+1:
    puff=dict()
    row = puff_data.row_values(i)
    puff['group']=int(row[0])
    puff['t_peak']=int(row[7])
    puff['r100']=int(row[15])
    puff['t0']=puff['t_peak']-puff['r100']
    j=len(row)
    tf=''
    while tf=='': #this gets the last value in the row, which should be approximately the end time of the puff
        j-=1
        tf=row[j]
    puff['tf']=puff['t_peak']+int(tf) 
    puffs.append(puff)


###############################################################################
#### SECOND, GO THROUGH THE 'GROUP TRACES' SHEET AND GET THE TRACES FOR EACH PUFF
###############################################################################
group_traces=worksheet.sheet_by_name('Group traces')
for i in np.arange(nPuffs):
    puff=puffs[i]
    group=puff['group']
    col=group_traces.col_values(group-1)[1:]
    baseline=col[puff['t0']]
    puff['trace']=np.array(col[puff['t0']:puff['tf']]) - baseline
    

alltraces=np.concatenate([puff['trace'] for puff in puffs])
#plot(alltraces)
hist=np.histogram(alltraces, bins=1000, range=(-.1,.9))
#plot(hist[1][:-1],hist[0])

values=hist[0]
filename='Quantal_Analyzer_output.txt'
np.savetxt(filename,values,delimiter='\t',fmt='%10f')