# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 16:46:59 2020

@author: g_dic
"""
import flika
from flika import global_vars as g
from flika import *
import sys 

sys.path.append(r'C:\Users\g_dic\.FLIKA\plugins')

from pynsight.pynsight import *
from pynsight.particle_simulator import particle_simulator

#%gui qt
#start_flika()

simulated_particles = particle_simulator(.1, .01, 50, .1, 500, 128, .1, .16)
data_window = Window(simulated_particles.particle_window.image)
data_window.setName('Data Window (F/F0)')
blur_window = gaussian_blur(2, norm_edges=True, keepSourceWindow=True)
blur_window.setName('Blurred Window')
binary_window = threshold(18, keepSourceWindow=True)
binary_window.setName('Binary Window')
binary_window.save
pynsight.gui()