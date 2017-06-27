#radar collision coordinator
from model import *
from observer import *
import sys


rrc_ip = sys.argv[1]
rrc_port = int(sys.argv[2])


rrc = Transmitter(rrc_ip, rrc_port)
rrc_observer = RoundRobinBalancer()
rrc.addObserver(rrc_observer)



def signal_handler(signal, frame):
    rrc.stop()

    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

rrc.run()
while True:
    pass

