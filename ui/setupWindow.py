import typing
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,\
     QSlider, QDial, QProgressBar, QLineEdit, QDialog, QDialogButtonBox, QGridLayout, QCheckBox, QDoubleSpinBox, QFrame
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QLocale
import numpy as np

from ui import Plot
from misc import getLx

class SetupWindow(QDialog):
    def __init__(self, r0 = 62.5, rw = 10, lw = 30) -> None:
        super().__init__()

        self.rw = rw
        self.lw = lw
        self.r0 = r0

        mainLayout = QHBoxLayout()
        inputsLayout = QVBoxLayout()
        mainLayout.addLayout(inputsLayout)

        self.r0Input = QDoubleSpinBox(prefix='r0=', suffix=' мкм')
        self.r0Input.setMaximum(62.5)
        self.r0Input.setValue(r0)
        self.rwInput = QDoubleSpinBox(prefix='rw=', suffix=' мкм')
        self.rwInput.setValue(rw)
        self.lwInput = QDoubleSpinBox(prefix='lw=', suffix=' мм')
        self.lwInput.setValue(lw)
        inputsLayout.addWidget(self.r0Input)
        inputsLayout.addWidget(self.rwInput)
        inputsLayout.addWidget(self.lwInput)
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        inputsLayout.addWidget(self.buttonBox)

        self.LPlot = Plot(xlabel='$x$, мм', ylabel='$L$, мм')
        self.rPlot = Plot(xlabel='$x$, мм', ylabel='$r$, мкм')
        mainLayout.addWidget(self.LPlot)
        mainLayout.addWidget(self.rPlot)

        self.r0Input.valueChanged.connect(self.updateR0)
        self.rwInput.valueChanged.connect(self.updateRw)
        self.lwInput.valueChanged.connect(self.updateLw)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.updatePlots()
        
        self.setLayout(mainLayout)

    def updatePlots(self):
        Lx, Rx, xMax, _, _ = getLx(r0=self.r0, lw=self.lw, rw=self.rw)
        x = np.linspace(0, xMax, 100)
        self.LPlot.plot(x, Lx(x))
        self.rPlot.plot(x, Rx(x))

    def updateR0(self, r0):
        self.r0 = r0
        self.updatePlots()
    def updateRw(self, rw):
        self.rw = rw
        self.updatePlots()
    def updateLw(self, lw):
        self.lw = lw
        self.updatePlots()
    