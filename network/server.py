import socket, pickle, asyncio

from aioconsole import ainput

from data import Message
from data.AnnouncePeerMessage import AnnouncePeerMessage
from data.ClientMetaData import ClientMetaData


def filter_client(receiver, clients):
    """
    Filter clients based on receiver name
    :param receiver: receivers name
    :param clients: clients object
    :return: filtered clients
    """
    return [(k[0], v.port) for k, v in clients.items() if v.name != receiver]


class P2PServer:

    def __init__(self, port, node):
        self.server = None
        self.clients = {}  # store known clients
        self.connections = []  # store connections
        self.uid = "server-" + str(hash(socket.gethostname()))
        self.host = "127.0.0.1"
        self.port = port  # system will pick a random port, if port == 0
        self.node = node

    async def start(self,node, bp):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.node.sp = self.server.getsockname()[1]
        self.port = self.server.getsockname()[1]
        self.server.listen()
        self.server.setblocking(False)
        print("[server] Started on port:", self.server.getsockname()[1])
        if bp != -1:
            node.connectToNode("127.0.0.1", bp)
        while True:
            client, _ = await asyncio.get_event_loop().sock_accept(self.server)
            asyncio.ensure_future(self.__handle_client(client))  # ensure_future -> run in background


    async def __handle_client(self, client):
        """
        Handle client connection
        clients are incoming_connections stored in clients

        """
        request = None
        while request != 'quit':
            request = await asyncio.get_event_loop().sock_recv(client, 1024)

            if not client in self.connections:
                self.connections.append(client)

            if request == b'':  # client disconnected
                print(f"[server] {self.clients[client.getpeername()].name} disconnected!")
                del self.clients[client.getpeername()]
                self.connections.remove(client)
                break
            o = pickle.loads(request)  # deserialize object

            if isinstance(o, ClientMetaData):
                a = AnnouncePeerMessage([(k[0], self.clients[k].port) for k, v in self.clients.items()], True)
                if a.known_connections:
                    for k, v in self.clients.items():
                        print(f"{k}: {v} ")
                        r = next((e for e in self.connections if e.getpeername() == client.getpeername()))
                        r.send(pickle.dumps(a))
                        print(f"[server] Sending to {o.port}>{r.getpeername()}: {a}")

                print(f"[server] New client detected {client.getpeername()} as {o.name} at port {o.port}")
                self.clients[client.getpeername()] = o
            elif isinstance(o, Message.Message):
                print(f"[server] Message: {o.message}")
            elif isinstance(o, AnnouncePeerMessage):
                print(f"[server] Received: Announced ----> {o}")

            else:
                print(f"[server] Unknown object received {o}")
            # TODO handle request, store client information, etc.
        client.close()
