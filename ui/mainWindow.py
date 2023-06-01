from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,\
     QSlider, QDial, QProgressBar, QLineEdit, QDialog, QDialogButtonBox, QGridLayout, QCheckBox, QDoubleSpinBox, QFrame
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QLocale

from ui import Plot, SetupWindow

homingButtonText = 'Поиск нуля'
MTSButtonText = 'Начальная позиция'
burnerSetupButtonText = 'Подвод горелки'
HHOGenButtonStartText = 'Включить подачу смеси'
HHOGenButtonStopText = 'Остановить подачу смеси'
ignitionButtonStartText = 'Зажечь пламя'
ignitionButtonStopText = 'Потушить пламя'
startButtonStartText = 'Запуск'
startButtonStopText = 'Стоп'
pullingSetupButtonText = 'Настройка растяжки...'

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        # pulling parameters
        self.r0 = 125 / 2
        self.rw = 10
        self.lw = 30

        self.xv = 1 # Standa velocity
        self.xa = .0001 # Standa acceleration
        self.xd = .4 # Standa deceleraion

        self.Lv = 8 # Thorlabs velocity
        self.La = 20 # Thorlabs acceleration

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
        sideButtonLayout.addWidget(self.homingButton)
        sideButtonLayout.addWidget(self.MTSButton)
        sideButtonLayout.addWidget(self.burnerSetupButton)
        sideButtonLayout.addWidget(self.HHOGenButton)
        sideButtonLayout.addWidget(self.ignitionButton)

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
        self.xaInput = QDoubleSpinBox(decimals=5, prefix='a=', suffix=' мм/с²')
        self.xaInput.setValue(self.xa)
        self.xdInput = QDoubleSpinBox(decimals=5, prefix='d=', suffix=' мм/с²')
        self.xdInput.setValue(self.xd)
        xPlotLayout.addWidget(self.xPlot)
        xPlotLayout.addLayout(xPlotSideLayout)
        xPlotSideLayout.addWidget(self.xvInput)
        xPlotSideLayout.addWidget(self.xaInput)
        xPlotSideLayout.addWidget(self.xdInput)
        self.xdInput.setFixedWidth(180)
        xPlotFrame.setMinimumHeight(280)
        
        # L plot
        self.LPlot = Plot(ylabel='$L$, mm')
        self.LvInput = QDoubleSpinBox(decimals=5, prefix='v=', suffix=' мм/с')
        self.LvInput.setValue(self.Lv)
        self.LaInput = QDoubleSpinBox(decimals=5, prefix='a=', suffix=' мм/с²')
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
        self.xvInput.valueChanged.connect(self.setXv)
        self.xaInput.valueChanged.connect(self.setXa)
        self.xdInput.valueChanged.connect(self.setXd)
        self.LvInput.valueChanged.connect(self.setLv)
        self.LaInput.valueChanged.connect(self.setLa)

    def callSetupDialog(self):
        setupWindow = SetupWindow(r0=self.r0, rw=self.rw, lw=self.lw)
        if setupWindow.exec():
            self.r0 = setupWindow.r0
            self.rw = setupWindow.rw
            self.lw = setupWindow.lw
    def setXv(self, xv):
        self.xv = xv
    def setXa(self, xa):
        self.xa = xa
    def setXd(self, xd):
        self.xd = xd

    def setLv(self, Lv):
        self.Lv = Lv
    def setLa(self, La):
        self.La = La

