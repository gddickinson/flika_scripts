import numpy as np
from os.path import expanduser, join

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np

filePath = join(expanduser("~/Desktop"),'array_4D_data.npy')

data = np.load(filePath)
print(data.shape)
data = data.reshape((152,357,3,256))


# create qtgui
app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.orbit(256, 256)
w.setCameraPosition(0, 0, 0)
w.opts['distance'] = 200
w.show()
w.setWindowTitle('pyqtgraph example: GLVolumeItem')

g = gl.GLGridItem()
g.scale(20, 20, 1)
w.addItem(g)


v = gl.GLVolumeItem(data, sliceDensity=1, smooth=False, glOptions='translucent')
#v.translate(-data.shape[0]/2, -data.shape[1]/2, -150)
w.addItem(v)