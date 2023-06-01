import sys
import asyncio
import qasync

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,\
     QSlider, QDial, QProgressBar, QLineEdit, QDialog, QDialogButtonBox, QGridLayout, QCheckBox
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QLocale

from ui import MainWindow


app = QApplication(sys.argv)

loop = qasync.QEventLoop(app)
asyncio.set_event_loop(loop)

mainWindow = MainWindow()
mainWindow.show()

with loop:
    loop.run_forever()