import asyncio
import pickle
import socket

from data.AnnouncePeerMessage import AnnouncePeerMessage
from data.ClientMetaData import ClientMetaData


class P2PClient:

    def __init__(self, node, bootstrap_port, name):
        self.server = node.server
        self.node = node
        self.client = None
        self.uid = name
        self.host = "127.0.0.1"
        self.port = bootstrap_port
        self.clients = []
        print("[client] Started with uid:", self.uid, self.port)

    async def receive_data(self, client_socket):
        while True:
            try:
                response = await asyncio.to_thread(client_socket.recv, 1024)
                if response:
                    data = pickle.loads(response)

                    if isinstance(data, AnnouncePeerMessage):
                        print("[client] >Announce message received", data.known_connections, self.server.connections)
                        for newPeers in data.known_connections:
                            print("[client] Connecting to new peer", newPeers[1])
                            self.node.connectToNode("127.0.0.1", newPeers[1])
                    else:
                        print("[client] Received unknown: ", data)
                else:
                    client_socket.close()
                    break
            except Exception as e:
                print(e)
                client_socket.close()
                break

    async def send_some_data(self):
        if self.port == -1:
            print("[client] Cannot connect to bootstrap server")
            return
        client_socket = socket.socket()
        client_socket.connect((self.host, self.port))

        asyncio.ensure_future(self.receive_data(client_socket))

        client_socket.send(pickle.dumps(ClientMetaData(self.uid, self.server.port)))
        await asyncio.sleep(1)
        # TODO send known own client via AnnouncePeerMessage to all clients

        #  client_socket.close()
