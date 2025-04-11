from PyQt6.QtWidgets import QWidget, QPushButton, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,\
     QProgressBar, QDoubleSpinBox, QFrame, QMessageBox, QComboBox, QInputDialog
from PyQt6.QtGui import QAction

from ui import Plot, SetupWindow
from proc import Proc
from misc import SettingsLoader, Settings

from qasync import asyncSlot

homingButtonText = 'Поиск нуля'
MTSButtonText = 'Начальная позиция'
burnerSetupButtonText = 'Подвод горелки'
HHOGenButtonStartText = 'Включить подачу смеси'
HHOGenButtonStopText = 'Остановить подачу смеси'
ignitionButtonStartText = 'Зажечь пламя'
ignitionButtonStopText = 'Потушить пламя'
moveButtonText = 'Развести подвижки'
alignButtonText = 'Юстировка...'
startButtonStartText = 'Запуск'
startButtonStopText = 'Стоп'
pullingSetupButtonText = 'Настройка растяжки...'

newSettingsText = 'Новые настройки'
saveSettingsText = 'Сохранить'

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # pulling parameters
        self.settings = Settings()
        
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
        self.alignButton = QPushButton(alignButtonText)
        sideButtonLayout.addWidget(self.homingButton)
        sideButtonLayout.addWidget(self.MTSButton)
        sideButtonLayout.addWidget(self.burnerSetupButton)
        sideButtonLayout.addWidget(self.HHOGenButton)
        sideButtonLayout.addWidget(self.ignitionButton)
        sideButtonLayout.addWidget(self.moveButton)
        sideButtonLayout.addWidget(self.alignButton)

        # progress bar
        self.progressBar = QProgressBar()
        self.progressText = QLabel(f'r={self.settings.r0} → {self.settings.rw}')
        self.startButton = QPushButton(startButtonStartText)
        progressBarLayout.addWidget(self.progressBar)
        progressBarLayout.addWidget(self.progressText)
        progressBarLayout.addWidget(self.startButton)

        # x plot
        self.xPlot = Plot(ylabel='$x$, mm')
        self.xvInput = QDoubleSpinBox(decimals=5, prefix='v=', suffix=' мм/с')
        self.xvInput.setValue(self.settings.xv)
        self.xvInput.setRange(1e-5, 2000)
        self.xaInput = QDoubleSpinBox(decimals=5, prefix='a=', suffix=' мм/с²')
        self.xaInput.setValue(self.settings.xa)
        self.xaInput.setRange(1e-5, 2000)
        self.xaInput.setSingleStep(.001)
        self.xdInput = QDoubleSpinBox(decimals=5, prefix='d=', suffix=' мм/с²')
        self.xdInput.setValue(self.settings.xd)
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
        self.LvInput.setValue(self.settings.Lv)
        self.LaInput = QDoubleSpinBox(decimals=2, prefix='a=', suffix=' мм/с²')
        self.LaInput.setRange(1, 5000)
        self.LaInput.setValue(self.settings.La)
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
        self.alignButton.released.connect(self.callAlign)

        #proc init
        self.proc = Proc(
            self.settings.Lv, 
            self.settings.La, 
            self.settings.xv, 
            self.settings.xa, 
            self.settings.xd
        )

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
        setupWindow = SetupWindow(self.settings)
        if setupWindow.exec():
            self.settings = setupWindow.settings

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
    async def callAlign(self):
        await self.proc.align()

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
        await self.proc.run(self, self.settings)

    def callStop(self):
        self.toolBar.setEnabled(True)
        self.startButton.setEnabled(False)
        self.stopFlag = True
        
    def setXv(self):
        self.settings.xv = self.xvInput.value()
        self.proc.pullingMotor1.setSpeed(self.settings.xv)
        self.proc.pullingMotor2.setSpeed(self.settings.xv)
        
        self.settings.xv = self.proc.pullingMotor1.speed
        # self.xvInput.valueChanged.disconnect()
        self.xvInput.setValue(self.settings.xv)
        # self.xvInput.valueChanged.connect(self.setXv)

    def setXa(self):
        self.settings.xa = self.xaInput.value()
        self.proc.pullingMotor1.setAccel(self.settings.xa)
        self.proc.pullingMotor2.setAccel(self.settings.xa)

        self.settings.xa = self.proc.pullingMotor1.accel
        # self.xaInput.valueChanged.disconnect()
        self.xaInput.setValue(self.settings.xa)
        # self.xaInput.valueChanged.connect(self.setXa)

    def setXd(self):
        self.settings.xd = self.xdInput.value()
        self.proc.pullingMotor1.setDecel(self.settings.xd)
        self.proc.pullingMotor2.setDecel(self.settings.xd)

        self.settings.xd = self.proc.pullingMotor1.decel
        # self.xdInput.valueChanged.disconnect()
        self.xdInput.setValue(self.settings.xd)
        # self.xdInput.valueChanged.connect(self.setXd)

    def setLv(self):
        self.settings.Lv = self.LvInput.value()
        self.proc.mainMotor.setSpeed(self.settings.Lv)

    def setLa(self):
        self.settings.La = self.LaInput.value()
        self.proc.mainMotor.setAccel(self.settings.La)

    def updateIndicators(self, ts, xs, Ls, r, p):
        self.xPlot.plot(ts, xs)
        self.LPlot.plot(ts, Ls)

        self.progressText.setText(f'{r} → {self.settings.rw}')
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
        self.settings = self.settingsLoader.load(name)
        self.xvInput.setValue(self.settings.xv)
        self.setXv()
        self.xaInput.setValue(self.settings.xa)
        self.setXa()
        self.xdInput.setValue(self.settings.xd)
        self.setXd()
        self.LvInput.setValue(self.settings.Lv)
        self.setLv()
        self.LaInput.setValue(self.settings.La)
        self.setLa()

    def newSettings(self):
        name, ok = QInputDialog().getText(self, 'Имя настройки', 'Имя:')
        if name and ok:
            self.settingsLoader.save(name, self.settings)
            self.settingsList.addItem(name)
            self.settingsList.setCurrentText(name)
            self.loadSettings(name)
    def saveSettings(self):
        self.settingsLoader.save(self.settingsList.currentText(), self.settings)