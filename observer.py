import json
import socket
import sys
import RCS_messages
import Balancer_messages


class Observer:
    def onPublish(self, data):
        pass

    def onDie(self):
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


class RadarConfigurationObserver(Observer):
    DEFAULT_RADARS = [{'id': 1,'lat': 0,'lon': 1, 'radius': 99},
                      {'id': 2,'lat': 2,'lon': 8, 'radius': 64},
                      {'id': 3,'lat': 7,'lon': 6, 'radius': 11},
                      {'id': 4,'lat': 4,'lon': 6, 'radius': 5}]
    radars = DEFAULT_RADARS



    def onPublish(self, data):
        rec_dict = data['data']
        s = data['socket']
        command = rec_dict['command']
        payload = rec_dict['payload']
        if command == RCS_messages.ADD:
            self.radars.append(payload)
        elif command == RCS_messages.REMOVE:
            rem_id = payload['id']
            radars = list(filter(lambda x: x['id'] != rem_id, self.radars))
            # for i in range(len(radars)):
            #     if radars[i]['id'] == rem_id:
            #         radars.remove(i)
        elif command == RCS_messages.ALL:  # command = RCS_message.ALL
            data = {"payload": self.radars}
            msg = json.dumps(data)
            s.send(msg.encode())

        elif command == RCS_messages.BY_ID:
            rem_id = payload['id']
            to_send = {}
            for radar in self.radars:
                if radar['id'] == rem_id:
                    to_send = radar
                    break

            data = {"payload": to_send}
            msg = json.dumps(data)
            s.send(msg.encode())

from time import gmtime, strftime

class RadarResolverObserver(Observer):

    def __init__(self, rcs_socket, rrc_socket, ip, port, BUFF_SIZE=200):
        self.radars = []
        self.ip = ip
        self.port = port
        self.BUFF_SIZE = BUFF_SIZE
        self.rcs_socket = rcs_socket
        self.rrc_socket = rrc_socket
        self.register()


    def register(self):
        data = {"command": Balancer_messages.REGISTER, "payload":{
            'ip': self.ip,
            'port': self.port,
            'id' : strftime("%Y-%m-%d %H:%M:%S", gmtime())
        }}
        msg = json.dumps(data)
        self.rrc_socket.send(msg.encode())

    def unregister(self):
        data = {"command": Balancer_messages.UNREGISTER}
        msg = json.dumps(data)
        self.rrc_socket.send(msg.encode())

    def isNearby(self, lat, lon, rlat, rlon, radius):
        # x^2 + y^2 <= R^2
        # (x - x0)^2 + (y - y0)^2 <= R^2
        return (lat - rlat)**2 + (lon - rlon)**2 <= radius**2

    def onDie(self):
        super(RadarResolverObserver, self).onDie()
        self.unregister()


    def onPublish(self, data):
        rec_dict = data['data']
        lat = rec_dict['lat']
        lon = rec_dict['lon']

        s = data['socket']

        command = {'command':RCS_messages.ALL, 'payload':{}}
        msg = json.dumps(command)
        self.rcs_socket.send(msg.encode())
        response = self.rcs_socket.recv(self.BUFF_SIZE)

        rec_data = response.decode()
        try:
            rec_dict = json.loads(rec_data)
            radars = rec_dict['payload']
            nearby = []
            for radar in radars:
                rid = radar['id']
                rlat = radar['lat']
                rlon = radar['lon']
                radius = radar['radius']

                if self.isNearby(lat, lon, rlat, rlon, radius):
                    nearby.append(rid)

            data = {"payload": nearby}
            msg = json.dumps(data)
            print(msg)
            s.send(msg.encode())

        except:
            pass

class RoundRobinBalancer(Observer):
    def __init__(self, BUFF_SIZE=100):
        self.rrs = []
        self.next = 0
        self.BUFF_SIZE = BUFF_SIZE

    def onPublish(self, data):
        rec_dict = data['data']
        s = data['socket']

        if 'command' in rec_dict:
            command = rec_dict['command']
            if command == Balancer_messages.REGISTER:
                port = rec_dict['payload']['port']
                id = rec_dict['payload']['id']
                ip= rec_dict['payload']['ip']


                self.rrs.append((id, ip, port))

            elif command == Balancer_messages.UNREGISTER:
                rid = rec_dict['payload']['id']
                idx = None
                for i in range(len(self.rrs)):
                    v = self.rrs[i]
                    if rid == v[0]:
                        idx = rid
                        break
                if idx:
                    self.rrs = self.rrs.pop(idx)



        else:
            if len(self.rrs) == 0:
                return

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if self.next < len(self.rrs):
                msg = json.dumps(rec_dict)
                params = self.rrs[self.next]
                sock.connect((params[1], int(params[2])))
                sock.send(msg.encode())
                response = sock.recv(self.BUFF_SIZE)
                s.send(response)

                self.next += 1
            else:
                self.next = 0

                msg = json.dumps(rec_dict)
                params = self.rrs[self.next]
                sock.connect((params[1], int(params[2])))
                sock.send(msg.encode())

                response = sock.recv(self.BUFF_SIZE)
                s.send(response)

                self.next += 1

            sock.close()


class RadarCollisionObserver(Observer):

    def __init__(self, rcs_socket, rrc_socket, ip, port, BUFF_SIZE=200):
        self.radars = []
        self.ip = ip
        self.port = port
        self.BUFF_SIZE = BUFF_SIZE
        self.rcs_socket = rcs_socket
        self.rrc_socket = rrc_socket
        self.register()


    def register(self):
        data = {"command": Balancer_messages.REGISTER, "payload":{
            'ip': self.ip,
            'port': self.port,
            'id' : strftime("%Y-%m-%d %H:%M:%S", gmtime())
        }}
        msg = json.dumps(data)
        self.rrc_socket.send(msg.encode())

    def unregister(self):
        data = {"command": Balancer_messages.UNREGISTER}
        msg = json.dumps(data)
        self.rrc_socket.send(msg.encode())

    def isNearby(self, lat, lon, rlat, rlon, radius):
        # x^2 + y^2 <= R^2
        # (x - x0)^2 + (y - y0)^2 <= R^2
        return (lat - rlat)**2 + (lon - rlon)**2 <= radius**2

    def onDie(self):
        super(RadarCollisionObserver, self).onDie()
        self.unregister()


    def onPublish(self, data):
        rec_dict = data['data']
        lat = rec_dict['lat']
        lon = rec_dict['lon']

        s = data['socket']

        command = {'command':RCS_messages.ALL, 'payload':{}}
        msg = json.dumps(command)
        self.rcs_socket.send(msg.encode())
        response = self.rcs_socket.recv(self.BUFF_SIZE)

        rec_data = response.decode()
        try:
            rec_dict = json.loads(rec_data)
            radars = rec_dict['payload']
            nearby = []
            for radar in radars:
                rid = radar['id']
                rlat = radar['lat']
                rlon = radar['lon']
                radius = radar['radius']

                if self.isNearby(lat, lon, rlat, rlon, radius):
                    nearby.append(rid)

            data = {"payload": nearby}
            msg = json.dumps(data)
            print(msg)
            s.send(msg.encode())

        except:
            pass