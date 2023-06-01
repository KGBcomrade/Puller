from ui import BurnerSetupWindow
from PyQt6.QtWidgets import QMessageBox
import asyncio, qasync

lock = asyncio.Lock()

async def _waitWindow(message: str, proc):
    waitWindow = QMessageBox(QMessageBox.Icon.Information, 'Подожди...', message, QMessageBox.StandardButton.NoButton)
    waitWindow.show()
    await proc()
    waitWindow.accept()

async def simLongProc():
    await asyncio.sleep(2)

async def simShortProc():
    await asyncio.sleep(.2)

async def homing():
    # warning
    async with lock:
        warning = QMessageBox(QMessageBox.Icon.Warning, 'Внимание!', 'Проверь, что раме не мешают другие подвижки и нажми ОК', 
                            QMessageBox.StandardButton.No | QMessageBox.StandardButton.Ok)
        if warning.exec() == QMessageBox.StandardButton.No:
            return -1
        
        # homing
        await _waitWindow('Выполняется поиск нуля...', simLongProc)
        # waitWindow = QMessageBox(QMessageBox.Icon.Information, 'Подожди', 'Выполняется поиск нуля...', QMessageBox.StandardButton.NoButton)
        # waitWindow.show()
        # await asyncio.sleep(2)
        # waitWindow.accept()


    return 0

async def MTS():
    await _waitWindow('Свдиг подвижек на начальные позиции...', simLongProc)

async def burnerSetup():
    # wait until move under the camera
    # await WaitWindow.create('Горелка подводится под камеру...')
    await _waitWindow('Горелка подводится под камеру...', simLongProc)
    
    # setup
    setupWindow = BurnerSetupWindow(0)
    setupWindow.exec()

    # wait until move back
    # await WaitWindow.create('Горелка отводится назад...')
    await _waitWindow('Горелка отводится назад...', simLongProc)

async def HHOOn():
    print('HHO On')
    pass

async def HHOOff():
    print('HHO Off')
    pass

async def ignite():
    # warning
    warning = QMessageBox(QMessageBox.Icon.Warning, 'Внимание!', 'Убедись, что поток смеси достиг 21% на РРГ и нажми ОК', 
                          QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
    if warning.exec() == QMessageBox.StandardButton.No:
        return -1
    
    # ignition
    repeatition = QMessageBox(QMessageBox.Icon.Question, 'Повторить?', 'Повторить поджиг?', 
                              QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
    while True:
        pass # TODO add ignition
        if repeatition.exec() == QMessageBox.StandardButton.No: # check if ignited
            break


async def extinguish():
    repeatition = QMessageBox(QMessageBox.Icon.Question, 'Повторить?', 'Повторить тушение?', 
                              QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
    while True:
        pass # TODO add extinguishing
        if repeatition.exec() == QMessageBox.StandardButton.No: # check if extinguished
            break   
