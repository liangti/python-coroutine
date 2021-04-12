"""Coroutine Task Application"""
import os
import socket

from src.task import NewTask

SOCKET_ADDR = "play"


class Server:
    """Socket Server"""
    def __init__(self, timeout=5):
        """Init"""
        self.timeout = timeout

    def handle_client(self, client, addr, size=1024):
        """Handle client method"""
        data = client.recv(size)
        print(data)

    def mainloop(self):
        """Server main loop"""
        try:
            os.unlink(SOCKET_ADDR)
        except FileNotFoundError:
            pass
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind((SOCKET_ADDR))
        sock.listen(self.timeout)
        while True:
            client, addr = sock.accept()
            self.handle_client(client, addr)


class Client:
    """Socket Client"""
    def __init__(self, port):
        """Init"""
        self.port = port

    def send(self, data):
        """Client send"""
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(SOCKET_ADDR)
        sock.send(b"hi")
        sock.close()