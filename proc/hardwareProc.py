from .proc import Proc
from hardware import DDS220M, PowerPlot, StandaMotor, VControl, Fixmov
from hardware.standa import initDevices as initStandaMotors

class HardwareProc(Proc):
    def __init__(self, mainMotorSpeed, mainMotorAccel, pullingMotorSpeed, pullingMotorAccel, pullingMotorDecel) -> None:
        super().__init__(mainMotorSpeed, mainMotorAccel, pullingMotorSpeed, pullingMotorAccel, pullingMotorDecel)
        
        self.mainMotor = DDS220M(speed=mainMotorSpeed, accel=mainMotorAccel)
        ids = initStandaMotors()
        if len(ids) < 3:
            raise RuntimeError('Certain standa motors undetected')
        self.pullingMotor1 = StandaMotor(ids[0], speed=pullingMotorSpeed, accel=pullingMotorAccel, decel=pullingMotorDecel)
        self.pullingMotor2 = StandaMotor(ids[2], speed=pullingMotorSpeed, accel=pullingMotorAccel, decel=pullingMotorDecel)
        self.burnerMotor = StandaMotor(ids[1], speed=1.5)

        self.vControl = VControl()
        self.powerPlot = PowerPlot()
        self.fixmov = Fixmov()