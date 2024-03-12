import sys
if '--no-hardware' in sys.argv:
    from .motor import Motor
else:
    from .dds220m import DDS220M
    from .powerPlot import PowerPlot
    from .standa import StandaMotor
    from .vcontrol import VControl