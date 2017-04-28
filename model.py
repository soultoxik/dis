import random
import threading
import time
import math

import signal
import sys

import json


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
	V = 4
	AIRPORT_SCHEMA = None
	
	def __init__(self, id, airport_id):
		super(Plain, self).__init__()
		self.id = id
		self.airport_id = airport_id
		self.lat = random.randint(0, 180)
		self.lon = random.randint(0, 180)
	
	
	def angle(self, x1, y1, x2, y2):
		a = math.atan2(y2 - y1, x2 - x1) / math.pi * 180
		
		return a
	
	
	
		
	def publish(self):
		schema = self.AIRPORT_SCHEMA[self.airport_id]

		a_lat = schema['lat']
		a_lon = schema['lon']
		a = self.angle(self.lat, self.lon, a_lat, a_lon)
	
		new_lat = self.lat + self.V * math.cos(math.radians(a))
		new_lon = self.lon + self.V * math.sin(math.radians(a))
		self.lat = new_lat
		self.lon = new_lon
		return {
			'id':self.id,
			'lat':new_lat,
			'lon':new_lon,
			'airport_id':self.airport_id
		}
