#radar configuration server


import select, socket, sys, queue
import sys

import signal
import json
import RCS_messages

TCP_IP = sys.argv[1]
TCP_PORT = int(sys.argv[2])
BUFFER_SIZE = 100  # Normally 1024, but we want fast response

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
server.bind((TCP_IP, TCP_PORT))
server.listen(1)
inputs = [server]
outputs = []
message_queues = {}
radars = []

def signal_handler(signal, frame):
    server.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

while inputs:
    readable, writable, exceptional = select.select(
        inputs, outputs, inputs)
    for s in readable:
        if s is server:
            connection, client_address = s.accept()
            connection.setblocking(0)
            inputs.append(connection)
            message_queues[connection] = queue.Queue()
        else:
            data = s.recv(BUFFER_SIZE)
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
                # print(s.getpeername(), ':', rec_dict)
                command = rec_dict['command']
                payload = rec_dict['payload']
                if command == RCS_messages.ADD:
                    radars.append(payload)
                elif command == RCS_messages.REMOVE:
                    rem_id = payload['id']
                    for i in range(len(radars)):
                        if radars[i]['id'] == rem_id:
                            radars.remove(i)
                else: # command = RCS_message.ALL
                    data = {"payload", radars}
                    msg = json.dumps(data)
                    s.send(msg.encode())

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
