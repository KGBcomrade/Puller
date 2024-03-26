from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog, QDialogButtonBox, QDoubleSpinBox, QComboBox
import numpy as np

from ui import Plot
from misc import getLx, omegaTypes

class SetupWindow(QDialog):
    def __init__(self, omegaType = 'theta', r0 = 62.5, **kwargs) -> None:
        super().__init__()

        self.omegaType = omegaType
        self.rw = kwargs['rw']
        self.lw = kwargs['lw']
        self.r0 = r0
        self.k = kwargs['k']
        self.tW = kwargs['tW']
        self.dr = kwargs['dr']
        self.omega = kwargs['omega']
        self.x = kwargs['x']
        self.L0 = kwargs['L0']
        self.alpha = kwargs['alpha']
        self.x0 = kwargs['x0']

        mainLayout = QHBoxLayout()
        inputsLayout = QVBoxLayout()
        mainLayout.addLayout(inputsLayout)

        self.omegaTypesCB = QComboBox()
        self.omegaTypesCB.addItems(omegaTypes)
        self.omegaTypesCB.textActivated.connect(self.updateOmegaType)
        self.omegaTypesCB.setCurrentText(self.omegaType)

        self.kInput = QDoubleSpinBox(prefix='𝚯/=')
        self.kInput.setMaximum(20)
        self.kInput.setMinimum(.01)
        self.kInput.setValue(self.k)
        self.omegaInput = QDoubleSpinBox(prefix='Ω=', suffix='мрад')
        self.omegaInput.setMinimum(.01)
        self.omegaInput.setMaximum(100)
        self.omegaInput.setValue(self.omega)
        self.xInput = QDoubleSpinBox(prefix='x=', suffix='мм')
        self.xInput.setMinimum(1)
        self.xInput.setMaximum(100)
        self.xInput.setValue(self.x)
        self.L0Input = QDoubleSpinBox(prefix='L₀=', suffix='мм')
        self.L0Input.setMinimum(0)
        self.L0Input.setMaximum(10)
        self.L0Input.setValue(self.L0)
        self.alphaInput = QDoubleSpinBox(prefix='α=')
        self.alphaInput.setMinimum(-1)
        self.alphaInput.setMaximum(1)
        self.alphaInput.setValue(self.alpha)
        self.r0Input = QDoubleSpinBox(prefix='r0=', suffix=' мкм')
        self.r0Input.setMaximum(62.5)
        self.r0Input.setValue(r0)
        self.rwInput = QDoubleSpinBox(prefix='rw=', suffix=' мкм')
        self.rwInput.setValue(self.rw)
        self.lwInput = QDoubleSpinBox(prefix='lw=', suffix=' мм')
        self.lwInput.setValue(self.lw)
        self.tWInput = QDoubleSpinBox(prefix='tW=', suffix='с')
        self.tWInput.setMinimum(0)
        self.tWInput.setMaximum(500)
        self.tWInput.setValue(self.tW)
        self.drInput = QDoubleSpinBox(prefix='dr=')
        self.drInput.setMaximum(2)
        self.drInput.setMinimum(.001)
        self.drInput.setValue(self.dr)
        self.x0Input = QDoubleSpinBox(prefix='x0=', suffix='мм')
        self.x0Input.setMaximum(30)
        self.x0Input.setMinimum(0)
        self.x0Input.setValue(self.x0)
        inputsLayout.addWidget(self.omegaTypesCB)
        inputsLayout.addWidget(self.kInput)
        inputsLayout.addWidget(self.omegaInput)
        inputsLayout.addWidget(self.xInput)
        inputsLayout.addWidget(self.L0Input)
        inputsLayout.addWidget(self.alphaInput)
        inputsLayout.addWidget(self.r0Input)
        inputsLayout.addWidget(self.rwInput)
        inputsLayout.addWidget(self.lwInput)
        inputsLayout.addWidget(self.tWInput)
        inputsLayout.addWidget(self.drInput)
        inputsLayout.addWidget(self.x0Input)
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        inputsLayout.addWidget(self.buttonBox)

        self.LPlot = Plot(xlabel='$x$, мм', ylabel='$L$, мм')
        self.rPlot = Plot(xlabel='$x$, мм', ylabel='$r$, мкм')
        mainLayout.addWidget(self.LPlot)
        mainLayout.addWidget(self.rPlot)

        self.kInput.valueChanged.connect(self.updateK)
        self.omegaInput.valueChanged.connect(self.updateOmega)
        self.xInput.valueChanged.connect(self.updateX)
        self.L0Input.valueChanged.connect(self.updateL0)
        self.alphaInput.valueChanged.connect(self.updateAlpha)
        self.r0Input.valueChanged.connect(self.updateR0)
        self.rwInput.valueChanged.connect(self.updateRw)
        self.lwInput.valueChanged.connect(self.updateLw)
        self.tWInput.valueChanged.connect(self.updateTW)
        self.drInput.valueChanged.connect(self.updateDr)
        self.x0Input.valueChanged.connect(self.updateX0)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.altInputs = [self.kInput, self.omegaInput, self.xInput, self.L0Input, self.alphaInput, self.lwInput, self.rwInput, self.drInput]
        self.altInputsMap = {
            'theta': [self.kInput, self.lwInput, self.rwInput, self.drInput],
            'const': [self.omegaInput, self.lwInput, self.rwInput, self.drInput],
            'nano': [self.xInput, self.L0Input, self.alphaInput]
        }

        self.updatePlots()
        self.updateOmegaType(self.omegaType)
        
        self.setLayout(mainLayout)

    def updatePlots(self):
        Lx, Rx, xMax, _, _ = getLx(self.omegaType, r0=self.r0, lw=self.lw, rw=self.rw, dr=self.dr, k=self.k, omega=self.omega, x=self.x, L0=self.L0, alpha=self.alpha)
        x = np.linspace(0, xMax, 100)
        self.LPlot.plot(x, Lx(x))
        self.rPlot.plot(x, Rx(x))

    def updateOmegaType(self, omegaType):
        self.omegaType = omegaType
        for w in self.altInputs:
            w.hide()
        for w in self.altInputsMap[omegaType]:
            w.show()

        self.updatePlots()
    def updateK(self, k):
        self.k = k
        self.updatePlots()
    def updateOmega(self, omega):
        self.omega = omega
        self.updatePlots()
    def updateX(self, x):
        self.x = x
        self.updatePlots()
    def updateL0(self, L0):
        self.L0 = L0
        self.updatePlots()
    def updateAlpha(self, alpha):
        self.alpha = alpha
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
    def updateX0(self, x0):
        self.x0 = x0
    