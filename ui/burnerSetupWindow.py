import typing
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,\
     QSlider, QDial, QProgressBar, QLineEdit, QDialog, QDialogButtonBox, QGridLayout, QCheckBox, QDoubleSpinBox, QFrame
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QLocale
from PyQt6.QtGui import QIntValidator, QDoubleValidator
import asyncio
from qasync import asyncSlot

def simulateMovement(pos):
    print(pos)

def getDoubleValidator():
    validator = QDoubleValidator()
    validator.setLocale(QLocale("en_US"))
    return validator

class BurnerSetupWindow(QDialog):
    def __init__(self, position: typing.SupportsFloat, stretchFunction: typing.Callable, movementFunction: typing.Callable= simulateMovement, 
                 step: typing.SupportsFloat = 0.01) -> None:
        super().__init__()
        self.setWindowTitle('Настройка подвода горелки')

        self.position = position
        self._movementFunction = movementFunction
        self.step = step

        mainLayout = QVBoxLayout()
        
        self.setLayout(mainLayout)

        mainLayout.addWidget(QLabel('Настрой положение горелки по камере'))

        inputLayout = QHBoxLayout()
        self.positionIntput = QLineEdit(str(self.position))
        self.positionIntput.setValidator(getDoubleValidator())
        self.upButton = QPushButton('Вверх')
        self.downButton = QPushButton('Вниз')
        inputLayout.addWidget(self.positionIntput)
        inputLayout.addWidget(self.upButton)
        inputLayout.addWidget(self.downButton)
        mainLayout.addLayout(inputLayout)

        self.stretchButton = QPushButton('Растянуть на шаг')
        mainLayout.addWidget(self.stretchButton)

        self.okButton = QPushButton('Ok')
        mainLayout.addWidget(self.okButton)

        self.okButton.released.connect(self.accept)
        self.upButton.released.connect(self._increasePosition)
        self.downButton.released.connect(self._decreasePosition)
        self.positionIntput.returnPressed.connect(self._onPositionChanged)

    def _setButtonsEnabled(self, enabled: bool):
        self.upButton.setEnabled(enabled)
        self.downButton.setEnabled(enabled)
        self.okButton.setEnabled(enabled)

    def _stretch(self):
        self.stretchButton.setEnabled(False)
        self._stretch()
        self.stretchButton.setEnabled(True)

    def _move(self):
        self._setButtonsEnabled(False)
        self._movementFunction(self.position)
        self._setButtonsEnabled(True)

    def _onPositionChanged(self):
        self.position = float(self.positionIntput.text())
        self._move()

    def _increasePosition(self):
        self.position += self.step
        self.position = round(self.position, 5)
        self.positionIntput.setText(str(self.position))
        self._move()

    def _decreasePosition(self):
        self.position -= self.step
        self.position = round(self.position, 5)
        self.positionIntput.setText(str(self.position))
        self._move()


