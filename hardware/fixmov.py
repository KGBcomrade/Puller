import serial
import asyncio
from .pathes import ard_com

class Fixmov:
    def __init__(self) -> None:
        self.ard = serial.Serial(ard_com)

    async def moveBack(self, delay):
        self.ard.write(b'm')
        await asyncio.sleep(delay)
        self.ard.write(b's')