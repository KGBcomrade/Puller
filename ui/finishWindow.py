import typing
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,\
     QSlider, QDial, QProgressBar, QLineEdit, QDialog, QDialogButtonBox, QGridLayout, QCheckBox, QDoubleSpinBox, QFrame
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QLocale

class FinishWindow(QDialog):
    def __init__(self, stretchFunction: typing.Callable) -> None:
        super().__init__()

        self._stretchFunction = stretchFunction

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        self.saveCheckBox = QCheckBox('Сохранить данные')
        self.mongoDBCheckBox = QCheckBox('Загрузить в MongoDB')
        self.mongoDBCheckBox.setEnabled(False)
        self.moveCheckBox = QCheckBox('Сместить раму вправо')
        self.stretchButton = QPushButton('Доп. растяжка')
        self.exitButton = QPushButton('ОК')
        
        mainLayout.addWidget(self.saveCheckBox)
        mainLayout.addWidget(self.mongoDBCheckBox)
        mainLayout.addWidget(self.moveCheckBox)
        mainLayout.addWidget(self.stretchButton)
        mainLayout.addWidget(self.exitButton)

        self.saveCheckBox.stateChanged.connect(self._onSaveCheckChanged)
        self.stretchButton.released.connect(self._stretch)
        self.exitButton.released.connect(self.accept)

    def _onSaveCheckChanged(self):
        self.mongoDBCheckBox.setChecked(False)
        self.mongoDBCheckBox.setEnabled(self.saveCheckBox.isChecked())

    def _setButtonsEnabled(self, enabled):
        self.stretchButton.setEnabled(enabled)
        self.exitButton.setEnabled(enabled)

    def _stretch(self):
        self._setButtonsEnabled(False)
        self._stretchFunction()
        self._setButtonsEnabled(True)