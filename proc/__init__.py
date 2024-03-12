import sys

if '--no-hardware' in sys.argv:
    from .simProc import SimProc as Proc
else:
    from .hardwareProc import HardwareProc as Proc