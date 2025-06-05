import typing
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QSlider, QDialog, QDoubleSpinBox, \
     QPushButton, QMessageBox
from PyQt6.QtCore import Qt

import requests
import cv2
import numpy as np
from misc import getFiberEdges

# CV params
dvr_address = 'http://10.201.2.244'
dvr_port = 8090
top_oid = 3
side_oid = 4

def getPhoto(oid):
    resp = requests.request('GET', f'{dvr_address}:{dvr_port}/photo.jpg?oid={top_oid}')
    nar = np.fromstring(resp.content, np.uint8)
    return cv2.imdecode(nar, cv2.IMREAD_GRAYSCALE)


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

        self.autoButton = QPushButton('Авто...')
        self.exitButton = QPushButton('Выход')

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(coordLayout)
        mainLayout.addLayout(moveLayout)
        mainLayout.addWidget(self.autoButton)
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
        
        self.autoButton.released.connect(self._auto)
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
        
        wait = QMessageBox(QMessageBox.Icon.Information, 'Подожди', 'Подвижки разводятся в разные стороны...', QMessageBox.StandardButton.NoButton)
        wait.setStandardButtons(QMessageBox.StandardButton.NoButton)
        wait.show()
        self.moveApartFunc(self.coord)
        wait.accept()
        self.realCoord = self.coord

    def _moveMMCenter(self):
        self.moveMainMotorFunc(self.mainMotorAlignCoord)
    
    def _moveMMLeft(self):
        self.moveMainMotorFunc(self.mainMotorAlignCoord + self.gapLength / 2 + self.realCoord)
    
    def _moveMMRight(self):
        self.moveMainMotorFunc(self.mainMotorAlignCoord - self.gapLength / 2 - self.realCoord)

    def _auto(self):
        self._moveMMLeft()
        top1 = getPhoto(top_oid)
        side1 = getPhoto(side_oid)
        self._moveMMRight()
        top2 = getPhoto(top_oid)
        side2 = getPhoto(side_oid)

        top1a1, top1b1, top1a2, top1b2 = getFiberEdges(top1)
        side1a1, side1b1, side1a2, side1b2 = getFiberEdges(side1)
        top2a1, top2b1, top2a2, top2b2 = getFiberEdges(top2)
        side2a1, side2b1, side2a2, side2b2 = getFiberEdges(side2)

        print(f'top left: {top1a1} * x + {top1b1}, {top1a2} * x + {top1b2}')
        print(f'top right: {top2a1} * x + {top2b1}, {top2a2} * x + {top2b2}')
        print(f'side left: {side1a1} * x + {side1b1}, {side1a2} * x + {side1b2}')
        print(f'side right: {side2a1} * x + {side2b1}, {side2a2} * x + {side2b2}')

        print(f'top shift: {(top1b1 + top1b2) / 2 - (top2b1 + top2b2) / 2}')
        print(f'side shift: {(side1b1 + side1b2) / 2 - (side2b1 + side2b2) / 2}')