import pickle
import socket
import sys
import threading

from data.AnnouncePeerMessage import AnnouncePeerMessage
from data.ClientMetaData import ClientMetaData
from data.ForwardMessage import ForwardMessage
from data.game.GameJoinMessage import GameJoinMessage
from data.game.GameSearchMessage import GameSearchMessage
from data.game.GameUpdateMessage import GameUpdateMessage
from network import network_util
from util.logging import log


class P2PClient:

    def __init__(self, node, bootstrap_port, name) -> None:
        self.server = node.server
        self.node = node
        self.client = None
        self.uid = name
        self.name = "client-" + str(self.server.port)
        self.host = "127.0.0.1"
        self.port = bootstrap_port
        self.clients = {}
        log(f"[client] Started {self.name}. Connecting to 127.0.0.1:{self.port}")

    def receive_data(self, client_socket) -> None:
        no_error = True
        while no_error:
            try:
                response = network_util.recv_msg(client_socket)

                if not response:
                    log("[client] Connection closed")
                    client_socket.close()
                    break

                data = pickle.loads(response, encoding="utf-8", fix_imports=True, buffers=None)

                if isinstance(data, ClientMetaData):
                    self.node.server.clients[client_socket.getpeername()] = data
                    self.clients[client_socket.getpeername()] = data

                elif isinstance(data, AnnouncePeerMessage):
                    log("[client] >Announce message received", data.known_connections, self.server.connections)
                    for newPeers in data.known_connections:
                        if self.node.connect_to_node("127.0.0.1", newPeers[1]):
                            log("[client] Connecting to new peer", newPeers[1])
                elif isinstance(data, GameSearchMessage):
                    log("[client] >GameSearchMessage received", data.game)
                    self.node.add_game_search(data)
                    self.node.join_any_game()
                    # update ttl and forward to ttl clients
                    updated_message = GameSearchMessage(data.ttl - 1, self.uid, data.game)
                    if updated_message.ttl > 0:  # only forward if ttl > 0
                        self.node.broadcast_message_with_ttl(updated_message, updated_message.ttl)
                elif isinstance(data, GameUpdateMessage):
                    log("[client] >GameUpdateMessage received", data.game.game_id, data.game_object, data.game_value)
                    game = self.node.game_master.get_or_add_game(data.game)
                    game.update(data, self.node.game_master)
                elif isinstance(data, GameJoinMessage):
                    log("[client] >GameJoinMessage received", data)
                    game = self.node.game_master.get_or_add_game(data.game)
                    self.node.game_master.add_client(data.player, game)
                elif isinstance(data, ForwardMessage):
                    log("[client] >ForwardMessage received", data.message)
                    if data.receiver == self.node.name:
                        log("[client] >ForwardMessage received", data.message)
                    elif self.node.knows_client(data.receiver):
                        log("[client] >ForwardMessage forwarding", data.message)
                        self.node.send_to_client(data.receiver, data.message)
                    else:
                        log("[client] >ForwardMessage unknown receiver", data.receiver)

                else:
                    log("[client] Received unknown: ", data)
            except Exception as e:
                log("[client] Node Connection closed", e)
                sys.exit(1)

    def knows_client(self, client_name: str) -> bool:
        return client_name in [self.clients[x].name for x in self.clients]

    def send_message(self, message) -> None:
        if not isinstance(message, (bytes, bytearray)):
            message = pickle.dumps(message, protocol=None)
        network_util.send_msg(self.client, message)

    def close_connection(self):
        log("[client] Closing connection")
        self.client.close()

    def connect_to_socket(self) -> None:
        if self.port == -1:
            log("[client] Cannot connect to bootstrap server")
            return
        client_socket = socket.socket()
        client_socket.connect((self.host, self.port))
        self.client = client_socket
        threading.Thread(target=self.receive_data, args=(client_socket,)).start()
        self.send_message(pickle.dumps(ClientMetaData(self.uid, self.server.port), protocol=None))
