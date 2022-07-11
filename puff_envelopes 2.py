# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 13:50:14 2015

@author: George
"""

a=np.mean(g.m.puffAnalyzer.clusters.cluster_im,3).astype(np.bool)
a=a*g.m.puffAnalyzer.highpass_window.image
Window(np.mean(a,0))
