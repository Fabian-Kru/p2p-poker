import pickle
import socket
import sys
import threading
from typing import TYPE_CHECKING

from data import Message
from data.AnnouncePeerMessage import AnnouncePeerMessage
from data.ClientMetaData import ClientMetaData
from data.ForwardMessage import ForwardMessage
from data.game.GameJoinMessage import GameJoinMessage
from data.game.GameUpdateMessage import GameUpdateMessage
from network import network_util
from util.logging import log

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

    def start(self, node: 'P2PNode', bp: int) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.node.sp = self.server.getsockname()[1]
        self.port = self.server.getsockname()[1]
        self.server.listen()
        self.server.setblocking(True)
        log("[server] Started on port:", self.server.getsockname()[1])
        if bp != -1:
            node.connect_to_node("127.0.0.1", bp)
        while True:
            try:
                client, _ = self.server.accept()
                threading.Thread(target=self.__handle_client, args=(client,)).start()
            except (socket.error, ConnectionResetError, OSError) as e:
                log(f"[server] Error: {e}")
                sys.exit(0)
                break

    def close_connections(self) -> None:
        for client in self.connections:
            client.close()
        self.server.close()
        sys.exit(1)

    def __handle_client(self, client: socket):
        """
        Handle client connection
        clients are incoming_connections stored in clients

        """
        while True:
            try:
                request = network_util.recv_msg(client)

                if not request or request == b'' or len(request) == 0:  # client disconnected
                    log(f"[server] {self.clients[client.getpeername()].name} disconnected!")
                    del self.clients[client.getpeername()]
                    self.connections.remove(client)
                    break

                if client not in self.connections:
                    self.connections.append(client)
                    message = pickle.dumps(ClientMetaData(self.node.name, self.port))
                    network_util.send_msg(client, message)

                o = pickle.loads(request)  # deserialize object

                if isinstance(o, ClientMetaData):
                    a = AnnouncePeerMessage([(k[0], self.clients[k].port) for k, v in self.clients.items()], True)
                    if a.known_connections:
                        for k, v in self.clients.items():
                            log(f"{k}: {v} ")
                            r = next((e for e in self.connections if e.getpeername() == client.getpeername()))
                            network_util.send_msg(r, pickle.dumps(a))
                            log(f"[server] Sending to {o.port}>{r.getpeername()}: {a}")

                    log(f"[server] New client detected {client.getpeername()} as {o.name} at port {o.port}")
                    self.clients[client.getpeername()] = o
                elif isinstance(o, Message.Message):
                    log(f"[server] Message: {o.message}")
                elif isinstance(o, AnnouncePeerMessage):
                    log(f"[server] Received: Announced ----> {o}")
                elif isinstance(o, GameUpdateMessage):
                    print("[server] >GameUpdateMessage received", o.game.game_id, o.game_object, o.game_value)
                    game = self.node.game_master.get_or_add_game(o.game)
                    game.update(o, self.node.game_master)
                elif isinstance(o, GameJoinMessage):
                    log("[server] >GameJoinMessage received", o)
                    game = self.node.game_master.get_or_add_game(o.game)
                    self.node.game_master.add_client(game.game_id, o.player)
                elif isinstance(o, ForwardMessage):
                    log("[server] >ForwardMessage received", o.message)
                    if self.node.knows_client(o.receiver):
                        self.node.send_to_client(o.receiver, o.message)

                else:
                    log(f"[server] Unknown object received {o}")
            except (socket.error, ConnectionResetError) as e:
                name = self.clients[client.getpeername()].name
                log(f"[Socket-Error, Server] {name} disconnected!")
                self.node.game_master.client_disconnect(name)
                del self.clients[client.getpeername()]
                self.connections.remove(client)
                break
            except Exception as e:
                log(f"[server] Error: {e}")
                break

        client.close()

    def known_client(self, client_name: str) -> bool:
        return client_name in [self.clients[x].name for x in self.clients]

    def send_to_client(self, client_name, message) -> None:
        for client in self.connections:
            if self.clients[client.getpeername()].name == client_name:
                if isinstance(message, (bytes, bytearray)):
                    network_util.send_msg(client, message)
                else:
                    network_util.send_msg(client, pickle.dumps(message))
                break

    def broadcast_message(self, message) -> None:

        if isinstance(message, GameUpdateMessage) and message.receiver is not None:
            self.send_to_client(message.receiver, message)
            return
        for client in self.connections:
            self.node.send_to_client(self.clients[client.getpeername()].name, message)
