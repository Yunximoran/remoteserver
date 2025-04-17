import socket

from ._tcp import _ProtoType


class Connector(_ProtoType):
    def __init__(self, address, *, listens = None, timeout = None, settings = []):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.settings(settings)
        
        self.sock.connect(address)
        if listens:
            self.sock.listen(listens)
        self.sock.settimeout(timeout)