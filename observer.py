import json
import sys

class Observer:
	def onPublish(self, data):
		pass

class LoggingObserver(Observer):
	def onPublish(self, data):
		print(data)

		
class NetworkPushObserver(Observer):
	def __init__(self, socket):
		super(Observer, self).__init__()
		self.socket = socket
	
	def onPublish(self, data):
		msg = json.dumps(data)
		self.socket.send(msg.encode())