import pickle
import socket

from data.PingPong import PingPong


class P2PClient:

    def __init__(self):
        self.client = None
        self.uid = "client-" + str(hash(socket.gethostname()))
        self.host = "127.0.0.1"
        self.port = 9072
        self.send_some_data()

    def send_some_data(self):
        s = socket.socket()
        s.connect((self.host, self.port))
        d = PingPong("client")
        st = pickle.dumps(d)  # serialize object -> bytes
        print("Sending: ", d)
        s.send(st)
        data = s.recv(1024)
        print("Received: ", pickle.loads(data))
        s.close()


P2PClient()
