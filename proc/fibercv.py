from PyQt6.QtCore import QRunnable
import numpy as np
from misc import getFiberInterp, Cam
import time
from scipy.integrate import fixed_quad
from scipy.interpolate import interp1d
import cv2

#crop params
lbound = 20
ubound = 160

class FiberCV(QRunnable):
    def __init__(self, delay=1):
        super().__init__()
        self.delay = delay
        self.stopFlag = False
        self.cam = Cam('t_side')
    
    def run(self):
        photo = self.cam.getPhoto()
        fiber0X, fiber0Y = getFiberInterp(photo, lbound, ubound)
        
        fiber0 = interp1d(fiber0X, fiber0Y)
        while not self.stopFlag:
            time.sleep(self.delay)

            photo = self.cam.getPhoto()
            try:
                fiberX, fiberY = getFiberInterp(photo, lbound, ubound)
            except IndexError:
                print('Error')
            fiber = interp1d(fiberX, fiberY)

            xmin = np.max((fiber0X[0], fiberX[0]))
            xmax = np.min((fiber0X[-1], fiberX[-1]))

            shift = np.sqrt(fixed_quad(lambda x: (fiber0(x) - fiber(x)) ** 2, xmin, xmax)[0])


    def stop(self):
        self.stopFlag = True