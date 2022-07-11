# -*- coding: utf-8 -*-
"""
Created on Mon Sep 15 13:24:11 2014
@author: Kyle Ellefsen

This file can be used to make pretty looking movies (.mp4) of calcium imaging data

You'll need to edit  the file names, and you'll need to create the output_directory for all the jpgs
"""



tif_file='trial3_widefield.tif'
directory='D:/Data/Ian Parker/2014.08.27 Shadowless TIRF Alternating Widefield/processed/'
output_directory='D:/Desktop/puffs/'

import pyqtgraph as pg
data_window=open_file(directory+tif_file)
boxcar_differential_filter(10,11,keepSourceWindow=True)
ratio(100,100,'standard deviation')
gaussian_blur(3)
threshold(1.4)
binary_window=remove_small_blobs(3, 25)
g.m.currentWindow=data_window
boxcar_differential_filter(10,11,keepSourceWindow=True)
texture_window=ratio(100,100,'standard deviation')
result=image_calculator(texture_window,binary_window,'Multiply')
bg_window=open_file('D:/Data/Ian Parker/2014.08.27 Shadowless TIRF Alternating Widefield/trial3_cal520_cIP3_EGTA_altshad_WF.stk')
bg_window_wf,bg_window_tirf=deinterleave(2)
close(bg_window_tirf)
g.m.currentWindow=bg_window_wf
zproject(59,600,'Average')
bg=g.m.currentWindow.image
close(g.m.currentWindow)
bgItem=pg.ImageItem(bg)
bgItem.setOpacity(.5)
g.m.currentWindow=result
g.m.currentWindow.imageview.view.addItem(bgItem)
time_stamp(100) #frame rate in Hz (frames per second)
exporter = pg.exporters.ImageExporter.ImageExporter(g.m.currentWindow.imageview.view)
for i in np.arange(1,2000):
    g.m.currentWindow.imageview.timeLine.setPos(310+i)
    exporter.export(output_directory+'{:03}.jpg'.format(i))

'''
Once you've exported all of the frames you wanted, open a command line and run the following:

    ffmpeg -r 100 -i %03d.jpg test1800.mp4
    
-r: framerate
-i: input files.  
%03d: The files have to be numbered 001.jpg, 002.jpg... etc.
'''