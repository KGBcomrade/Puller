import datetime
import os
import asyncio

import numpy as np
from devices import DSO_X2002A

class PowerPlot:
    def __init__(self, address = 'USB0::0x0957::0x179B::MY54491022::INSTR') -> None:
        self.osc = DSO_X2002A(address)  #('USB0::2391::6043::MY54490944::INSTR')

        self.osc.set_y_scale(5)
        self.osc.conn.write(":CHANnel1:OFFSet 18")
        self.osc.set_x_scale(0.1)
        self.osc.conn.write(':TIMebase:POSition 0.000')
        self.osc.conn.write(':TIMebase:REFerence LEFT')
        self.osc.conn.write(':ACQuire:TYPE HRES')

        self.osc.conn.write(':STOP')
        
        self.osc.set_y_scale(5)
        self.osc.set_x_scale(20) # (meast*0.1)
        self.osc.conn.write(":CHANnel1:OFFSet 18")
        self.osc.conn.write(':TIMebase:POSition 0.000')
        self.osc.conn.write(':TIMebase:REFerence LEFT')
        self.osc.conn.write(':ACQuire:TYPE HRES')
        self.osc.conn.write(':WAVeform:SOURce CHAN{}'.format(1))
        self.osc.conn.write(":WAVeform:FORMat {}".format('WORD'))
        self.osc.conn.write(":WAVeform:BYTeorder MSBFirst")
        self.osc.conn.write(':WAVeform:POINts:MODE RAW')
        self.osc.conn.write(":WAVeform:POINts 10000")

    def run(self):
        self.osc.conn.write(':RUN')
        self.osc.conn.write(':TRIG:FORC')
    
    def stop(self):
        self.osc.conn.write(':STOP')

    async def save(self, pathDat):
        folderName = str(datetime.date.today())


        fullname = os.path.join(pathDat,folderName)
        for e in fullname:
            if os.path.exists(os.path.join(pathDat,folderName)):
                pass
            else:
                os.mkdir(os.path.join(pathDat,folderName))
        u = 1
        names = os.listdir(os.path.join(pathDat,folderName))

        for e in names:
            if os.path.exists(os.path.join(fullname,"".join([str(u),".csv"]))):
                u += 1
            else: break

        name = os.path.join(fullname,"".join([str(u),".csv"]))
        self.osc.conn.write(':WAVeform:DATA?')
        await asyncio.sleep(5)
        raw_data = self.osc.conn.read_raw()
        await asyncio.sleep(5.3)
        raw_data3 = [raw_data[i:i + 2] for i in range(10, len(raw_data) - 1, 2)]  # split raw to pair
        int_list = list(map(lambda x: int.from_bytes(x, byteorder='big'), raw_data3))
        int_list = np.array(int_list)
        YINCrement = float(self.osc.conn.query(':WAVeform:YINCrement?'))
        YORigin = float(self.osc.conn.query(':WAVeform:YORigin?'))
        XINCrement = float(self.osc.conn.query(':WAVeform:XINCrement?'))
        XORigin = float(self.osc.conn.query(':WAVeform:XORigin?'))
        YReference = float(self.osc.conn.query(":WAVeform:YREFerence?"))
        Y_waveform = (int_list - YReference) * YINCrement + YORigin
        X_waveform = np.arange(0, len(int_list)) * XINCrement + XORigin
        listData = Y_waveform # X_waveform

        current_datetime = str(datetime.datetime.now())
        current_datetime = current_datetime.replace(":"," ")


        await asyncio.sleep(3)
        # Save waveform data values to CSV file.
        # TODO save params
        with open(name, 'w') as f:
            for i in range(0,len(listData)):
                # time_val = x_origin + (i * x_increment)
                # voltage = ((listData[i] - y_reference) * y_increment) + y_origin
                f.write("%E, %f\n" % (X_waveform[i], listData[i]))
