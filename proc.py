from time import time
from ui import BurnerSetupWindow, FinishWindow
from PyQt6.QtWidgets import QMessageBox
import asyncio

from hardware import DDS220M, PowerPlot, StandaMotor, VControl
from hardware.standa import initDevices as initStandaMotors

from misc import getLx

lock = asyncio.Lock()

mainMotor = None
pullingMotor1 = None
pullingMotor2 = None
burnerMotor = None
vControl = None
powerPlot = None

mainMotorStartPos = 14.4
mainMotorEndPos = 214
burnerMotorStartPos = 10
burnerMotorExtPos = burnerMotorStartPos + 10
burnerMotorWorkPos = 36.8
pullingMotor1StartPos = 0
pullingMotor2StartPos = 0
stretch = 0.001 # мм, шаг ручного растяжения

ts = []
xs = []
Ls = []

def initDevices():
    global mainMotor, burnerMotor, pullingMotor1, pullingMotor2, vControl, powerPlot
    mainMotor = DDS220M()
    ids = initStandaMotors()
    if len(ids) < 3:
        raise RuntimeError('Certain standa motors undetected')
    pullingMotor1 = StandaMotor(ids[0], speed=100)
    pullingMotor2 = StandaMotor(ids[2], speed=100)
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
    await burnerMotor.moveTo(burnerMotorStartPos)
    await asyncio.gather(mainMotor.moveTo(mainMotorStartPos), 
                         pullingMotor1.moveTo(pullingMotor1StartPos), 
                         pullingMotor2.moveTo(pullingMotor2StartPos))

async def _burnerForward():
    await burnerMotor.moveTo(burnerMotorWorkPos)

async def _burnerBackward():
    await burnerMotor.moveTo(burnerMotorStartPos)

def _moveBurner(pos):
    asyncio.run(burnerMotor.moveTo(pos))

def _stretch():
    pullingMotor1.moveByS(-stretch)
    pullingMotor2.moveByS(-stretch)
    pullingMotor1.waitForStop()
    pullingMotor2.waitForStop()

async def homing():
    # warning
    async with lock:
        warning = QMessageBox(QMessageBox.Icon.Warning, 'Внимание!', 'Проверь, что раме не мешают другие подвижки и нажми ОК', 
                            QMessageBox.StandardButton.No | QMessageBox.StandardButton.Ok)
        if warning.exec() == QMessageBox.StandardButton.No:
            return -1
        
        # homing
        await _waitWindow('Поиск нуля...', _homing)

    return 0

async def MTS():
    await _waitWindow('Свдиг подвижек на начальные позиции...', _MTS)

async def burnerSetup(burnerPullingPos = 36.8):
    global burnerMotorWorkPos
    burnerMotorWorkPos = burnerPullingPos
    # wait until move under the camera
    await _waitWindow('Горелка подводится под камеру...', _burnerForward)
    
    # setup
    setupWindow = BurnerSetupWindow(burnerMotorWorkPos, _stretch, burnerMotor.moveToS)
    setupWindow.exec()

    # wait until move back
    # await WaitWindow.create('Горелка отводится назад...')
    await _waitWindow('Горелка отводится назад...', _burnerBackward)
    
    return setupWindow.position

async def HHOOn():
    vControl.setHHOGenerationEnabled(True)
async def HHOOff():
    vControl.setHHOGenerationEnabled(False)
async def ignite():
    # warning
    warning = QMessageBox(QMessageBox.Icon.Warning, 'Внимание!', 'Убедись, что поток смеси достиг 21% на РРГ и нажми ОК', 
                          QMessageBox.StandardButton.No | QMessageBox.StandardButton.Ok)
    if warning.exec() == QMessageBox.StandardButton.No:
        return -1
    
    # ignition
    await vControl.ignite()
    repeatition = QMessageBox(QMessageBox.Icon.Question, 'Повторить?', 'Повторить поджиг?', 
                              QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
    while True:
        await vControl.ignite()
        if repeatition.exec() == QMessageBox.StandardButton.No: # check if ignited
            break


async def extinguish():
    await vControl.extinguish()
    repeatition = QMessageBox(QMessageBox.Icon.Question, 'Повторить?', 'Повторить тушение?', 
                              QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
    while True:
        await vControl.extinguish()
        if repeatition.exec() == QMessageBox.StandardButton.No: # check if extinguished
            break   

def _getX():
    xr0 = pullingMotor1StartPos + pullingMotor2StartPos
    xr = pullingMotor1.getPosition() + pullingMotor2.getPosition()
    return xr0 - xr

async def _mainMotorRun(Lx, xMax):
    turn = 1
    while True:
        x = _getX()
        if x >= xMax:
            break
        yTarget = Lx(x) / 2 * turn + mainMotorStartPos
        await mainMotor.moveTo(yTarget)
        turn *= -1

async def _plotter(Lx, Rx, xMax, updater):
    while True:
        x = _getX()
        if x >= xMax:
            break

        ts.append(time())
        xs.append(x)
        Ls.append(Lx(x))

        updater(ts, xs, Ls, Rx(x))
        
        await asyncio.sleep(.5)

async def _pullerMotorRun(xMax):
    await asyncio.gather(pullingMotor1.moveTo(pullingMotor1StartPos - xMax / 2),
                         pullingMotor2.moveTo(pullingMotor2StartPos - xMax / 2))

async def run(win, rw=20, lw=30, r0=62.5, dr=1, tWarmen=0):
    Lx, Rx, xMax, _, _ = getLx(r0=r0, rw=rw, lw=lw, dr=dr)

    await burnerMotor.moveTo(burnerMotorWorkPos) # Подвод горелки
    t0 = time() # Время начала прогрева

    mainMotorTask = asyncio.create_task(_mainMotorRun(Lx, xMax))
    plotterTask = asyncio.create_task(_plotter(Lx, Rx, xMax, win.updateIndicators))
    while time() - t0 < tWarmen:
        await asyncio.sleep(0)
    
    await _pullerMotorRun(xMax)
    mainMotorTask.cancel()
    plotterTask.cancel()

    await burnerMotor.moveTo(burnerMotorExtPos)
    await win.callExtinguish()

    finishWindow = FinishWindow(_stretch)
    finishWindow.exec()

    finishTasks = [asyncio.create_task(burnerMotor.moveTo(burnerMotorStartPos))]

    if finishWindow.moveCheckBox.isChecked():
        finishTasks.append(asyncio.create_task(mainMotor.moveTo(mainMotorEndPos)))

    if finishWindow.saveCheckBox.isChecked():
        #TODO add saving task
        pass

    asyncio.gather(*finishTasks)
