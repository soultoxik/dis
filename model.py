import random
import threading
import time
import math

import signal
import sys

import json

import select, socket, sys, queue
import sys

import signal
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

class Transmitter(Publisher):
	def __init__(self, TCP_IP, TCP_PORT, BUFFER_SIZE = 100):
		super(Publisher, self).__init__()
		self.TCP_IP = TCP_IP
		self.TCP_PORT = TCP_PORT
		self.BUFFER_SIZE = BUFFER_SIZE  # Normally 1024, but we want fast response

	def proc(self, event):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setblocking(0)
		server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
		server.bind((self.TCP_IP, self.TCP_PORT))
		server.listen(1)
		inputs = [server]
		outputs = []
		message_queues = {}

		while inputs and event.wait(1):
			readable, writable, exceptional = select.select(
				inputs, outputs, inputs)
			for s in readable:
				if s is server:
					connection, client_address = s.accept()
					connection.setblocking(0)
					inputs.append(connection)
					message_queues[connection] = queue.Queue()
				else:
					data = s.recv(self.BUFFER_SIZE)
					if data:

						message_queues[s].put(data)

						if s not in outputs:
							outputs.append(s)
					else:
						if s in outputs:
							outputs.remove(s)
						inputs.remove(s)
						s.close()

						del message_queues[s]

			for s in writable:
				try:
					next_msg = message_queues[s].get_nowait()
				except queue.Empty:
					outputs.remove(s)
				else:
					rec_data = next_msg.decode()
					try:
						rec_dict = json.loads(rec_data)
						for observer in self.observers:
							observer.onPublish(rec_dict)
						# print(s.getpeername(), ':', rec_dict)
					except:
						print(s.getpeername(), "broken", rec_data)

					# rec_data = rec_data.split('}')
					# for rec in rec_data:
					#	if rec != '':
					#		rec = rec + '}'
					#		rec_dict = json.loads(rec)
					#		print(s.getpeername(), ':', rec_dict)

					# print(s.getpeername(), ':', rec_dict)
					# s.send(next_msg)
					# print(next_msg)

			for s in exceptional:
				inputs.remove(s)
				if s in outputs:
					outputs.remove(s)
				s.close()
				del message_queues[s]


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
