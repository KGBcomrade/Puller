from abc import ABC, abstractclassmethod
import asyncio

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

    @abstractclassmethod
    async def moveBy(self, dp, interval, lock):
        pass

    @abstractclassmethod
    async def moveTo(self, position, interval, lock):
        pass

    @abstractclassmethod
    async def home(self, interval, lock):
        pass