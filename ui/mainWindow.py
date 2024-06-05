from PyQt6.QtWidgets import QWidget, QPushButton, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,\
     QProgressBar, QDoubleSpinBox, QFrame, QMessageBox, QComboBox, QInputDialog
from PyQt6.QtGui import QAction

from ui import Plot, SetupWindow
from proc import Proc
from misc import SettingsLoader

from qasync import asyncSlot

homingButtonText = 'Поиск нуля'
MTSButtonText = 'Начальная позиция'
burnerSetupButtonText = 'Подвод горелки'
HHOGenButtonStartText = 'Включить подачу смеси'
HHOGenButtonStopText = 'Остановить подачу смеси'
ignitionButtonStartText = 'Зажечь пламя'
ignitionButtonStopText = 'Потушить пламя'
moveButtonText = 'Развести подвижки'
startButtonStartText = 'Запуск'
startButtonStopText = 'Стоп'
pullingSetupButtonText = 'Настройка растяжки...'

newSettingsText = 'Новые настройки'
saveSettingsText = 'Сохранить'

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # pulling parameters
        self.omegaType = 'theta'
        self.k = 7
        self.omega = 6.2
        self.x = 10
        self.L0 = 2
        self.alpha = -0.01
        self.r0 = 125 / 2
        self.rw = 25
        self.lw = 25

        self.tW = 45
        self.dr = .1

        self.xv = .03 # Standa velocity
        self.xa = 1 # Standa acceleration
        self.xd = 1 # Standa deceleraion

        self.Lv = 5 # Thorlabs velocity
        self.La = 300 # Thorlabs acceleration
        
        self.burnerPullingPos = 36.55

        self.stopFlag = False

        # toolbar
        self.toolBar = self.addToolBar('Settings')
        self.newAction = QAction(newSettingsText)
        self.saveAction = QAction(saveSettingsText)
        self.settingsList = QComboBox()
        self.toolBar.addAction(self.newAction)
        self.toolBar.addAction(self.saveAction)
        self.toolBar.addWidget(self.settingsList)
        # layouts
        mainLayout = QHBoxLayout()
        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)
        
        sideButtonFrame = QFrame()
        sideButtonFrame.setStyleSheet('background-color: rgb(120, 188, 255);')
        sideButtonLayout = QVBoxLayout()
        progressLayout = QVBoxLayout()
        mainLayout.addWidget(sideButtonFrame)
        sideButtonFrame.setLayout(sideButtonLayout)
        mainLayout.addLayout(progressLayout)
        
        progressBarLayout = QHBoxLayout()
        xPlotFrame = QFrame()
        LPlotFrame = QFrame()
        xPlotFrame.setFrameShape(QFrame.Shape.Panel)
        LPlotFrame.setFrameShape(QFrame.Shape.Panel)
        xPlotLayout = QHBoxLayout()
        LPlotLayout = QHBoxLayout()
        xPlotFrame.setLayout(xPlotLayout)
        LPlotFrame.setLayout(LPlotLayout)
        progressLayout.addLayout(progressBarLayout)
        progressLayout.addWidget(xPlotFrame)
        progressLayout.addWidget(LPlotFrame)

        xPlotSideLayout = QVBoxLayout()
        LPlotSideLayout = QVBoxLayout()

        # side buttons
        self.homingButton = QPushButton(homingButtonText)
        self.MTSButton = QPushButton(MTSButtonText)
        self.burnerSetupButton = QPushButton(burnerSetupButtonText)
        self.HHOGenButton = QPushButton(HHOGenButtonStartText)
        self.ignitionButton = QPushButton(ignitionButtonStartText)
        self.moveButton = QPushButton(moveButtonText)
        sideButtonLayout.addWidget(self.homingButton)
        sideButtonLayout.addWidget(self.MTSButton)
        sideButtonLayout.addWidget(self.burnerSetupButton)
        sideButtonLayout.addWidget(self.HHOGenButton)
        sideButtonLayout.addWidget(self.ignitionButton)
        sideButtonLayout.addWidget(self.moveButton)

        # progress bar
        self.progressBar = QProgressBar()
        self.progressText = QLabel(f'r={self.r0} → {self.rw}')
        self.startButton = QPushButton(startButtonStartText)
        progressBarLayout.addWidget(self.progressBar)
        progressBarLayout.addWidget(self.progressText)
        progressBarLayout.addWidget(self.startButton)

        # x plot
        self.xPlot = Plot(ylabel='$x$, mm')
        self.xvInput = QDoubleSpinBox(decimals=5, prefix='v=', suffix=' мм/с')
        self.xvInput.setValue(self.xv)
        self.xvInput.setRange(1e-5, 2000)
        self.xaInput = QDoubleSpinBox(decimals=5, prefix='a=', suffix=' мм/с²')
        self.xaInput.setValue(self.xa)
        self.xaInput.setRange(1e-5, 2000)
        self.xaInput.setSingleStep(.001)
        self.xdInput = QDoubleSpinBox(decimals=5, prefix='d=', suffix=' мм/с²')
        self.xdInput.setValue(self.xd)
        self.xdInput.setRange(1e-5, 2000)
        xPlotLayout.addWidget(self.xPlot)
        xPlotLayout.addLayout(xPlotSideLayout)
        xPlotSideLayout.addWidget(self.xvInput)
        xPlotSideLayout.addWidget(self.xaInput)
        xPlotSideLayout.addWidget(self.xdInput)
        self.xdInput.setFixedWidth(180)
        xPlotFrame.setMinimumHeight(280)
        
        # L plot
        self.LPlot = Plot(ylabel='$L$, mm')
        self.LvInput = QDoubleSpinBox(decimals=2, prefix='v=', suffix=' мм/с')
        self.LvInput.setRange(1, 300)
        self.LvInput.setValue(self.Lv)
        self.LaInput = QDoubleSpinBox(decimals=2, prefix='a=', suffix=' мм/с²')
        self.LaInput.setRange(1, 5000)
        self.LaInput.setValue(self.La)
        self.pullingSetupButton = QPushButton(pullingSetupButtonText)
        LPlotLayout.addWidget(self.LPlot)
        LPlotLayout.addLayout(LPlotSideLayout)
        LPlotSideLayout.addWidget(self.LvInput)
        LPlotSideLayout.addWidget(self.LaInput)
        LPlotSideLayout.addWidget(self.pullingSetupButton)
        self.LaInput.setFixedWidth(180)
        LPlotFrame.setMinimumHeight(280)


        self.pullingSetupButton.released.connect(self.callSetupDialog)
        self.xvInput.editingFinished.connect(self.setXv)
        self.xaInput.editingFinished.connect(self.setXa)
        self.xdInput.editingFinished.connect(self.setXd)
        self.LvInput.editingFinished.connect(self.setLv)
        self.LaInput.editingFinished.connect(self.setLa)
        
        self.ignitionButton.setEnabled(False)

        self.homingButton.released.connect(self.callHoming)
        self.MTSButton.released.connect(self.callMTS)
        self.burnerSetupButton.released.connect(self.callBurnerSetup)
        self.HHOGenButton.released.connect(self.callHHOOn)
        self.ignitionButton.released.connect(self.callIgnition)
        self.moveButton.released.connect(self.callMoveApart)

        #proc init
        self.proc = Proc(self.Lv, self.La, self.xv, self.xa, self.xd)

        # settings
        self.settingsLoader = SettingsLoader()
        self.settingsList.addItems(self.settingsLoader.getNames())
        self.settingsList.textActivated.connect(self.loadSettings)
        self.settingsList.setCurrentText(self.settingsLoader.last)
        self.loadSettings(self.settingsLoader.last)
        self.newAction.triggered.connect(self.newSettings)
        self.saveAction.triggered.connect(self.saveSettings)

        self.startButton.released.connect(self.callRun)

        

    def _setMovementEnabled(self, enabled: bool):
        self.homingButton.setEnabled(enabled)
        self.MTSButton.setEnabled(enabled)
        self.burnerSetupButton.setEnabled(enabled)

    def callSetupDialog(self):
        setupWindow = SetupWindow(omegaType=self.omegaType, r0=self.r0, rw=self.rw, lw=self.lw, k = self.k, omega=self.omega, x=self.x, L0=self.L0, alpha=self.alpha, tW=self.tW, dr=self.dr, x0=self.x0)
        if setupWindow.exec():
            self.omegaType = setupWindow.omegaType
            self.k = setupWindow.k
            self.omega = setupWindow.omega
            self.x = setupWindow.x
            self.L0 = setupWindow.L0
            self.alpha = setupWindow.alpha
            self.r0 = setupWindow.r0
            self.rw = setupWindow.rw
            self.lw = setupWindow.lw
            self.tW = setupWindow.tW
            self.dr = setupWindow.dr
            self.x0 = setupWindow.x0

    @asyncSlot()
    async def callMTS(self):
        self._setMovementEnabled(False)
        await self.proc.MTS()
        self._setMovementEnabled(True)

    @asyncSlot()
    async def callHoming(self):
        self._setMovementEnabled(False)
        await self.proc.homing()
        self._setMovementEnabled(True)

    @asyncSlot()
    async def callBurnerSetup(self):
        self._setMovementEnabled(False)
        self.burnerPullingPos = await self.proc.burnerSetup(self.burnerPullingPos)
        self._setMovementEnabled(True)

    @asyncSlot()
    async def callHHOOn(self):
        self.HHOGenButton.setText(HHOGenButtonStopText)
        self.HHOGenButton.released.disconnect()
        self.HHOGenButton.released.connect(self.callHHOOff) 
        
        await self.proc.HHOOn()

        self.ignitionButton.setEnabled(True)

    @asyncSlot()
    async def callHHOOff(self):
        self.HHOGenButton.setText(HHOGenButtonStartText)
        self.HHOGenButton.released.disconnect()
        self.HHOGenButton.released.connect(self.callHHOOn)
        
        self.ignitionButton.setEnabled(False)

        await self.proc.HHOOff()

    @asyncSlot()
    async def callIgnition(self):

        self.HHOGenButton.setEnabled(False)
        self._setMovementEnabled(False)
       
        if not (await self.proc.ignite()):
            self.ignitionButton.setText(ignitionButtonStopText)
            self.ignitionButton.released.disconnect()
            self.ignitionButton.released.connect(self.callExtinguish) 
        else:
            self.HHOGenButton.setEnabled(True)
            self._setMovementEnabled(True)


    @asyncSlot()
    async def callExtinguish(self):
        self.ignitionButton.setText(ignitionButtonStartText)
        self.ignitionButton.released.disconnect()
        self.ignitionButton.released.connect(self.callIgnition)

        await self.proc.extinguish()

        self.HHOGenButton.setEnabled(True)
        self._setMovementEnabled(True)

    @asyncSlot()
    async def callMoveApart(self):
        await self.proc.moveApart()

    @asyncSlot()
    async def callRun(self):
        warning = QMessageBox(QMessageBox.Icon.Warning, 'Внимание', 'Крышка камеры закрыта?', 
                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if warning.exec() == QMessageBox.StandardButton.No:
            return
        self.startButton.setText(startButtonStopText)
        self.startButton.released.disconnect()
        self.startButton.released.connect(self.callStop)
        self.toolBar.setEnabled(False)
        await self.proc.run(self, self.omegaType, self.r0, tWarmen=self.tW, lw=self.lw, rw=self.rw, omega=self.omega, x=self.x, L0=self.L0, alpha=self.alpha, k=self.k, dr=self.dr)

    def callStop(self):
        self.toolBar.setEnabled(True)
        self.startButton.setEnabled(False)
        self.stopFlag = True
        
    def setXv(self):
        self.xv = self.xvInput.value()
        self.proc.pullingMotor1.setSpeed(self.xv)
        self.proc.pullingMotor2.setSpeed(self.xv)
        
        self.xv = self.proc.pullingMotor1.speed
        # self.xvInput.valueChanged.disconnect()
        self.xvInput.setValue(self.xv)
        # self.xvInput.valueChanged.connect(self.setXv)

    def setXa(self):
        self.xa = self.xaInput.value()
        self.proc.pullingMotor1.setAccel(self.xa)
        self.proc.pullingMotor2.setAccel(self.xa)

        self.xa = self.proc.pullingMotor1.accel
        # self.xaInput.valueChanged.disconnect()
        self.xaInput.setValue(self.xa)
        # self.xaInput.valueChanged.connect(self.setXa)

    def setXd(self):
        self.xd = self.xdInput.value()
        self.proc.pullingMotor1.setDecel(self.xd)
        self.proc.pullingMotor2.setDecel(self.xd)

        self.xd = self.proc.pullingMotor1.decel
        # self.xdInput.valueChanged.disconnect()
        self.xdInput.setValue(self.xd)
        # self.xdInput.valueChanged.connect(self.setXd)

    def setLv(self, Lv):
        self.Lv = Lv
        self.proc.mainMotor.setSpeed(self.Lv)

    def setLa(self, La):
        self.La = La
        self.proc.mainMotor.setAccel(self.La)

    def updateIndicators(self, ts, xs, Ls, r, p):
        self.xPlot.plot(ts, xs)
        self.LPlot.plot(ts, Ls)

        self.progressText.setText(f'{r} → {self.rw}')
        self.progressBar.setValue(p)

    @property
    def x0(self):
        return self._x0
    
    @x0.setter
    def x0(self, value):
        self._x0 = value

        self.proc.pullingMotor1StartPos = -self.x0 / 2
        self.proc.pullingMotor2StartPos = -self.x0 / 2


    def loadSettings(self, name):
        self.omegaType, self.k, self.omega, self.x, self.L0, self.alpha, self.r0, self.rw, self.lw, self.xv, self.xa, self.xd, self.Lv, self.La, self.tW, self.dr, self.x0 = self.settingsLoader.load(name)
        self.xvInput.setValue(self.xv)
        self.xaInput.setValue(self.xa)
        self.xdInput.setValue(self.xd)
        self.LvInput.setValue(self.Lv)
        self.LaInput.setValue(self.La)

    def newSettings(self):
        name, ok = QInputDialog().getText(self, 'Имя настройки', 'Имя:')
        if name and ok:
            self.settingsLoader.save(name, omegaType=self.omegaType, k=self.k, omega=self.omega, x=self.x, L0=self.L0, alpha=self.alpha, r0=self.r0, rw=self.rw, lw=self.lw, xv=self.xv, xa=self.xa, xd=self.xd, Lv=self.Lv, La=self.La, tW=self.tW, dr=self.dr, x0=self.x0)
            self.settingsList.addItem(name)
            self.settingsList.setCurrentText(name)
            self.loadSettings(name)
    def saveSettings(self):
        self.settingsLoader.save(self.settingsList.currentText(), omegaType=self.omegaType, k=self.k, omega=self.omega, x=self.x, L0=self.L0, alpha=self.alpha, r0=self.r0, rw=self.rw, lw=self.lw, xv=self.xv, xa=self.xa, xd=self.xd, Lv=self.Lv, La=self.La, tW=self.tW, dr=self.dr, x0=self.x0)