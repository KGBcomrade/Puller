import typing
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,\
     QSlider, QDial, QProgressBar, QLineEdit, QDialog, QDialogButtonBox, QGridLayout, QCheckBox, QDoubleSpinBox, QFrame
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QLocale

class FinishWindow(QDialog):
    def __init__(self, stretchFunction: typing.Callable, moveFuntion: typing.Callable) -> None:
        super().__init__()

        self._stretchFunction = stretchFunction
        self._moveFunction = moveFuntion

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        self.saveCheckBox = QCheckBox('Сохранить данные')
        self.stretchButton = QPushButton('Доп. растяжка')
        self.moveButton = QPushButton('Переместить раму вправо')
        self.exitButton = QPushButton('ОК')
        
        mainLayout.addWidget(self.saveCheckBox)
        mainLayout.addWidget(self.stretchButton)
        mainLayout.addWidget(self.moveButton)
        mainLayout.addWidget(self.exitButton)

    def _setButtonsEnabled(self, enabled):
        self.stretchButton.setEnabled(enabled)
        self.moveButton.setEnabled(enabled)
        self.exitButton.setEnabled(enabled)

    def _stretch(self):
        self._setButtonsEnabled(False)
        self._stretchFunction()
        self._setButtonsEnabled(True)

    def _move(self):
        self._setButtonsEnabled(False)
        self._moveFunction()
        self.exitButton.setEnabled(True)

    def _exit(self):
        if self.saveCheckBox.isChecked():
            #TODO save data
            pass

        self.accept()
