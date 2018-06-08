# coding: utf-8
import zmq
import time
import json



class Messager(object):
    def __init__(self, ip, port):
        host= 'tcp://{ip}:{port}'.format(ip=ip, port=port)
        ctx = zmq.Context()
        self._sock = ctx.socket(zmq.PUB)
        self._sock.bind(host)

    def destroy(self):
        self._sock.close()

    def send(self, topic, frame):
        self._sock.send_multipart([topic, json.dumps(frame, ensure_ascii=False)])



