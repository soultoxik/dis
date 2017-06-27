#radar collision
from model import *
from observer import *
import sys


rr = Transmitter(sys.argv[1],int(sys.argv[2]))

rcs_ip = sys.argv[3]
rcs_port = int(sys.argv[4])

rrc_ip = sys.argv[5]
rrc_port = int(sys.argv[6])

rcs_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
rcs_socket.connect((rcs_ip, rcs_port))


rrc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
rrc_socket.connect((rrc_ip, rrc_port))


rr_observer = RadarResolverObserver(rcs_socket, rrc_socket, sys.argv[1], int(sys.argv[2]))

rr.addObserver(rr_observer)


def signal_handler(signal, frame):
    rr.stop()

    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


rr.run()
while True:
    pass



