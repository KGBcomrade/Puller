from time import time
import os
from ui import BurnerSetupWindow, FinishWindow, MoveApartWindow, AlignWindow
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QThreadPool
import asyncio
import pandas as pd
import numpy as np
import datetime

from misc import getLx, Settings
from hardware.pathes import save_path

from sacred.observers import MongoObserver
from sacred import Experiment
import dotenv

from .fibercv import FiberCV

mainMotorTempSpeed = 16
mainMotorTempAccel = 20
pullingMotorTempSpeed = 2
pullingMotorTempAccel = 1
fixMotorDelay = 12.3

class Proc:
    def __init__(self, mainMotorSpeed, mainMotorAccel, pullingMotorSpeed, pullingMotorAccel, pullingMotorDecel, Kp, Ki, Kd) -> None:
        self.lock = asyncio.Lock()

        self.mainMotorStartPos = 14.4
        self.mainMotorEndPos = 181
        self.mainMotorAlignPos = 102.5
        self.gapLength = 31 # мм, расстояние между краями тянущих подвижек
        self.burnerMotorStartPos = 6
        self.burnerMotorExtPos = self.burnerMotorStartPos + 10
        self.burnerMotorWorkPos = 36.8
        self.pullingMotor1StartPos = 0
        self.pullingMotor2StartPos = 0
        self.stretch = 0.001 # мм, шаг ручного растяжения

        self.data = pd.DataFrame({'t': [], 'x': [], 'L': []})

        self.tStart = 0

        self.plotEvent = asyncio.Event()

        self.threadPool = QThreadPool()
        self.fcv = FiberCV(Kp, Ki, Kd, delay=.25)


    async def _waitWindow(message: str, proc, *args, **kwargs):
        waitWindow = QMessageBox(QMessageBox.Icon.Information, 'Подожди...', message, QMessageBox.StandardButton.NoButton)
        waitWindow.setStandardButtons(QMessageBox.StandardButton.NoButton)
        waitWindow.show()
        await proc(*args, **kwargs)
        waitWindow.accept()

    async def _cancellableWaitWindow(message: str, proc, *args, **kwargs):
        waitWindow = QMessageBox(QMessageBox.Icon.Information, 'Подожди...', message, QMessageBox.StandardButton.Cancel)
        waitWindow.show()

        waitEvent = asyncio.Event()

        def onCancel():
            waitEvent.set()

        waitWindow.rejected.connect(onCancel)

        await proc(*args, **kwargs, event=waitEvent)

    async def _homing(self):
        with self.mainMotor.tempSpeed(mainMotorTempSpeed, mainMotorTempAccel), \
            self.pullingMotor1.tempSpeed(pullingMotorTempSpeed, pullingMotorTempAccel), \
                self.pullingMotor2.tempSpeed(pullingMotorTempSpeed, pullingMotorTempAccel):
            await self.burnerMotor.home()
            await asyncio.gather(self.mainMotor.home(), self.pullingMotor1.home(), self.pullingMotor2.home())

    async def _fixmovMove(self, event):
        async def moveDelay():
            await asyncio.sleep(fixMotorDelay)
            event.set()
        mdTask = asyncio.create_task(moveDelay())
        await self.fixmov.moveBack(event)
        mdTask.cancel()

    async def _MTS(self):
        with self.mainMotor.tempSpeed(mainMotorTempSpeed, mainMotorTempAccel), \
            self.pullingMotor1.tempSpeed(pullingMotorTempSpeed, pullingMotorTempAccel), \
            self.pullingMotor2.tempSpeed(pullingMotorTempSpeed, pullingMotorTempAccel):
            await self.burnerMotor.moveTo(self.burnerMotorStartPos)
            await asyncio.gather(self.mainMotor.moveTo(self.mainMotorStartPos), 
                                self.pullingMotor1.moveTo(self.pullingMotor1StartPos), 
                                self.pullingMotor2.moveTo(self.pullingMotor2StartPos))

    async def _alignMove(self):
        await self.burnerMotor.moveTo(self.burnerMotorStartPos)
        with self.mainMotor.tempSpeed(mainMotorTempSpeed, mainMotorTempAccel):
            await self.mainMotor.moveTo(self.mainMotorAlignPos)
        

    async def _burnerForward(self):
        await self.burnerMotor.moveTo(self.burnerMotorWorkPos)

    async def _burnerBackward(self):
        await self.burnerMotor.moveTo(self.burnerMotorStartPos)

    def _moveBurner(self, pos):
        asyncio.run(self.burnerMotor.moveTo(pos))

    def _stretch(self):
        with self.pullingMotor1.tempSpeed(pullingMotorTempSpeed, pullingMotorTempAccel, pullingMotorTempAccel), \
        self.pullingMotor2.tempSpeed(pullingMotorTempSpeed, pullingMotorTempAccel, pullingMotorTempSpeed):
            self.pullingMotor1.moveByS(-self.stretch, lock=False)
            self.pullingMotor2.moveByS(-self.stretch, lock=False)
            self.pullingMotor1.waitForStop()
            self.pullingMotor2.waitForStop()


    def _moveApartS(self, x):
        with self.pullingMotor1.tempSpeed(pullingMotorTempSpeed, pullingMotorTempAccel, pullingMotorTempAccel), \
        self.pullingMotor2.tempSpeed(pullingMotorTempSpeed, pullingMotorTempAccel, pullingMotorTempSpeed):
            self.pullingMotor1.moveToS(-x, lock=False)
            self.pullingMotor2.moveToS(-x, lock=False)
            self.pullingMotor1.waitForStop()
            self.pullingMotor2.waitForStop()

    def _moveMainMotorS(self, x):
        self.mainMotor.moveToS(x)

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
        await Proc._cancellableWaitWindow('Отвод вилки для заклеивания...', self._fixmovMove)
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
        await self.vControl.extinguish(self.fixmov, delay=10, interval=2)
        repeatition = QMessageBox(QMessageBox.Icon.Question, 'Повторить?', 'Повторить тушение?', 
                                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
        while repeatition.exec() == QMessageBox.StandardButton.Yes:
            await self.vControl.extinguish(self.fixmov, interval=3)  

    async def moveApart(self):
        maw = MoveApartWindow()
        if maw.exec():
            await Proc._waitWindow('Подвижки разовдятся...', self._moveApart, maw.getMotors(), -maw.coord)

    async def align(self):
        await Proc._waitWindow('Рама подводится под камеру...', self._alignMove)
        alignWindow = AlignWindow(self._moveApartS, self._moveMainMotorS, self.mainMotorAlignPos, self.gapLength)
        alignWindow.exec()

    async def _moveApart(self, motors, coord):
        tasks = []
        with self.pullingMotor1.tempSpeed(pullingMotorTempSpeed, pullingMotorTempAccel, pullingMotorTempAccel), \
        self.pullingMotor2.tempSpeed(pullingMotorTempSpeed, pullingMotorTempAccel, pullingMotorTempSpeed):
            
            if motors[0]:
                tasks.append(asyncio.create_task(self.pullingMotor2.moveTo(coord)))
            if motors[1]:
                tasks.append(asyncio.create_task(self.pullingMotor1.moveTo(coord)))
            
            await asyncio.gather(*tasks)
                
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
            
            self.plotEvent.set()

    async def _plotter(self, Lx, Rx, xMax, updater):
        while True:
            x = self._getX()
            if x >= xMax:
                break
            self.data.loc[len(self.data) + 1] = [time() - self.tStart, x, Lx(x).item()]
            updater(self.data['t'], self.data['x'], self.data['L'], Rx(x), x * 100 // xMax, self.fcv.t, self.fcv.shifts)
            
            await self.plotEvent.wait()
            self.plotEvent.clear()

    async def _pullerMotorRun(self, xMax):
        await asyncio.gather(self.pullingMotor1.moveTo(self.pullingMotor1StartPos - xMax / 2),
                            self.pullingMotor2.moveTo(self.pullingMotor2StartPos - xMax / 2))

    def _upload(self, num, settings: Settings):
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

        conf = settings.__dict__
        conf['bX'] = self.burnerMotorWorkPos
        ex.add_config(conf)

        @ex.automain
        def _push(_run):
            for _, d in self.data.iterrows():
                for n, v in d.items():
                    _run.log_scalar(n, v)
            fname = os.path.join(save_path, str(datetime.date.today()), f'power_{num}.csv')
            _run.add_artifact(fname)
            power = np.genfromtxt(fname, delimiter=',')
            power[:, 0] += -power[:, 0].min() + self.tStart

            NN = 100 # reduced pplot metrics upload
            for tp in power[::NN]:
                _run.log_scalar('t_power', tp[0])
                _run.log_scalar('power', tp[1])
            
            meanN = 50 # power sampling
            P0 = power[:meanN, 1].mean()
            P1 = power[-meanN:, 1].mean()
            T = P1 / P0 * 100

            return float(T)

        ex.run()


    async def _delayedPPStart(self, delay=0):
        await asyncio.sleep(delay)
        self.powerPlot.run()
                


    async def run(self, win, settings: Settings):
        Lx, Rx, xMax, _, _ = getLx(settings)

        mainMotorTask = asyncio.create_task(self._mainMotorRun(Lx, xMax))
        ppTask = asyncio.create_task(self._delayedPPStart(0))
        await self.burnerMotor.moveTo(self.burnerMotorWorkPos) # Подвод горелки
        self.tStart = time() # Время начала прогрева
        self.threadPool.start(self.fcv)
        plotterTask = asyncio.create_task(self._plotter(Lx, Rx, xMax, win.updateIndicators))
        while time() - self.tStart < settings.tW:
            await asyncio.sleep(0)
        pullerMotorTask = asyncio.create_task(self._pullerMotorRun(xMax * (1)))

        while True:
            await asyncio.sleep(0)
            if win.stopFlag:
                pullerMotorTask.cancel()
                self.pullingMotor1.softStop()
                self.pullingMotor2.softStop()
                break

            if self._getX() >= xMax - 2 * win.settings.xv ** 2 / win.settings.xd:
                break

            if pullerMotorTask.done():
                break

        self.fcv.stop()
        returnTask = asyncio.create_task(self.burnerMotor.moveTo(self.burnerMotorExtPos))

        await asyncio.sleep(6) 

        mainMotorTask.cancel()
        plotterTask.cancel()
        
        await returnTask
        await win.callExtinguish()
        await win.callHHOOff()

        finishWindow = FinishWindow(self._stretch)
        finishWindow.exec()

        self.powerPlot.stop()

        finishTasks = [asyncio.create_task(self.burnerMotor.moveTo(self.burnerMotorStartPos))]

        if finishWindow.moveCheckBox.isChecked():
            finishTasks.append(asyncio.create_task(self.mainMotor.moveTo(self.mainMotorEndPos)))

        if finishWindow.saveCheckBox.isChecked():
            num = await asyncio.create_task(self.powerPlot.save(save_path))
            self.data.to_csv(os.path.join(save_path, str(datetime.date.today()), f'movement_{num}.csv'))

            if finishWindow.mongoDBCheckBox.isChecked():
                self._upload(num, settings)


        asyncio.gather(*finishTasks)
        win.callStop()