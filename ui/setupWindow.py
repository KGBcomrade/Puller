import typing
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,\
     QSlider, QDial, QProgressBar, QLineEdit, QDialog, QDialogButtonBox, QGridLayout, QCheckBox, QDoubleSpinBox, QFrame, QComboBox
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QLocale
import numpy as np

from ui import Plot
from misc import getLx, omegaTypes, getROmega

class SetupWindow(QDialog):
    def __init__(self, omegaType = 'theta', r0 = 62.5, rw = 10, lw = 30, k = 7, tW = 0, dr=.1) -> None:
        super().__init__()

        self.omegaType = omegaType
        self.rw = rw
        self.lw = lw
        self.r0 = r0
        self.k = k
        self.tW = tW
        self.dr = dr

        mainLayout = QHBoxLayout()
        inputsLayout = QVBoxLayout()
        mainLayout.addLayout(inputsLayout)

        self.omegaTypesCB = QComboBox()
        self.omegaTypesCB.addItems(omegaTypes)
        self.omegaTypesCB.textActivated.connect(self.updateOmegaType)
        self.omegaTypesCB.setCurrentText(self.omegaType)

        self.kInput = QDoubleSpinBox(prefix='𝚯/=')
        self.kInput.setMaximum(2000)
        self.kInput.setMinimum(.01)
        self.kInput.setValue(self.k)
        self.r0Input = QDoubleSpinBox(prefix='r0=', suffix=' мкм')
        self.r0Input.setMaximum(62.5)
        self.r0Input.setValue(r0)
        self.rwInput = QDoubleSpinBox(prefix='rw=', suffix=' мкм')
        self.rwInput.setValue(rw)
        self.lwInput = QDoubleSpinBox(prefix='lw=', suffix=' мм')
        self.lwInput.setValue(lw)
        self.tWInput = QDoubleSpinBox(prefix='tW=', suffix='с')
        self.tWInput.setMinimum(0)
        self.tWInput.setMaximum(500)
        self.tWInput.setValue(self.tW)
        self.drInput = QDoubleSpinBox(prefix='dr=')
        self.drInput.setMaximum(2)
        self.drInput.setMinimum(.001)
        self.drInput.setValue(self.dr)
        inputsLayout.addWidget(self.omegaTypesCB)
        inputsLayout.addWidget(self.kInput)
        inputsLayout.addWidget(self.r0Input)
        inputsLayout.addWidget(self.rwInput)
        inputsLayout.addWidget(self.lwInput)
        inputsLayout.addWidget(self.tWInput)
        inputsLayout.addWidget(self.drInput)
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        inputsLayout.addWidget(self.buttonBox)

        self.LPlot = Plot(xlabel='$x$, мм', ylabel='$L$, мм')
        self.rPlot = Plot(xlabel='$x$, мм', ylabel='$r$, мкм')
        mainLayout.addWidget(self.LPlot)
        mainLayout.addWidget(self.rPlot)

        self.kInput.valueChanged.connect(self.updateK)
        self.r0Input.valueChanged.connect(self.updateR0)
        self.rwInput.valueChanged.connect(self.updateRw)
        self.lwInput.valueChanged.connect(self.updateLw)
        self.tWInput.valueChanged.connect(self.updateTW)
        self.drInput.valueChanged.connect(self.updateDr)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.updatePlots()
        self.updateOmegaType(self.omegaType)
        
        self.setLayout(mainLayout)

    def updatePlots(self):
        r, omega = getROmega(self.omegaType, self.k)
        Lx, Rx, xMax, _, _ = getLx(r, omega, r0=self.r0, lw=self.lw, rw=self.rw, dr=self.dr)
        x = np.linspace(0, xMax, 100)
        self.LPlot.plot(x, Lx(x))
        self.rPlot.plot(x, Rx(x))

    def updateOmegaType(self, omegaType):
        self.omegaType = omegaType

        if self.omegaType == 'const':
            self.kInput.setPrefix('Ω=')
            self.kInput.setSuffix('mrad')
        elif self.omegaType == 'theta':
            self.kInput.setPrefix('𝚯/=')
            self.kInput.setSuffix('')
        elif self.omegaType == 'nano':
            self.kInput.setPrefix('α=-')
            self.kInput.setSuffix('')

        self.updatePlots()
    def updateK(self, k):
        self.k = k
        self.updatePlots()
    def updateR0(self, r0):
        self.r0 = r0
        self.updatePlots()
    def updateRw(self, rw):
        self.rw = rw
        self.updatePlots()
    def updateLw(self, lw):
        self.lw = lw
        self.updatePlots()
    def updateTW(self, tW):
        self.tW = tW
        self.updatePlots()
    def updateDr(self, dr):
        self.dr = dr
        self.updatePlots()
    