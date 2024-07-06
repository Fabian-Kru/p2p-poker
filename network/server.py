import asyncio
import pickle
import socket
from typing import TYPE_CHECKING

from data.ForwardMessage import ForwardMessage
from data.game.GameJoinMessage import GameJoinMessage
from data.game.GameUpdateMessage import GameUpdateMessage
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
                client.send(pickle.dumps(ClientMetaData(self.node.name, self.port)))

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
            elif isinstance(o, GameUpdateMessage):
                log("[server] >GameUpdateMessage received", o)
                game = self.node.game_master.get_or_add_game(o.game)
                game.update(o)
            elif isinstance(o, GameJoinMessage):
                log("[server] >GameJoinMessage received", o)
                game = self.node.game_master.get_or_add_game(o.game)
                game.add_client(o.player)
                update_data = GameUpdateMessage(game, "clients", game.clients)
                game.update(update_data) # update local cache
                # TODO gjm -> game_master -> game_update -> all_clients
                for c in game.clients:
                    await self.node.send_to_client(c, pickle.dumps(update_data))
            elif isinstance(o, ForwardMessage):
                log("[server] >ForwardMessage received", o.message)
                if self.node.knows_client(o.receiver):
                    await self.node.send_to_client(o.receiver, o.message)

            else:
                log(f"[server] Unknown object received {o}")
            # TODO handle request, store client information, etc.
        client.close()

    def known_client(self, client_name: str) -> bool:
        return client_name in [self.clients[x].name for x in self.clients]

    async def send_to_client(self, client_name, message) -> None:
        for client in self.connections:
            if self.clients[client.getpeername()].name == client_name:
                if isinstance(message, (bytes, bytearray)):
                    client.send(message)
                else:
                    client.send(pickle.dumps(message))
                break

    async def broadcast_message(self, message) -> None:
        for client in self.connections:
            print("[server] Sending to", self.clients[client.getpeername()].name)
            client.send(pickle.dumps(message))
