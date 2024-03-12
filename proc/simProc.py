from hardware import Motor
from .proc import Proc

class SimProc(Proc):
    def __init__(self, mainMotorSpeed, mainMotorAccel, pullingMotorSpeed, pullingMotorAccel, pullingMotorDecel) -> None:
        super().__init__(mainMotorSpeed, mainMotorAccel, pullingMotorSpeed, pullingMotorAccel, pullingMotorDecel)
        self.mainMotor = Motor(mainMotorSpeed, mainMotorAccel)
        self.pullingMotor1 = Motor(pullingMotorSpeed, pullingMotorAccel)
        self.pullingMotor2 = Motor(pullingMotorSpeed, pullingMotorAccel)
        self.burnerMotor = Motor(1, 1)