import typing
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QSlider, QDialog, QDialogButtonBox, QDoubleSpinBox, \
     QButtonGroup, QRadioButton
from PyQt6.QtCore import Qt

class MoveApartWindow(QDialog):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle('Разъезд подвижек')

        mainLayout = QVBoxLayout()
        self.coordSlider = QSlider(orientation=Qt.Orientation.Horizontal)
        self.coordSpinBox = QDoubleSpinBox()
        coordLayout = QHBoxLayout()
        coordLayout.addWidget(self.coordSlider)
        coordLayout.addWidget(self.coordSpinBox)
        radioGroup = QButtonGroup()
        self.leftRB = QRadioButton('Левая')
        self.rightRB = QRadioButton('Правая')
        self.allRB = QRadioButton('Обе')
        radioGroup.addButton(self.leftRB)
        radioGroup.addButton(self.rightRB)
        radioGroup.addButton(self.allRB)
        rbLayout = QHBoxLayout()
        rbLayout.addWidget(self.leftRB)
        rbLayout.addWidget(self.rightRB)
        rbLayout.addWidget(self.allRB)
        self.allRB.setChecked(True)

        btns = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.dialogButtonBox = QDialogButtonBox(btns)

        self.dialogButtonBox.accepted.connect(self.accept)
        self.dialogButtonBox.rejected.connect(self.reject)

        mainLayout.addLayout(coordLayout)
        mainLayout.addLayout(rbLayout)
        mainLayout.addWidget(self.dialogButtonBox)

        self.setLayout(mainLayout)

        self.coordSlider.valueChanged.connect(self._updateCoord)
        self.coordSpinBox.valueChanged.connect(self._setValue)

        self.coordSpinBox.setMaximum(50)
        self.coordSpinBox.setMinimum(0)
        
        self.coord = 50
        self.coordSpinBox.setValue(self.coord)
        
    def _updateCoord(self):
        self.coord = self.coordSlider.value() / 2
        self.coordSpinBox.setValue(self.coord)

    def _setValue(self, value: typing.SupportsFloat):
        self.coord = value
        self.coordSlider.setValue(int(self.coord * 2))

    def getMotors(self):
        '''
        Returns (left, right) bool tuple
        '''
        return (self.leftRB.isChecked() or self.allRB.isChecked(), self.rightRB.isChecked() or self.allRB.isChecked())