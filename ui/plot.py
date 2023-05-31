from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,\
     QSlider, QDial, QProgressBar, QLineEdit, QDialog, QDialogButtonBox, QGridLayout, QCheckBox, QDoubleSpinBox, QFrame
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QLocale
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

class Plot(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=10, height=8, dpi=100, xlabel=None, ylabel=None) -> None:
        super(QWidget, self).__init__(parent)
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(FigureCanvasQTAgg, self).__init__(fig)
        self.xlabel = xlabel
        self.ylabel = ylabel
        
        

    def plot(self, x, y):
        self.axes.clear()
        self.axes.plot(x, y)
        self.axes.grid()
        
        if self.xlabel is not None:
            self.axes.set_xlabel(xlabel=self.xlabel)
        if self.ylabel is not None:
            self.axes.set_ylabel(ylabel=self.ylabel)
        
        self.draw_idle()