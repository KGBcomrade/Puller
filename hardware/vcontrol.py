from StepMotorSupply import DP831A
import time
import asyncio


rigol_i1 = 0.1 	# Rigol
rigol_v1 = 5	# Rigol

rigol_i2 = 1    # Rigol
rigol_v2 = 24	# Rigol

rigol_i3 = 1	# Rigol
rigol_v3 = 12	# Rigol

class VControl:
    def __init__(self, address='USB0::0x1AB1::0x0E11::DP8A221000017::INSTR') -> None:
        self.rigol = DP831A(address)
        time.sleep(.1)
        # Ignition
        self.rigol.say(':INST CH1')
        self.rigol.say(f':CURR {rigol_i1}')
        self.rigol.say(f':VOLT {rigol_v1}')
        # HHO generator
        self.rigol.say(':INST CH2')
        self.rigol.say(f':CURR {rigol_i2}')
        self.rigol.say(f':VOLT {rigol_v2}')
        # Extinguishing
        self.rigol.say(':INST CH3')
        self.rigol.say(f':CURR {rigol_i3}')
        self.rigol.say(f':VOLT {rigol_v3}')
        time.sleep(.05)

    def setHHOGenerationEnabled(self, enabled):
        command = 'ON' if enabled else 'OFF'
        self.rigol.say(f':OUTP CH2,{command}')

    async def ignite(self, interval = 1):
        self.rigol.say(':OUTP CH1,ON')
        await asyncio.sleep(interval)
        self.rigol.say(':OUTP CH1,OFF')

    async def extinguish(self, fixmov, delay=20, interval=1):
        valveTask = asyncio.create_task(fixmov.valveDelay(delay))
        self.rigol.say(':OUTP CH3,ON')
        await valveTask
        await asyncio.sleep(interval)
        self.rigol.say(':OUTP CH3,OFF')
        fixmov.valveClose()