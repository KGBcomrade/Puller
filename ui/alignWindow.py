import typing
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QSlider, QDialog, QDoubleSpinBox, \
     QPushButton, QMessageBox, QLabel, QFrame
from PyQt6.QtCore import Qt

import requests
import cv2
import numpy as np
from misc import getFiberEdges
from .canvas import Canvas

# CV params
dvr_address = 'http://10.201.2.244'
dvr_port = 8090
top_oid = 3
side_oid = 4
top_scale = 10.8
side_scale = 12.7

def getPhoto(oid):
    resp = requests.request('GET', f'{dvr_address}:{dvr_port}/photo.jpg?oid={oid}')
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

        resultWindow = ResultWindow(top1, side1, top2, side2)
        resultWindow.exec()



class ResultWindow(QDialog):
    def __init__(self, top1, side1, top2, side2):
        super().__init__()

        top1a1, top1b1, top1a2, top1b2 = getFiberEdges(top1)
        side1a1, side1b1, side1a2, side1b2 = getFiberEdges(side1)
        top2a1, top2b1, top2a2, top2b2 = getFiberEdges(top2)
        side2a1, side2b1, side2a2, side2b2 = getFiberEdges(side2)

        top1Fig = Canvas()
        top2Fig = Canvas()
        side1Fig = Canvas()
        side2Fig = Canvas()

        x = np.arange(top1.shape[1])
        top1Fig.imshow(top1)
        top1Fig.plot(x, top1a1 * x + top1b1)
        top1Fig.plot(x, top1a2 * x + top1b2)
        top2Fig.imshow(top2)
        top2Fig.plot(x, top2a1 * x + top2b1)
        top2Fig.plot(x, top2a2 * x + top2b2)
        side1Fig.imshow(side1)
        side1Fig.plot(x, side1a1 * x + side1b1)
        side1Fig.plot(x, side1a2 * x + side1b2)
        side2Fig.imshow(side2)
        side2Fig.plot(x, side2a1 * x + side2b1)
        side2Fig.plot(x, side2a2 * x + side2b2)
        

        topFigLayout = QHBoxLayout()
        sideFigLayout = QHBoxLayout()
        mainLayout = QVBoxLayout()
        topFigLayout.addWidget(top1Fig)
        topFigLayout.addWidget(top2Fig)
        sideFigLayout.addWidget(side1Fig)
        sideFigLayout.addWidget(side2Fig)
        mainLayout.addLayout(topFigLayout)
        mainLayout.addLayout(sideFigLayout)

        topLeftEq = QLabel(f'Top left: {top1a1} * x + {top1b1}, {top1a2} * x + {top1b2}')
        topRightEq = QLabel(f'Top right: {top2a1} * x + {top2b1}, {top2a2} * x + {top2b2}')
        sideLeftEq = QLabel(f'Side left: {side1a1} * x + {side1b1}, {side1a2} * x + {side1b2}')
        sideRightEq = QLabel(f'Side right: {side2a1} * x + {side2b1}, {side2a2} * x + {side2b2}')
        
        topShift = (top1b1 + top1b2) / 2 - (top2b1 + top2b2) / 2
        sideShift = (side1b1 + side1b2) / 2 - (side2b1 + side2b2) / 2
        topShiftLabel = QLabel(f'Top shift: {topShift * top_scale} um ({topShift} px)')
        sideShiftLabel = QLabel(f'Side shift: {sideShift * side_scale} um ({sideShift} px)')

        labelLayout = QVBoxLayout()
        labelLayout.addWidget(topLeftEq)
        labelLayout.addWidget(topRightEq)
        labelLayout.addWidget(sideLeftEq)
        labelLayout.addWidget(sideRightEq)
        labelLayout.addWidget(topShiftLabel)
        labelLayout.addWidget(sideShiftLabel)
        labelFrame = QFrame()
        labelFrame.setLayout(labelLayout)
        mainLayout.addWidget(labelFrame)

        exitButton = QPushButton('Выход')
        exitButton.released.connect(self.accept)
        mainLayout.addWidget(exitButton)

        self.setLayout(mainLayout)