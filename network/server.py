import asyncio
import pickle
import socket
from typing import TYPE_CHECKING
from util.logging import log
from data import Message
from data.AnnouncePeerMessage import AnnouncePeerMessage
from data.ClientMetaData import ClientMetaData

if TYPE_CHECKING:
    from network.network import P2PNode


def filter_client(receiver, clients):
    """
    Filter clients based on receiver name
    :param receiver: receivers name
    :param clients: clients object
    :return: filtered clients
    """
    return [(k[0], v.port) for k, v in clients.items() if v.name != receiver]


class P2PServer:

    def __init__(self, port: int, node: 'P2PNode') -> None:
        self.server = None
        self.clients = {}  # store known clients
        self.connections = []  # store connections
        self.uid = "server-" + str(hash(socket.gethostname()))
        self.host = "127.0.0.1"
        self.port = port  # system will pick a random port, if port == 0
        self.node = node

    async def start(self, node: 'P2PNode', bp: int) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.node.sp = self.server.getsockname()[1]
        self.port = self.server.getsockname()[1]
        self.server.listen()
        self.server.setblocking(False)
        log("[server] Started on port:", self.server.getsockname()[1])
        if bp != -1:
            node.connect_to_node("127.0.0.1", bp)
        while True:
            client, _ = await asyncio.get_event_loop().sock_accept(self.server)
            asyncio.ensure_future(self.__handle_client(client))  # ensure_future -> run in background

    async def __handle_client(self, client: socket):
        """
        Handle client connection
        clients are incoming_connections stored in clients

        """
        request = None
        while request != 'quit':
            request = await asyncio.get_event_loop().sock_recv(client, 1024)

            if client not in self.connections:
                self.connections.append(client)

            if request == b'':  # client disconnected
                log(f"[server] {self.clients[client.getpeername()].name} disconnected!")
                del self.clients[client.getpeername()]
                self.connections.remove(client)
                break
            o = pickle.loads(request)  # deserialize object

            if isinstance(o, ClientMetaData):
                a = AnnouncePeerMessage([(k[0], self.clients[k].port) for k, v in self.clients.items()], True)
                if a.known_connections:
                    for k, v in self.clients.items():
                        log(f"{k}: {v} ")
                        r = next((e for e in self.connections if e.getpeername() == client.getpeername()))
                        r.send(pickle.dumps(a))
                        log(f"[server] Sending to {o.port}>{r.getpeername()}: {a}")

                log(f"[server] New client detected {client.getpeername()} as {o.name} at port {o.port}")
                self.clients[client.getpeername()] = o
            elif isinstance(o, Message.Message):
                log(f"[server] Message: {o.message}")
            elif isinstance(o, AnnouncePeerMessage):
                log(f"[server] Received: Announced ----> {o}")

            else:
                log(f"[server] Unknown object received {o}")
            # TODO handle request, store client information, etc.
        client.close()

    async def send_to_client(self, client_name, message) -> None:
        for client in self.connections:
            if self.clients[client.getpeername()].name == client_name:
                client.send(pickle.dumps(message))
                break

    async def broadcast_message(self, message) -> None:
        for client in self.connections:
            client.send(pickle.dumps(message))
