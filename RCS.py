#radar configuration server
from model import *
from observer import *
import sys


rcs = Transmitter(sys.argv[1],int(sys.argv[2]))

rcs_observer = RadarConfigurationObserver()

rcs.addObserver(rcs_observer)


def signal_handler(signal, frame):
    rcs.stop()

    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


rcs.run()
while True:
    pass



