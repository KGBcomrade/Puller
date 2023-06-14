from ctypes import *
import os
import re
import sys
import tempfile
import urllib
import asyncio
from . import pathes
from .motor import Motor, MotorTempSpeed

try: 
    from pyximc import *
except ImportError as err:
    print ("Can't import pyximc module. The most probable reason is that you changed the relative location of the Python.py and pyximc.py files. See developers' documentation for details.")
    exit()
except OSError as err:
    # print(err.errno, err.filename, err.strerror, err.winerror) # Allows you to display detailed information by mistake.
    if platform.system() == "Windows":
        if err.winerror == 193:   # The bit depth of one of the libraries bindy.dll, libximc.dll, xiwrapper.dll does not correspond to the operating system bit.
            print("Err: The bit depth of one of the libraries bindy.dll, libximc.dll, xiwrapper.dll does not correspond to the operating system bit.")
            # print(err)
        elif err.winerror == 126: # One of the library bindy.dll, libximc.dll, xiwrapper.dll files is missing.
            print("Err: One of the library bindy.dll, libximc.dll, xiwrapper.dll is missing.")
            print("It is also possible that one of the system libraries is missing. This problem is solved by installing the vcredist package from the ximc\\winXX folder.")
            # print(err)
        else:           # Other errors the value of which can be viewed in the code.
            print(err)
        print("Warning: If you are using the example as the basis for your module, make sure that the dependencies installed in the dependencies section of the example match your directory structure.")
        print("For correct work with the library you need: pyximc.py, bindy.dll, libximc.dll, xiwrapper.dll")
    else:
        print(err)
        print ("Can't load libximc library. Please add all shared libraries to the appropriate places. It is decribed in detail in developers' documentation. On Linux make sure you installed libximc-dev package.\nmake sure that the architecture of the system and the interpreter is the same")
    exit()

def info(device_id):
    print("\nGet device info")
    x_device_information = device_information_t()
    result = lib.get_device_information(device_id, byref(x_device_information))
    print("Result: " + repr(result))
    if result == Result.Ok:
        print("Device information:")
        print(" Manufacturer: " +
                repr(string_at(x_device_information.Manufacturer).decode()))
        print(" ManufacturerId: " +
                repr(string_at(x_device_information.ManufacturerId).decode()))
        print(" ProductDescription: " +
                repr(string_at(x_device_information.ProductDescription).decode()))
        print(" Major: " + repr(x_device_information.Major))
        print(" Minor: " + repr(x_device_information.Minor))
        print(" Release: " + repr(x_device_information.Release))

def status(device_id):
    print("\nGet status")
    x_status = status_t()
    result = lib.get_status(device_id, byref(x_status))
    print("Result: " + repr(result))
    if result == Result.Ok:
        print("Status.Ipwr: " + repr(x_status.Ipwr))
        print("Status.Upwr: " + repr(x_status.Upwr))
        print("Status.Iusb: " + repr(x_status.Iusb))
        print("Status.Flags: " + repr(hex(x_status.Flags)))

def get_position_calb(device_id):
    x_pos = get_position_t()
    lib.get_position(device_id, byref(x_pos))
    return 0.00125*(x_pos.Position +  x_pos.uPosition/pow(2,9-1))   

def left(device_id):
    lib.command_left(device_id)

def move(device_id, distance, udistance):
    lib.command_move(device_id, distance, udistance)

def wait_for_stop(device_id, interval):
    lib.command_wait_for_stop(device_id, interval)

def serial(device_id):
    print("\nReading serial")
    x_serial = c_uint()
    result = lib.get_serial_number(device_id, byref(x_serial))
    if result == Result.Ok:
        print("Serial: " + repr(x_serial.value))

def get_speed(device_id):
    mvst = move_settings_t()
    lib.get_move_settings(device_id, byref(mvst))
    
    return mvst.Speed
        
def get_position(device_id):
    x_pos = get_position_t()
    lib.get_position(device_id, byref(x_pos))
    return x_pos.Position, x_pos.uPosition

def set_speed(device_id, speed):
    mvst = move_settings_calb_t()
    lib.get_move_settings_calb(device_id, byref(mvst), byref(SetCalibr))
    mvst.Speed = speed
    lib.set_move_settings_calb(device_id, byref(mvst), byref(SetCalibr))

def set_microstep_mode_256(device_id):
    eng = engine_settings_t()
    lib.get_engine_settings(device_id, byref(eng))
    eng.MicrostepMode = MicrostepMode.MICROSTEP_MODE_FRAC_256
    lib.set_engine_settings(device_id, byref(eng))

