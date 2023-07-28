from time import time
import os
from ui import BurnerSetupWindow, FinishWindow
from PyQt6.QtWidgets import QMessageBox
import asyncio
import pandas as pd
import numpy as np
import datetime

from hardware import DDS220M, PowerPlot, StandaMotor, VControl
from hardware.standa import initDevices as initStandaMotors

from misc import getLx
from hardware.pathes import save_path

from sacred.observers import MongoObserver
from sacred import Experiment
import dotenv

mainMotorTempSpeed = 16
mainMotorTempAccel = 20
pullingMotorTempSpeed = 1.5
pullingMotorTempAccel = 1

class Proc:
    def __init__(self, mainMotorSpeed, mainMotorAccel, pullingMotorSpeed, pullingMotorAccel, pullingMotorDecel) -> None:
        self.lock = asyncio.Lock()

        self.mainMotorStartPos = 14.4
        self.mainMotorEndPos = 214
        self.burnerMotorStartPos = 10
        self.burnerMotorExtPos = self.burnerMotorStartPos + 10
        self.burnerMotorWorkPos = 36.8
        self.pullingMotor1StartPos = 0
        self.pullingMotor2StartPos = 0
        self.stretch = 0.001 # мм, шаг ручного растяжения

        self.data = pd.DataFrame({'t': [], 'x': [], 'L': []})

        self.mainMotor = DDS220M(speed=mainMotorSpeed, accel=mainMotorAccel)
        ids = initStandaMotors()
        if len(ids) < 3:
            raise RuntimeError('Certain standa motors undetected')
        self.pullingMotor1 = StandaMotor(ids[0], speed=pullingMotorSpeed, accel=pullingMotorAccel, decel=pullingMotorDecel)
        self.pullingMotor2 = StandaMotor(ids[2], speed=pullingMotorSpeed, accel=pullingMotorAccel, decel=pullingMotorDecel)
        self.burnerMotor = StandaMotor(ids[1], speed=1.5)

        self.vControl = VControl()
        self.powerPlot = PowerPlot()

        self.tStart = 0


    async def _waitWindow(message: str, proc):
        waitWindow = QMessageBox(QMessageBox.Icon.Information, 'Подожди...', message, QMessageBox.StandardButton.NoButton)
        waitWindow.setStandardButtons(QMessageBox.StandardButton.NoButton)
        waitWindow.show()
        await proc()
        waitWindow.accept()

    async def _homing(self):
        with self.mainMotor.tempSpeed(mainMotorTempSpeed, mainMotorTempAccel), \
            self.pullingMotor1.tempSpeed(pullingMotorTempSpeed, pullingMotorTempAccel), \
                self.pullingMotor2.tempSpeed(pullingMotorTempSpeed, pullingMotorTempAccel):
            await self.burnerMotor.home()
            await asyncio.gather(self.mainMotor.home(), self.pullingMotor1.home(), self.pullingMotor2.home())

    async def _MTS(self):
        with self.mainMotor.tempSpeed(16, 20), self.pullingMotor1.tempSpeed(2000, 900), self.pullingMotor2.tempSpeed(2000, 900):
            await self.burnerMotor.moveTo(self.burnerMotorStartPos)
            await asyncio.gather(self.mainMotor.moveTo(self.mainMotorStartPos), 
                                self.pullingMotor1.moveTo(self.pullingMotor1StartPos), 
                                self.pullingMotor2.moveTo(self.pullingMotor2StartPos))

    async def _burnerForward(self):
        await self.burnerMotor.moveTo(self.burnerMotorWorkPos)

    async def _burnerBackward(self):
        await self.burnerMotor.moveTo(self.burnerMotorStartPos)

    def _moveBurner(self, pos):
        asyncio.run(self.burnerMotor.moveTo(pos))

    def _stretch(self):
        self.pullingMotor1.moveByS(-self.stretch)
        self.pullingMotor2.moveByS(-self.stretch)
        self.pullingMotor1.waitForStop()
        self.pullingMotor2.waitForStop()

    async def homing(self):
        # warning
        async with self.lock:
            warning = QMessageBox(QMessageBox.Icon.Warning, 'Внимание!', 'Проверь, что раме не мешают другие подвижки и нажми ОК', 
                                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Ok)
            if warning.exec() == QMessageBox.StandardButton.No:
                return -1
            
            # homing
            await Proc._waitWindow('Поиск нуля...', self._homing)

        return 0

    async def MTS(self):
        await Proc._waitWindow('Свдиг подвижек на начальные позиции...', self._MTS)

    async def burnerSetup(self, burnerPullingPos = 36.8):
        self.burnerMotorWorkPos = burnerPullingPos
        # wait until move under the camera
        await Proc._waitWindow('Горелка подводится под камеру...', self._burnerForward)
        
        # setup
        setupWindow = BurnerSetupWindow(self.burnerMotorWorkPos, self._stretch, self.burnerMotor.moveToS)
        setupWindow.exec()
        self.burnerMotorWorkPos = setupWindow.position

        # wait until move back
        # await WaitWindow.create('Горелка отводится назад...')
        await Proc._waitWindow('Горелка отводится назад...', self._burnerBackward)
        
        return setupWindow.position

    async def HHOOn(self):
        self.vControl.setHHOGenerationEnabled(True)
    async def HHOOff(self):
        self.vControl.setHHOGenerationEnabled(False)
    async def ignite(self):
        # warning
        warning = QMessageBox(QMessageBox.Icon.Warning, 'Внимание!', 'Убедись, что поток смеси достиг 21% на РРГ и нажми ОК', 
                            QMessageBox.StandardButton.No | QMessageBox.StandardButton.Ok)
        if warning.exec() == QMessageBox.StandardButton.No:
            return -1
        
        # ignition
        await self.vControl.ignite()
        repeatition = QMessageBox(QMessageBox.Icon.Question, 'Повторить?', 'Повторить поджиг?', 
                                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
        while True:
            await self.vControl.ignite()
            if repeatition.exec() == QMessageBox.StandardButton.No: # check if ignited
                break


    async def extinguish(self):
        await self.vControl.extinguish()
        repeatition = QMessageBox(QMessageBox.Icon.Question, 'Повторить?', 'Повторить тушение?', 
                                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
        while True:
            await self.vControl.extinguish()
            if repeatition.exec() == QMessageBox.StandardButton.No: # check if extinguished
                break   

    def _getX(self):
        xr0 = self.pullingMotor1StartPos + self.pullingMotor2StartPos
        xr = self.pullingMotor1.getPosition() + self.pullingMotor2.getPosition()
        return xr0 - xr

    async def _mainMotorRun(self, Lx, xMax):
        turn = 1
        while True:
            x = self._getX()
            if x >= xMax:
                x = xMax
            yTarget = Lx(x) / 2 * turn + self.mainMotorStartPos
            await self.mainMotor.moveTo(yTarget, lock=False)
            await self.mainMotor.waitForStop(yTarget)
            turn *= -1

    async def _plotter(self, Lx, Rx, xMax, updater):
        while True:
            x = self._getX()
            if x >= xMax:
                break
            self.data.loc[len(self.data) + 1] = [time() - self.tStart, x, Lx(x).item()]
            updater(self.data['t'], self.data['x'], self.data['L'], Rx(x))
            
            await asyncio.sleep(.5)

    async def _pullerMotorRun(self, xMax):
        await asyncio.gather(self.pullingMotor1.moveTo(self.pullingMotor1StartPos - xMax / 2),
                            self.pullingMotor2.moveTo(self.pullingMotor2StartPos - xMax / 2))

    def _upload(self, num):
        ex = Experiment('pulling_g')
        dotenv.load_dotenv('keys.env')
        url = 'mongodb://{user}:{pw}@{host}:{port}/?replicaSet={rs}&authSource={auth_src}'.format(
            user=os.environ['mango_username'],
            pw=os.environ['mango_password'],
            host=os.environ['mango_host'],
            port=os.environ['mango_port'],
            rs='rs01',
            auth_src=os.environ['mango_database'])

        ex.observers.append(MongoObserver(url, tlsCAFile='cert.crt', db_name=os.environ['mango_database']))

        @ex.automain
        def _push(_run):
            for _, d in self.data.iterrows():
                for n, v in d.items():
                    _run.log_scalar(n, v)
            power = np.genfromtxt(os.path.join(save_path, str(datetime.date.today()), f'power_{num}.csv'), delimiter=',')
            power[:, 0] += -power[:, 0].min() + self.tStart

            for tp in power:
                _run.log_scalar('t_power', tp[0])
                _run.log_scalar('power', tp[1])
            


        ex.run()
                


    async def run(self, win, rw=20, lw=30, r0=62.5, dr=1, tWarmen=0):
        Lx, Rx, xMax, _, _ = getLx(r0=r0, rw=rw, lw=lw, dr=dr)

        await self.burnerMotor.moveTo(self.burnerMotorWorkPos) # Подвод горелки
        self.powerPlot.run()
        self.tStart = time() # Время начала прогрева
        mainMotorTask = asyncio.create_task(self._mainMotorRun(Lx, xMax))
        # plotterTask = asyncio.create_task(self._plotter(Lx, Rx, xMax, win.updateIndicators))
        while time() - self.tStart < tWarmen:
            await asyncio.sleep(0)
        pullerMotorTask = asyncio.create_task(self._pullerMotorRun(xMax * (1)))

        while True:
            await asyncio.sleep(0)
            if win.stopFlag:
                pullerMotorTask.cancel()
                self.pullingMotor1.softStop()
                self.pullingMotor2.softStop()
                break

            if self.pullingMotor1.getPosition() >= xMax/2:
                break

            if pullerMotorTask.done():
                break

        returnTask = asyncio.create_task(self.burnerMotor.moveTo(self.burnerMotorExtPos))

        await asyncio.sleep(1) 

        mainMotorTask.cancel()
        # plotterTask.cancel()
        
        await returnTask
        await win.callExtinguish()
        await win.callHHOOff()

        self.powerPlot.stop()

        finishWindow = FinishWindow(self._stretch)
        finishWindow.exec()

        finishTasks = [asyncio.create_task(self.burnerMotor.moveTo(self.burnerMotorStartPos))]

        if finishWindow.moveCheckBox.isChecked():
            finishTasks.append(asyncio.create_task(self.mainMotor.moveTo(self.mainMotorEndPos)))

        if finishWindow.saveCheckBox.isChecked():
            num = await asyncio.create_task(self.powerPlot.save(save_path))
            self.data.to_csv(os.path.join(save_path, str(datetime.date.today()), f'movement_{num}.csv'))

            if finishWindow.mongoDBCheckBox.isChecked():
                self._upload(num)


        asyncio.gather(*finishTasks)
