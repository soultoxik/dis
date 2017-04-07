import random
import threading
import time

import signal
import sys

class Publisher:
	
	def __init__(self):
		self.observers = []
		self.stopEvent = threading.Event()
		self.thread = threading.Thread(target=self.proc, args=[self.stopEvent])
		
	def proc(self, event):
		while not event.wait(1):
			data = self.publish()
			for observer in self.observers:
				observer.onPublish(data)
	def publish(self):
		pass
	def run(self):
		self.thread.start()
	def stop(self):
		self.stopEvent.set()
		self.thread.join()
	def addObserver(self, observer):
		self.observers.append(observer)

class Plain(Publisher):
	def __init__(self, id):
		super(Plain, self).__init__()
		self.id = id
		
	def publish(self):
		lat = random.randint(0, 180)
		lon = random.randint(0, 180)
		return {'id': self.id, 'lat': lat, 'lon': lon}
		
		
class Observer:
	def onPublish(self, data):
		pass

class LoggingObserver(Observer):
	def onPublish(self, data):
		print(data)

#cd Desktop\airport && python model.py
count = int(sys.argv[1])
		
plains = []
o1 = LoggingObserver()

for i in range(0,count):
	plain = Plain(i)
	plains.append(plain)
	plain.addObserver(o1)
	plain.run()
	
def signal_handler(signal, frame):
	for plain in plains:
		plain.stop()
		print("plain " + str(plain.id) + " stopped")
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

while True:
	pass