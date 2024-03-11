import sys
from PyQt6.QtWidgets import QApplication
import asyncio
import qasync
from ui import MainWindow


app = QApplication(sys.argv)

loop = qasync.QEventLoop(app)
asyncio.set_event_loop(loop)

# without hardware init
noHardware = ('--no-hardware' in sys.argv)

mainWindow = MainWindow(hardware = not noHardware)
mainWindow.show()

with loop:
    loop.run_forever()