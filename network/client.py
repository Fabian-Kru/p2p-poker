import pickle
import socket
from aioconsole import ainput
from data.ClientMetaData import ClientMetaData
from data.Message import Message


class P2PClient:

    def __init__(self, bootstrap_port, name):
        self.client = None
        self.uid = "client-" + name
        self.host = "127.0.0.1"
        self.port = bootstrap_port
        print("Client started with uid:", self.uid)

    async def send_some_data(self):
        if self.port == -1:
            print("Cannot connect to bootstrap server")
            return
        s = socket.socket()
        s.connect((self.host, self.port))
        d = ClientMetaData(self.uid)
        st = pickle.dumps(d)  # serialize object -> bytes
        s.send(st)
        text = st
        while text != 'quit':
            s.send(text)
            text = pickle.dumps(Message(await ainput()))
        s.close()
