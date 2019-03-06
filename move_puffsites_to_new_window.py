# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 10:43:07 2015

@author: George
"""

#select window to move sites to

import pyqtgraph as pg
g.m.currentWindow.imageview.addItem(g.m.puffAnalyzer.s1)
scatterplot=g.m.puffAnalyzer.s1
points=scatterplot.points()
spots=[{'pos':points[i].pos(),'data':points[i].data(),'brush':pg.mkBrush('r')} for i in np.arange(len(points))]
scatterplot.clear()
scatterplot.addPoints(spots)