from ui import BurnerSetupWindow
from PyQt6.QtWidgets import QMessageBox
import asyncio

from hardware import DDS220M, PowerPlot, StandaMotor, VControl
from hardware.standa import initDevices as initStandaMotors

lock = asyncio.Lock()

mainMotor = None
pullingMotor1 = None
pullingMotor2 = None
burnerMotor = None
vControl = None
powerPlot = None

mainMotor0 = 14.4
burnerMotor0 = 10
pullingMotor1_0 = 0
pullingMotor2_0 = 0

async def initDevices():
    mainMotor = DDS220M()
    ids = initStandaMotors()
    if len(ids) < 3:
        raise RuntimeError('Certain standa motors undetected')
    pullingMotor1 = StandaMotor(ids[0])
    pullingMotor2 = StandaMotor(ids[2])
    burnerMotor = StandaMotor(ids[1])

    vControl = VControl()
    powerPlot = PowerPlot()


async def _waitWindow(message: str, proc):
    waitWindow = QMessageBox(QMessageBox.Icon.Information, 'Подожди...', message, QMessageBox.StandardButton.NoButton)
    waitWindow.setStandardButtons(QMessageBox.StandardButton.NoButton)
    waitWindow.show()
    await proc()
    waitWindow.accept()

async def simLongProc():
    await asyncio.sleep(2)

async def simShortProc():
    await asyncio.sleep(.2)
    
async def _homing():
    await burnerMotor.home()
    await asyncio.gather(mainMotor.home(), pullingMotor1.home(), pullingMotor2.home())

async def _MTS():
    await burnerMotor.moveTo(burnerMotor0)
    await asyncio.gather(mainMotor.moveTo(mainMotor0), 
                         pullingMotor1.moveTo(pullingMotor1_0), 
                         pullingMotor2.moveTo(pullingMotor2_0))

async def homing():
    # warning
    async with lock:
        warning = QMessageBox(QMessageBox.Icon.Warning, 'Внимание!', 'Проверь, что раме не мешают другие подвижки и нажми ОК', 
                            QMessageBox.StandardButton.No | QMessageBox.StandardButton.Ok)
        if warning.exec() == QMessageBox.StandardButton.No:
            return -1
        
        # homing
        waitWindow = QMessageBox(QMessageBox.Icon.Information, 'Подожди', 'Выполняется поиск нуля...', QMessageBox.StandardButton.NoButton)
        waitWindow.show()

        await _waitWindow('Поиск нуля...', _homing)


        waitWindow.accept()


    return 0

async def MTS():
    await _waitWindow('Свдиг подвижек на начальные позиции...', _MTS)

async def burnerSetup():
    # wait until move under the camera
    # await WaitWindow.create('Горелка подводится под камеру...')
    await _waitWindow('Горелка подводится под камеру...', simLongProc)
    
    # setup
    setupWindow = BurnerSetupWindow(0)
    setupWindow.exec()

    # wait until move back
    # await WaitWindow.create('Горелка отводится назад...')
    await _waitWindow('Горелка отводится назад...', simLongProc)

async def HHOOn():
    print('HHO On')
    pass

async def HHOOff():
    print('HHO Off')
    pass

async def ignite():
    # warning
    warning = QMessageBox(QMessageBox.Icon.Warning, 'Внимание!', 'Убедись, что поток смеси достиг 21% на РРГ и нажми ОК', 
                          QMessageBox.StandardButton.No | QMessageBox.StandardButton.Ok)
    if warning.exec() == QMessageBox.StandardButton.No:
        return -1
    
    # ignition
    repeatition = QMessageBox(QMessageBox.Icon.Question, 'Повторить?', 'Повторить поджиг?', 
                              QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
    while True:
        pass # TODO add ignition
        if repeatition.exec() == QMessageBox.StandardButton.No: # check if ignited
            break


async def extinguish():
    repeatition = QMessageBox(QMessageBox.Icon.Question, 'Повторить?', 'Повторить тушение?', 
                              QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
    while True:
        pass # TODO add extinguishing
        if repeatition.exec() == QMessageBox.StandardButton.No: # check if extinguished
            break   
