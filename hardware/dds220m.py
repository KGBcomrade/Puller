import asyncio
import codecs
import time
import ftd2xx
import ftd2xx.defines as constants
from StepMotorSupply import DP831A

def com(q):
    ed, _ = codecs.escape_decode(q, 'hex')    #Перевод в удобоваримый для контроллера формат bytes с одним slash. (https://www.py4u.net/discuss/165846)
    return ed

def SET_VELPARAMS_220(a, v):
	v = round(v*134218)
	v = (v).to_bytes(4, byteorder='little', signed=True)            
	
	a = round(a*13.744)
	a = (a).to_bytes(4, byteorder='little', signed=True)                                  

	e =b'\x13\x04\x0E\x00\xa1\x01\x01\x00\x00\x00\x00\x00' + a + v
	return e  

def MOVE_RELATIVE_220(d):
	d = round(d*20000)
	d = (d).to_bytes(4, byteorder='little', signed=True)
	e = b'\x48\x04\x06\x00\xa1\x01\x01\x00' + d
	return e

def MOVE_ABSolute_220(d):
	d = round(d*20000)
	d = (d).to_bytes(4, byteorder='little', signed=True)
	e = b'\x53\x04\x06\x00\xa1\x01\x01\x00' + d
	return e

class DDS220M:
    def __init__(self, speed = 5, accel = 25, address = b'73851530') -> None:
        self.drive = ftd2xx.openEx(address) 
        self.drive.resetDevice()
        self.drive.resetPort()
        self.drive.setBreakOff()
        print(self.drive.getDeviceInfo())
        self.drive.setBaudRate(115200)
        self.drive.setDataCharacteristics(constants.BITS_8, constants.STOP_BITS_1, constants.PARITY_NONE)
        time.sleep(.105)
        self.drive.purge()
        time.sleep(.105)
        self.drive.resetDevice()
        self.drive.setFlowControl(constants.FLOW_RTS_CTS, 0, 0)
        self.drive.setRts()

        self.drive.write(b'\x23\x02\x01\x00\x11\x01') # identify
        self.drive.write(com('\\x10\\x02\\x01\\x01\\x21\\x01')) # SET_CHAN ENABLESTATE
        time.sleep(.5)
        self.drive.write(com('\\x11\\x02\\x01\\x01\\x21\\x01')) # SET_CHAN ENABLESTATE
        time.sleep(.5)
        self.drive.write(com('\\x12\\x02\\x01\\x01\\x21\\x01')) # SET_CHAN ENABLESTATE
        time.sleep(0.2)

        self.drive.write(b'\x40\x04\x0E\x00\xa1\x01\x01\x00\x00\x00\x00\x00\x11\x11\x11\x00\x00\x00\x00\x00' ) # HOMEPARAMS

        self.speed = speed
        self.accel = accel

        self.drive.write(SET_VELPARAMS_220(self.accel, self.speed))

    def setSpeed(self, speed):
        self.speed = speed
        self.drive.write(SET_VELPARAMS_220(self.accel, self.speed))
    
    def setAccel(self, accel):
        self.accel = accel
        self.drive.write(SET_VELPARAMS_220(self.accel, self.speed))


    async def _waitForStop(self, interval):
        x = 0
        while True:
            self.drive.write(b'\x92\x04\x00\x00\x21\x01')      # ich bin da
            await asyncio.sleep(0.05)
            w1 = self.drive.read(nchars = (self.drive.getStatus())[0])
            if len(w1) >= 12 :
                if w1[0:2] == b'\x91\x04'    :
                    # ort = (int(w1[8]) + 16**2 * int(w1[9]) + 16**4 * int(w1[10]) + 16**6 * int(w1[11]))/20000
                    if ((int(w1[12]) + 16**2 * int(w1[13]))/20000 == 0):
                        if (x < 5): 
                            x += 1
                        else:
                            break
            await asyncio.sleep(interval)


    async def home(self, interval=.1, lock=True):
        self.drive.write(com('\\x43\\x04\\x01\\x00\\x21\\x01')) # MOVE_HOME
        self.drive.write(b'\x11\x00\x00\x00\x21\x01') # HW_START_UPDATEMSGS

        if lock:
            await self._waitForStop(interval)

    async def moveTo(self, position, interval=.1, lock=True):
        self.drive.write(MOVE_ABSolute_220(position))
        if lock:
            await self._waitForStop(interval)         