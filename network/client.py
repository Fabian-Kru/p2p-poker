import pickle
import socket
from aioconsole import ainput

from data.AnnouncePeerMessage import AnnouncePeerMessage
from data.ClientMetaData import ClientMetaData
from data.Message import Message


class P2PClient:

    def __init__(self, bootstrap_port, name):
        self.client = None
        self.uid = "client-" + name
        self.host = "127.0.0.1"
        self.port = bootstrap_port
        self.clients = []
        print("Client started with uid:", self.uid)

    async def send_some_data(self):
        if self.port == -1:
            print("Cannot connect to bootstrap server")
            return
        s = socket.socket()
        s.connect((self.host, self.port))
        meta = ClientMetaData(self.uid)
        # request targeted server to send known connections
        # pickle.dumps(meta) serialize object -> bytes
        s.send(pickle.dumps(meta))
        # TODO handle response
        text = await ainput()
        while text != 'quit':

            if text == "announce" or text == "a":
                data = pickle.dumps(AnnouncePeerMessage(None, False))
                s.send(data)
                print("Sending announce")
                text = await ainput()
                continue

            print("Sending: ", pickle.loads(text))
            s.send(pickle.dumps(Message(pickle.loads(text))))
            text = await ainput()
        s.close()
