import typing
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QSlider, QDialog, QDoubleSpinBox, \
     QPushButton, QMessageBox
from PyQt6.QtCore import Qt

class AlignWindow(QDialog):
    def __init__(self, moveApartFunc, moveMainMotorFunc, mainMotorAlignCoord, gapLength) -> None:
        super().__init__()

        self.moveApartFunc = moveApartFunc
        self.moveMainMotorFunc = moveMainMotorFunc
        self.mainMotorAlignCoord = mainMotorAlignCoord
        self.gapLength = gapLength
        
        self.setWindowTitle('Юстировка')


        self.coordSlider = QSlider(orientation=Qt.Orientation.Horizontal)
        self.coordSpinBox = QDoubleSpinBox()
        self.coordSetButton = QPushButton('Развести')
        coordLayout = QHBoxLayout()
        coordLayout.addWidget(self.coordSlider)
        coordLayout.addWidget(self.coordSpinBox)
        coordLayout.addWidget(self.coordSetButton)

        self.leftButton = QPushButton('Левый край')
        self.centerButton = QPushButton('Центр')
        self.rightButton = QPushButton('Правый край')
        moveLayout = QHBoxLayout()
        moveLayout.addWidget(self.leftButton)
        moveLayout.addWidget(self.centerButton)
        moveLayout.addWidget(self.rightButton)

        self.exitButton = QPushButton('Выход')

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(coordLayout)
        mainLayout.addLayout(moveLayout)
        mainLayout.addWidget(self.exitButton)

        self.setLayout(mainLayout)

        self.coord = 0
        self.realCoord = 0
        self.coordSpinBox.setValue(self.coord)
        self.coordSpinBox.setValue(self.coord)

        self.coordSlider.valueChanged.connect(self._updateCoord)
        self.coordSpinBox.valueChanged.connect(self._setValue)

        self.coordSetButton.released.connect(self._moveApart)

        self.leftButton.released.connect(self._moveMMLeft)
        self.centerButton.released.connect(self._moveMMCenter)
        self.rightButton.released.connect(self._moveMMRight)
        
        self.exitButton.released.connect(self.accept)


    def _updateCoord(self):
        self.coord = self.coordSlider.value() / 2
        self.coordSpinBox.setValue(self.coord)

    def _setValue(self, value: typing.SupportsFloat):
        self.coord = value
        self.coordSlider.setValue(int(self.coord * 2))

    def _moveApart(self):
        warning = QMessageBox(QMessageBox.Icon.Warning, 'Внимание!', 'Убери волокно и нажми ОК', 
                            QMessageBox.StandardButton.No | QMessageBox.StandardButton.Ok)
        if warning.exec() == QMessageBox.StandardButton.No:
            return -1
        
        self.moveApartFunc(self.coord)
        self.realCoord = self.coord

    def _moveMMCenter(self):
        self.moveMainMotorFunc(self.mainMotorAlignCoord)
    
    def _moveMMLeft(self):
        self.moveMainMotorFunc(self.mainMotorAlignCoord - self.gapLength / 2 - self.realCoord)
    
    def _moveMMRight(self):
        self.moveMainMotorFunc(self.mainMotorAlignCoord + self.gapLength / 2 + self.realCoord)