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
        for observer in self.observers:
            observer.onDie()

        self.stopEvent.set()
        self.thread.join()

    def addObserver(self, observer):
        self.observers.append(observer)


class Transmitter(Publisher):
    def __init__(self, TCP_IP, TCP_PORT, BUFFER_SIZE=100):
        super(Transmitter, self).__init__()

        # self.observers = []
        #
        # self.stopEvent = threading.Event()
        # self.thread = threading.Thread(target=self.proc, args=[self.stopEvent])

        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        self.BUFFER_SIZE = BUFFER_SIZE  # Normally 1024, but we want fast response
    def stop(self):
        super(Transmitter,self).stop()

        self.server.close()

    def proc(self, event):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(0)
        self.server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.server.bind((self.TCP_IP, self.TCP_PORT))
        self.server.listen(1)
        inputs = [self.server]
        outputs = []
        message_queues = {}

        while inputs and not event.wait(1):
            readable, writable, exceptional = select.select(
                inputs, outputs, inputs)
            for s in readable:
                if s is self.server:
                    connection, client_address = s.accept()
                    connection.setblocking(0)
                    inputs.append(connection)
                    message_queues[connection] = queue.Queue()
                else:
                    try:
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
                    except:
                        pass

            for s in writable:
                try:
                    next_msg = message_queues[s].get_nowait()
                except queue.Empty:
                    outputs.remove(s)
                except Exception as e:
                    print(e)
                else:
                    rec_data = next_msg.decode()
                    try:
                        rec_dict = json.loads(rec_data)

                        data = {'data': rec_dict, 'socket': s}
                        for observer in self.observers:
                            observer.onPublish(data)
                        # print(s.getpeername(), ':', rec_dict)
                    except Exception as e:
                        print(s.getpeername(), "broken", rec_data)
                        print(str(e))

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
            'id': self.id,
            'lat': new_lat,
            'lon': new_lon,
            'airport_id': self.airport_id
        }
