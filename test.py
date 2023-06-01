import sys
from PyQt6.QtWidgets import QApplication
import asyncio
import qasync
from ui import MainWindow

app = QApplication(sys.argv)
loop = qasync.QEventLoop(app)
asyncio.set_event_loop(loop)

w = MainWindow()
w.show()

with loop:
    loop.run_forever()
