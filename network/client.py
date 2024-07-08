import asyncio
import pickle
import socket
import traceback
from asyncio import sleep

from data.AnnouncePeerMessage import AnnouncePeerMessage
from data.ClientMetaData import ClientMetaData
from data.ForwardMessage import ForwardMessage
from data.game.GameJoinMessage import GameJoinMessage
from data.game.GameSearchMessage import GameSearchMessage
from data.game.GameUpdateMessage import GameUpdateMessage
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

    async def receive_data(self, client_socket) -> None:
        while True:
            response = await asyncio.to_thread(client_socket.recv, 70000)
            if not response:
                log("[client] Connection closed")
                client_socket.close()
                break

            data = pickle.loads(response)

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
                self.node.add_game_search(data.game.game_id)

                self.node.game_master.add_game(data.game)
                game = self.node.game_master.get_or_add_game(data.game)
                game.add_client_local(self.name)
                await self.send_message(GameJoinMessage(data.game, self.name))
                log("[client] >GameJoinMessage sent", data.game, self.name)
                # update ttl and forward to ttl clients
                updated_message = GameSearchMessage(data.ttl - 1, self.uid, data.game)
                if updated_message.ttl > 0:  # only forward if ttl > 0
                    await self.node.broadcast_message_with_ttl(updated_message, updated_message.ttl)
            elif isinstance(data, GameUpdateMessage):
                print("[client] >GameUpdateMessage received", data.game.game_id, data.game_object, data.game_value)
                game = self.node.game_master.get_or_add_game(data.game)
                game.update(data)
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
                    await self.node.send_to_client(data.receiver, data.message)
                else:
                    log("[client] >ForwardMessage unknown receiver", data.receiver)

            else:
                log("[client] Received unknown: ", data)

    def knows_client(self, client_name: str) -> bool:
        return client_name in [self.clients[x].name for x in self.clients]

    async def send_message(self, message) -> None:
        if isinstance(message, (bytes, bytearray)):
            self.client.send(message)
        else:
            self.client.send(pickle.dumps(message))

    async def connect_to_socket(self) -> None:
        if self.port == -1:
            log("[client] Cannot connect to bootstrap server")
            return
        client_socket = socket.socket()
        client_socket.connect((self.host, self.port))
        self.client = client_socket
        asyncio.ensure_future(self.receive_data(client_socket))

        client_socket.send(pickle.dumps(ClientMetaData(self.uid, self.server.port)))
        await asyncio.sleep(1)
        # TODO send known own client via AnnouncePeerMessage to all clients

        #  client_socket.close()
