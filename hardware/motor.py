from abc import ABC, abstractclassmethod
import asyncio

class MotorTempSpeed:
    def __init__(self, motor, speed, accel):
        self.motor = motor
        self.tspeed = speed
        self.taccel = accel
        self.pspeed = motor.speed
        self.paccel = motor.accel

    def __enter__(self):
        self.motor.setSpeed(self.tspeed)
        self.motor.setAccel(self.taccel)
    
    def __exit__(self, *exc):
        self.motor.setSpeed(self.pspeed)
        self.motor.setAccel(self.paccel)

class Motor:
    def __init__(self, speed, accel):
        self.speed = speed
        self.accel = accel

        self.lock = asyncio.Lock()

        self.setSpeed(speed)
        self.setAccel(accel)

    def setSpeed(self, speed):
        self.speed = speed
    
    def setAccel(self, accel):
        self.accel = accel

    def tempSpeed(self, speed, accel):
        return MotorTempSpeed(self, speed, accel)

    @abstractclassmethod
    async def moveBy(self, dp, interval=.1, lock=True):
        pass

    @abstractclassmethod
    async def moveTo(self, position, interval=.1, lock=True):
        pass

    @abstractclassmethod
    async def home(self, interval=.1, lock=True):
        pass