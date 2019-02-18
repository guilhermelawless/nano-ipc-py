import socket
import struct
import json
from .errors import *


class NanoIPC(object):
    _PROTOCOL_PREAMBLE_LEAD = 'N'.encode('utf-8')
    _PROTOCOL_ENCODING = 1
    _preamble = (_PROTOCOL_PREAMBLE_LEAD, _PROTOCOL_ENCODING, 0, 0)
    PACKED_PREAMBLE = struct.pack('>cBBB', *_preamble)


class Client(object):
    def __init__(self, server_address, timeout=15):
        self.__addr = server_address
        if isinstance(self.__addr, str):
            address_family = socket.AF_UNIX
        else:
            address_family = socket.AF_INET6
        self.__sock = socket.socket(address_family, socket.SOCK_STREAM)
        self.set_timeout(timeout)
        self.connected = False

    def connect(self):
        if not self.connected:
            try:
                self.__sock.connect(self.__addr)
                self.connected = True
            except FileNotFoundError:
                raise ConnectionFailure("Could not connect to socket at {}".format(self.__addr))

    def close(self):
        if self.connected:
            self.__sock.close()
            self.connected = False

    def set_timeout(self, timeout):
        self.__sock.settimeout(timeout)

    def request(self, req):
        if not self.connected:
            self.connect()
        try:
            data = json.dumps(req).encode('utf-8')
        except TypeError:
            raise BadRequest("Request must be JSON serializable")

        self.__sock.sendall(NanoIPC.PACKED_PREAMBLE)
        self.__sock.sendall(struct.pack('>I', len(data)))
        self.__sock.sendall(data)

        header = self.__sock.recv(4)
        if len(header) == 0:
            raise ConnectionClosed()
        size = struct.unpack('>I', header)[0]
        data = self.__sock.recv(size)
        if len(data) == 0:
            raise ConnectionClosed()

        try:
            data_js = json.loads(data)
        except json.decoder.JSONDecodeError:
            raise BadResponse("Could not deserialize response", data)
        return data_js

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __del__(self):
        self.close()
