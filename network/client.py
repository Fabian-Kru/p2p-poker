import asyncio
import pickle
import socket
from typing import Coroutine, Any

from data.AnnouncePeerMessage import AnnouncePeerMessage
from data.ClientMetaData import ClientMetaData
from data.game.GameJoinMessage import GameJoinMessage
from data.game.GameSearchMessage import GameSearchMessage
from data.game.GameUpdateMessage import GameUpdateMessage


class P2PClient:

    def __init__(self, node, bootstrap_port, name) -> None:
        self.server = node.server
        self.node = node
        self.client = None
        self.uid = name
        self.host = "127.0.0.1"
        self.port = bootstrap_port
        self.clients = []
        print("[client] Started with uid:", self.uid, self.port)

    async def receive_data(self, client_socket) -> None:
        while True:
            try:
                response = await asyncio.to_thread(client_socket.recv, 1024)
                if response:
                    data = pickle.loads(response)

                    if isinstance(data, AnnouncePeerMessage):
                        print("[client] >Announce message received", data.known_connections, self.server.connections)
                        for newPeers in data.known_connections:
                            print("[client] Connecting to new peer", newPeers[1])
                            self.node.connect_to_node("127.0.0.1", newPeers[1])
                    elif isinstance(data, GameSearchMessage):
                        print("[client] >GameSearchMessage received", data)

                        # todo decide to join game or not
                        self.node.game_master.add_game(data.game)
                        client_socket.send(pickle.dumps(GameJoinMessage(data.game, "Player-1")))

                        # update ttl and forward to ttl clients
                        updated_message = GameSearchMessage(data.ttl - 1, self.uid, data.game)
                        if updated_message.ttl > 0:  # only forward if ttl > 0
                            await self.node.broadcast_message_with_ttl(updated_message, updated_message.ttl)
                    elif isinstance(data, GameUpdateMessage):
                        # todo update game state
                        print("[client] >GameUpdateMessage received", data)
                    else:
                        print("[client] Received unknown: ", data)
                else:
                    client_socket.close()
                    break
            except Exception as e:
                print(e)
                client_socket.close()
                break

    async def send_message(self, message) -> None:
        print("[client] Sending message:", message)
        self.client.send(pickle.dumps(message))

    async def send_some_data(self) -> None:
        if self.port == -1:
            print("[client] Cannot connect to bootstrap server")
            return
        client_socket = socket.socket()
        client_socket.connect((self.host, self.port))
        self.client = client_socket
        asyncio.ensure_future(self.receive_data(client_socket))

        client_socket.send(pickle.dumps(ClientMetaData(self.uid, self.server.port)))
        await asyncio.sleep(1)
        # TODO send known own client via AnnouncePeerMessage to all clients

        #  client_socket.close()
