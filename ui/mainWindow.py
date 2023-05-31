from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,\
     QSlider, QDial, QProgressBar, QLineEdit, QDialog, QDialogButtonBox, QGridLayout, QCheckBox, QDoubleSpinBox, QFrame
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QLocale

from ui import Plot

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
        LPLotFrame = QFrame()
        xPlotFrame.setFrameShape(QFrame.Shape.Panel)
        LPLotFrame.setFrameShape(QFrame.Shape.Panel)
        xPlotLayout = QHBoxLayout()
        LPlotLayout = QHBoxLayout()
        xPlotFrame.setLayout(xPlotLayout)
        LPLotFrame.setLayout(LPlotLayout)
        progressLayout.addLayout(progressBarLayout)
        progressLayout.addWidget(xPlotFrame)
        progressLayout.addWidget(LPLotFrame)

        xPlotSideLayout = QGridLayout()
        LPlotSideLayout = QGridLayout()

        # side buttons
        self.MTSButton = QPushButton(MTSButtonText)
        self.burnerSetupButton = QPushButton(burnerSetupButtonText)
        self.HHOGenButton = QPushButton(HHOGenButtonStartText)
        self.ignitionButton = QPushButton(ignitionButtonStartText)
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
        self.xvInput = QDoubleSpinBox(decimals=5)
        self.xvInput.setValue(self.xv)
        self.xaInput = QDoubleSpinBox(decimals=5)
        self.xaInput.setValue(self.xa)
        self.xdInput = QDoubleSpinBox(decimals=5)
        self.xdInput.setValue(self.xd)
        xPlotLayout.addWidget(self.xPlot)
        xPlotLayout.addLayout(xPlotSideLayout)
        xPlotSideLayout.addWidget(QLabel('v='), 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        xPlotSideLayout.addWidget(self.xvInput, 0, 1)
        xPlotSideLayout.addWidget(QLabel('мм/с'), 0, 2)
        xPlotSideLayout.addWidget(QLabel('a='), 1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        xPlotSideLayout.addWidget(self.xaInput, 1, 1)
        xPlotSideLayout.addWidget(QLabel('мм/с²'), 1, 2)
        xPlotSideLayout.addWidget(QLabel('d='), 2, 0, alignment=Qt.AlignmentFlag.AlignRight)
        xPlotSideLayout.addWidget(self.xdInput, 2, 1)
        xPlotSideLayout.addWidget(QLabel('мм/с²'), 2, 2)
        
        # L plot
        self.LPlot = Plot(ylabel='$L$, mm')
        self.LvInput = QDoubleSpinBox(decimals=5)
        self.LvInput.setValue(self.Lv)
        self.LaInput = QDoubleSpinBox(decimals=5)
        self.LaInput.setValue(self.La)
        self.pullingSetupButton = QPushButton(pullingSetupButtonText)
        LPlotLayout.addWidget(self.LPlot)
        LPlotLayout.addLayout(LPlotSideLayout)
        LPlotSideLayout.addWidget(QLabel('v='), 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        LPlotSideLayout.addWidget(self.LvInput, 0, 1)
        LPlotSideLayout.addWidget(QLabel('мм/с'), 0, 2)
        LPlotSideLayout.addWidget(QLabel('a='), 1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        LPlotSideLayout.addWidget(self.LaInput, 1, 1)
        LPlotSideLayout.addWidget(QLabel('мм/с²'), 1, 2)
        LPlotSideLayout.addWidget(self.pullingSetupButton, 2, 1)

