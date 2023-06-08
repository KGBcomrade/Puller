from ctypes import *
import os
import re
import sys
import tempfile
import urllib
import asyncio
from . import pathes

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

# def com_get_position_calb(device_id,SetCalibr):
#     # print("\nRead position")
#     x_pos = get_position_calb_t()
#     result = lib.get_position(device_id, byref(x_pos),SetCalibr)
#     print("Result: " + repr(result))
#     print(x_pos.Position)
#     return x_pos.Position

def get_position_calb(device_id):
    print("\nRead position")
    x_pos = get_position_t()
    result = lib.get_position(device_id, byref(x_pos))
    print("Result: " + repr(result))
    if result == Result.Ok:
        print("Position: {0} steps, {1} microsteps".format(x_pos.Position, x_pos.uPosition))        
    return 0.00125*(x_pos.Position +  x_pos.uPosition/pow(2,9-1))   

def left(device_id):
    print("\nMoving left")
    result = lib.command_left(device_id)
    print("Result: " + repr(result))

def move(device_id, distance, udistance):
    print("\nGoing to {0} steps, {1} microsteps".format(distance, udistance))
    result = lib.command_move(device_id, distance, udistance)
    print("Result: " + repr(result))

def wait_for_stop(device_id, interval):
    print("\nWaiting for stop")
    result = lib.command_wait_for_stop(device_id, interval)
    print("Result: " + repr(result))

def serial(device_id):
    print("\nReading serial")
    x_serial = c_uint()
    result = lib.get_serial_number(device_id, byref(x_serial))
    if result == Result.Ok:
        print("Serial: " + repr(x_serial.value))

def get_speed(device_id)        :
    print("\nGet speed")
    # Create move settings structure
    mvst = move_settings_t()
    # Get current move settings from controller
    result = lib.get_move_settings(device_id, byref(mvst))
    # Print command return status. It will be 0 if all is OK
    print("Read command result: " + repr(result))    
    
    return mvst.Speed
        
def get_position(device_id):
    print("\nRead position")
    x_pos = get_position_t()
    result = lib.get_position(device_id, byref(x_pos))
    print("Result: " + repr(result))
    if result == Result.Ok:
        print("Position: {0} steps, {1} microsteps".format(x_pos.Position, x_pos.uPosition))
    return x_pos.Position, x_pos.uPosition

def set_speed(device_id, speed):
    print("\nSet speed")
    # Create move settings structure
    mvst = move_settings_t()
    # Get current move settings from controller
    result = lib.get_move_settings(device_id, byref(mvst))
    # Print command return status. It will be 0 if all is OK
    print("Read command result: " + repr(result))
    print("The speed was equal to {0}. We will change it to {1}".format(mvst.Speed, speed))
    # Change current speed
    mvst.Speed = int(speed)
    # Write new move settings to controller
    result = lib.set_move_settings(device_id, byref(mvst))
    # Print command return status. It will be 0 if all is OK
    print("Write command result: " + repr(result))    

def set_microstep_mode_256(device_id):
    print("\nSet microstep mode to 256")
    # Create engine settings structure
    eng = engine_settings_t()
    # Get current engine settings from controller
    result = lib.get_engine_settings(device_id, byref(eng))
    # Print command return status. It will be 0 if all is OK
    print("Read command result: " + repr(result))
    # Change MicrostepMode parameter to MICROSTEP_MODE_FRAC_256
    # (use MICROSTEP_MODE_FRAC_128, MICROSTEP_MODE_FRAC_64 ... for other microstep modes)
    eng.MicrostepMode = MicrostepMode.MICROSTEP_MODE_FRAC_256
    # Write new engine settings to controller
    result = lib.set_engine_settings(device_id, byref(eng))
    # Print command return status. It will be 0 if all is OK
    print("Write command result: " + repr(result))    

def get_accel(device_id):
    print("\nGet accel")
    # Create move settings structure
    mvst = move_settings_t()
    # Get current move settings from controller
    result = lib.get_move_settings(device_id, byref(mvst))
    # Print command return status. It will be 0 if all is OK
    print("Read command result: " + repr(result))    
    
    return mvst.Accel

def get_decel(device_id):
    print("\nGet decel")
    # Create move settings structure
    mvst = move_settings_t()
    # Get current move settings from controller
    result = lib.get_move_settings(device_id, byref(mvst))
    # Print command return status. It will be 0 if all is OK
    print("Read command result: " + repr(result))    
    
    return mvst.Decel

def set_accel(device_id, accel):
    print("\nSet speed")
    # Create move settings structure
    mvst = move_settings_t()
    # Get current move settings from controller
    result = lib.get_move_settings(device_id, byref(mvst))
    # Print command return status. It will be 0 if all is OK
    print("Read command result: " + repr(result))
    print("The accel. rate was equal to {0}. We will change it to {1}".format(mvst.Accel, accel))
    # Change current speed
    mvst.Accel = int(accel)
    # Write new move settings to controller
    result = lib.set_move_settings(device_id, byref(mvst))
    # Print command return status. It will be 0 if all is OK
    print("Write command result: " + repr(result)) 

def set_decel(device_id, decel):
    print("\nSet speed")
    # Create move settings structure
    mvst = move_settings_t()
    # Get current move settings from controller
    result = lib.get_move_settings(device_id, byref(mvst))
    # Print command return status. It will be 0 if all is OK
    print("Read command result: " + repr(result))
    print("The decel. rate was equal to {0}. We will change it to {1}".format(mvst.Decel, decel))
    # Change current speed
    mvst.Decel = int(decel)
    # Write new move settings to controller
    result = lib.set_move_settings(device_id, byref(mvst))
    # Print command return status. It will be 0 if all is OK
    print("Write command result: " + repr(result))  

def standExit():
    # global lib
    # lib.close_device(byref(cast(device_id0, POINTER(c_int))))
    # lib.close_device(byref(cast(device_id1, POINTER(c_int))))
    # lib.close_device(byref(cast(device_id2, POINTER(c_int))))
    sys.exit()


SetCalibr = calibration_t()
SetCalibr.A = 0.00125
SetCalibr.MicrostepMode = 9

waitInterval = 100

class StandaMotor:
    def __init__(self, devId, speed=900, accel=900, decel=900):
        self.id = devId
        self.pos, self.uPos = get_position(devId)
        self.speed = get_speed
        self.accel = accel
        self.decel = decel

        self.lock = asyncio.Lock()
        
        set_microstep_mode_256(devId)
        set_speed(devId, speed)
        set_accel(devId, accel)
        set_decel(devId, decel)

    def setSpeed(self, speed):
        self.speed = speed
        set_speed(self.id, self.speed)
    
    def setAccel(self, accel):
        self.accel = accel
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

    async def _waitForStopAsync(self):
        status = status_t()
        while True:
            await asyncio.wait(waitInterval)
            lib.get_status(self.id, byref(status))
            if status.MoveSts & MoveState.MOVE_STATE_MOVING == 0:
                break

    async def moveTo(self, position):
        async with self.lock:
            lib.command_move_calb(self.id, c_float(position), SetCalibr)
            await self._waitForStopAsync()

    async def home(self):
        async with self.lock:
            lib.command_homezero(self.id)
            await self._waitForStopAsync()
        
        

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
    
            