def get_accel(device_id):
    mvst = move_settings_t()
    lib.get_move_settings(device_id, byref(mvst))
    
    return mvst.Accel

def get_decel(device_id):
    mvst = move_settings_t()
    lib.get_move_settings(device_id, byref(mvst))
    
    return mvst.Decel

def set_accel(device_id, accel):
    mvst = move_settings_calb_t()
    lib.get_move_settings_calb(device_id, byref(mvst), byref(SetCalibr))
    mvst.Accel = accel
    lib.set_move_settings_calb(device_id, byref(mvst), byref(SetCalibr))

def set_decel(device_id, decel):
    mvst = move_settings_calb_t()
    lib.get_move_settings_calb(device_id, byref(mvst), byref(SetCalibr))
    mvst.Decel = decel
    lib.set_move_settings_calb(device_id, byref(mvst), byref(SetCalibr))

def standExit():
    sys.exit()


SetCalibr = calibration_t()
SetCalibr.A = 0.00125
SetCalibr.MicrostepMode = 9

waitInterval = 100

class StandaMotorTempSpeed(MotorTempSpeed):
    def __init__(self, motor, speed, accel, decel):
        super().__init__(motor, speed, accel)
        self.tdecel = decel
        self.pdecel = motor.decel

    def __enter__(self):
        super().__enter__()
        self.motor.setDecel(self.tdecel)

    def __exit__(self, *exc):
        super().__exit__(self, *exc)
        self.motor.setDecel(self.pdecel)

class StandaMotor(Motor):
    def __init__(self, devId, speed=1, accel=1, decel=1):
        self.id = devId
        self.pos, self.uPos = get_position(devId)
        self.decel = decel

        self.lock = asyncio.Lock()
        
        set_microstep_mode_256(devId)
        super().__init__(speed=speed, accel=accel)
        set_decel(devId, decel)

    def tempSpeed(self, speed, accel, decel=None):
        return StandaMotorTempSpeed(self, speed, accel, accel if decel is None else decel)

    def setSpeed(self, speed):
        super().setSpeed(speed)
        set_speed(self.id, self.speed)
    
    def setAccel(self, accel):
        super().setAccel(accel)
        set_accel(self.id, self.accel)

    def setDecel(self, decel):
        self.decel = decel
        set_decel(self.id, self.decel)

    def moveByS(self, dp):
        lib.command_movr_calb(self.id, c_float(dp), SetCalibr)

    def waitForStop(self):
        lib.command_wait_for_stop(self.id, waitInterval)

    def moveToS(self, position):
        lib.command_move_calb(self.id, c_float(position), SetCalibr)
        lib.command_wait_for_stop(self.id, waitInterval) 

    def getPosition(self):
        return get_position_calb(self.id)

    async def _waitForStopAsync(self, interval=.1):
        status = status_t()
        await asyncio.sleep(4 * interval)
        while True:
            await asyncio.sleep(interval)
            lib.get_status(self.id, byref(status))
            if status.MoveSts & MoveState.MOVE_STATE_MOVING == 0:
                break

    async def moveTo(self, position, interval=.1, lock=True):
        async with self.lock:
            lib.command_move_calb(self.id, c_float(position), SetCalibr)
            if lock:
                await self._waitForStopAsync(interval)

    async def moveBy(self, dp, interval=.1, lock=True):
        async with self.lock:
            lib.command_movr_calb(self.id, c_float(dp), SetCalibr)
            if lock:
                await self._waitForStopAsync(interval)

    async def home(self, interval=.1, lock=True):
        async with self.lock:
            lib.command_homezero(self.id)
            if lock:
                await self._waitForStopAsync(interval)

    def softStop(self):
        lib.command_sstp(self.id)
        
        

def initDevices():
    # This is device search and enumeration with probing. It gives more information about devices.
    if lib.set_bindy_key(pathes.key_path.encode('utf-8')) != Result.Ok:
        raise SystemError('Failed to set bindy key')
    probe_flags = EnumerateFlags.ENUMERATE_PROBE + EnumerateFlags.ENUMERATE_NETWORK
    enum_hints = b"addr="
    devenum = lib.enumerate_devices(probe_flags, enum_hints)
    dev_count = lib.get_device_count(devenum)
    devNames = [lib.get_device_name(devenum, i) for i in range(dev_count)]

    for i in range(dev_count):
        if type(devNames[i]) is str:
            devNames[i] = devNames[i].encode()
            
    devIds = [lib.open_device(devName) for devName in devNames]

    return devIds
    
            
