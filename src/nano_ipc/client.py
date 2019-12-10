import asyncio
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
    def __init__(self, server_address, max_connections=10, timeout=15, loop=asyncio.get_event_loop()):
        """
        Creates a client handler for TCP or Unix domain socket connections

        :param server_address: Either a tuple (host, port) for a TCP connection, or a path for Unix domain sockets
        """
        self.__addr = server_address
        self.__loop = loop
        self.__timeout = timeout
        if max_connections > 100:
            raise Exception('No more than 100 connections')
        self.__max_connections = max_connections
        self.__connections = [None] * max_connections
        self.__queue = asyncio.LifoQueue(max_connections)
        for i in range(0, max_connections):
            self.__queue.put_nowait(i)

    async def __new_connection(self, pos):
        if not isinstance(self.__addr, tuple):
            conn = asyncio.open_unix_connection(path=self.__addr, loop=self.__loop)
        else:
            conn = asyncio.open_connection(host=self.__addr[0], port=self.__addr[1], loop=self.__loop)
        connection = await asyncio.wait_for(conn, 3)
        self.__connections[pos] = connection
        return connection

    async def __get_connection(self, pos):
        try:
            connection = self.__connections[pos]
        except IndexError:
            connection = None
        if not connection:
            connection = await self.__new_connection(pos)
        if not connection:
            raise ConnectionClosed()
        return connection

    def __close_one(self, pos):
        connection = self.__connections[pos]
        if connection is None:
            return False
        _, writer = connection
        try:
            writer.close()
        except Exception as e:
            print(e)
        finally:
            self.__connections[pos] = None

    async def close(self):
        for i in range(len(self.__connections)):
            self.__close_one(i)

    async def request(self, req):
        pos = None
        try:
            handle_json = not isinstance(req, bytes)
            if handle_json:
                try:
                    data = json.dumps(req).encode('utf-8')
                except TypeError:
                    raise BadRequest("Request must be a string or JSON serializable")
            else:
                data = req

            pos = await self.__queue.get()

            reader, writer = await self.__get_connection(pos)

            await asyncio.wait_for(writer.drain(), self.__timeout)
            # https://docs.nano.org/integration-guides/advanced/#ipc-requestresponse-format
            writer.writelines([
                NanoIPC.PACKED_PREAMBLE,
                struct.pack('>I', len(data)),
                data
            ])

            header = await asyncio.wait_for(reader.read(4), self.__timeout)
            if len(header) == 0:
                raise ConnectionClosed()
            size = struct.unpack('>I', header)[0]
            data = await asyncio.wait_for(reader.read(size), self.__timeout)
            if len(data) == 0:
                raise ConnectionClosed()

            if handle_json:
                try:
                    data_js = json.loads(data)
                except json.decoder.JSONDecodeError:
                    raise BadResponse("Could not deserialize response", data)
                return data_js
            else:
                return data
        except ConnectionClosed:
            if pos:
                self.__close_one(pos)
            await asyncio.sleep(1)
            response_again = await self.request(req)
            return response_again
        finally:
            self.__queue.put_nowait(pos)

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
