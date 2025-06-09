from PyQt6.QtCore import QRunnable
import numpy as np
from misc import getFiberInterp, Cam
import time
from scipy.integrate import quad
from scipy.interpolate import interp1d

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
        print('start fibercv')
        photo = self.cam.getPhoto()[lbound:ubound]
        fiber0X, fiber0Y = getFiberInterp(photo)
        fiber0 = interp1d(fiber0X, fiber0Y)
        while not self.stopFlag:
            time.sleep(self.delay)

            photo = self.cam.getPhoto()[lbound:ubound]
            fiberX, fiberY = getFiberInterp(photo)
            fiber = interp1d(fiberX, fiberY)

            xmin = np.max((fiber0X[0], fiberX[0]))
            xmax = np.min((fiber0X[-1], fiberX[-1]))

            shift = quad(lambda x: (fiber0(x) - fiber(x)) ** 2, xmin, xmax)[0]
            print(f'shift = {shift * self.cam.scale} um')

        print('fibercv stopped')

    def stop(self):
        self.stopFlag = True
        print('stop fibercv')