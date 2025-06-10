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
    def __init__(self, Kp, Ki=0, Kd=0, delay=1):
        super().__init__()
        self.delay = delay
        self.stopFlag = False
        self.cam = Cam('t_side')

        self.t = []
        self.shifts = []
        self.I = 0

        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
    
    def run(self):
        photo = self.cam.getPhoto()
        fiber0X, fiber0Y = getFiberInterp(photo, lbound, ubound)
        
        fiber0 = interp1d(fiber0X, fiber0Y)
        t0 = time.time()
        while not self.stopFlag:
            time.sleep(self.delay)

            photo = self.cam.getPhoto()
            try:
                fiberX, fiberY = getFiberInterp(photo, lbound, ubound)
            except IndexError:
                print('Error')
            except cv2.error:
                print('cv2 Error')
            fiber = interp1d(fiberX, fiberY)

            xmin = np.max((fiber0X[0], fiberX[0]))
            xmax = np.min((fiber0X[-1], fiberX[-1]))

            shift = np.sqrt(fixed_quad(lambda x: (fiber0(x) - fiber(x)) ** 2, xmin, xmax)[0])
            self.shifts.append(shift)
            self.t.append(time.time() - t0)
            self.I += shift * (self.t[-1] - 
                               (self.t[-2] if len(self.t) > 1 else t0))


    def stop(self):
        self.stopFlag = True

    def getVCoef(self):
        if len(self.shifts) == 0:
            return 0
        return self.Kp * (self.shifts[-1] + self.Ki * self.I)