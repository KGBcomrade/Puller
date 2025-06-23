from PyQt6.QtCore import QRunnable
import numpy as np
from misc import getFiberInterp, Cam
import time
from scipy.integrate import fixed_quad
from scipy.interpolate import interp1d
import cv2

#crop params
lboundS = 20
uboundS = 160
lboundT = 135
uboundT = -20

class FiberCV(QRunnable):
    def __init__(self, Kp, Ki=0, Kd=0, delay=1):
        super().__init__()
        self.delay = delay
        self.stopFlag = False
        self.camSide = Cam('t_side')
        self.camTop = Cam('t_top')

        self.t = []
        self.shifts = []
        self.I = 0

        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
    
    def run(self):
        time.sleep(3)
        photo0Flag = False
        while not photo0Flag:
            photoSide = self.camSide.getPhoto()
            photoTop = self.camTop.getPhoto()
            try:
                fiber0Xs, fiber0Ys = getFiberInterp(photoSide, lboundS, uboundS, scale=self.camSide.scale)
                fiber0Xt, fiber0Yt = getFiberInterp(photoTop, lboundT, uboundT, scale=self.camTop.scale)
                photo0Flag = True
            except IndexError:
                print('Error')
                photo0Flag = False
            except cv2.error:
                print('cv2 Error')
                photo0Flag = False
        
        fiber0 = interp1d(fiber0Xs, np.sqrt(fiber0Ys ** 2 + fiber0Yt ** 2))
        t0 = time.time()
        while not self.stopFlag:
            time.sleep(self.delay)

            photoSide = self.camSide.getPhoto()
            photoTop = self.camTop.getPhoto()
            try:
                fiberXs, fiberYs = getFiberInterp(photoSide, lboundS, uboundS, scale=self.camSide.scale)
                fiberXt, fiberYt = getFiberInterp(photoTop, lboundT, uboundT, scale=self.camTop.scale)
            except IndexError:
                print('Error')
            except cv2.error:
                print('cv2 Error')
            fiber = interp1d(fiberXs, np.sqrt(fiberYs ** 2 + fiberYt ** 2))

            xmin = np.max((fiber0Xs[0], fiberXs[0]))
            xmax = np.min((fiber0Xs[-1], fiberXs[-1]))

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