# -*- coding: utf-8 -*-
"""
Created on Fri May 22 14:59:23 2015

@author: George
"""
img = g.m.currentWindow.image
img=img-np.min(img)
img=img/np.max(img)
selem = disk(5)
img_eq = rank.equalize(img, selem=selem)
Window(img_eq)

