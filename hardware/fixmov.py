import serial
import asyncio
from .pathes import ard_com

class Fixmov:
    def __init__(self) -> None:
        self.ard = serial.Serial(ard_com)

    async def moveBack(self, event):
        self.ard.write(b'm')
        await event.wait()
        self.ard.write(b's')

    async def valveDelay(self, delay=20):
        self.ard.write(b'c')
        await asyncio.sleep(delay)
        self.ard.write(b'o')

    def valveClose(self):
        self.ard.write(b'c')