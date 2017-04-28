import random
import threading
import time
import math

import signal
import sys
import socket

from observer import *
from model import *
from builder import *



airports_builder = AirportsBuilder()



for i in range(10):
	lat = random.randint(0, 180)
	lon = random.randint(0, 180)
	cap = random.randint(0, 10)
	airports_builder.add(i, lat, lon, cap)
	

AIRPORT_SCHEMA = airports_builder.build()
		

#cd Desktop\airport && python model.py
count = int(sys.argv[1])
addr = sys.argv[2]
port = int(sys.argv[3])
		
plains = []
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((addr, port))
#s.send(MESSAGE)

#o1 = LoggingObserver()
o1 = NetworkPushObserver(s)

for i in range(0,count):
	a_id = random.randint(0,9)	
	plain = Plain(i,a_id)
	plain.AIRPORT_SCHEMA = AIRPORT_SCHEMA
	plains.append(plain)
	plain.addObserver(o1)
	plain.run()
	
def signal_handler(signal, frame):
	for plain in plains:
		plain.stop()
		print("plain " + str(plain.id) + " stopped")
	s.close()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

while True:
	pass