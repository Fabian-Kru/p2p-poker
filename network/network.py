import asyncio
import pickle

from client import P2PClient
from data.Message import Message
from data.game.GameSearchMessage import GameSearchMessage
from game.game import Game
from game.gamemanager import GameMaster
from typing import TYPE_CHECKING, List

from util.logging import log

if not TYPE_CHECKING:
    from server import P2PServer


class P2PNode:

    def __init__(self, _server_port: int, port: int) -> None:
        self.server = P2PServer(_server_port, self)
        self.clients: List[P2PClient] = []
        self.bp = port
        self.sp = _server_port
        self.game_master = GameMaster()  # shared between client and server to avoid sync problems

    def connect_to_node(self, ip: str, port: int) -> None:
        c = P2PClient(self, port, "client-" + str(self.sp))
        self.clients.append(c)
        asyncio.ensure_future(c.send_some_data())

    def get_client_by_name(self, name: str) -> [P2PClient, None]:
        for c in self.clients:
            if c.uid == name:
                log("Found client-1", c)
                return c
        return None

    async def send_to_client(self, client_name: str, message: bytes) -> None:
        client = self.get_client_by_name(client_name)

        if client is not None:
            asyncio.ensure_future(client.send_message(message))

        for k, v in self.server.clients.items():
            if v.name == client_name:
                asyncio.ensure_future(self.server.send_to_client(v.name, message))

    async def broadcast_message_with_ttl(self, message: str, ttl: int) -> None:
        for i, client in enumerate(self.clients):
            if i < ttl:
                asyncio.ensure_future(client.send_message(message))

    async def broadcast_message(self, message: str) -> None:
        for c in self.clients:
            asyncio.ensure_future(c.send_message(message))

    async def run(self) -> None:
        if bootstrap_port == -1:
            await self.server.start(self, -1)
            return
        await asyncio.create_task(self.server.start(self, self.bp)),

    async def process_input(self, command: str) -> None:

        if command == "search_game":
            log("[server] Searching for game")
            # Send to all connected clients -> ttl of 1-2
            game = Game("Game-1")
            self.game_master.add_game(game)
            await self.server.broadcast_message(GameSearchMessage(ttl=2, sender=None, game=game))
            return

        if command == "list":
            log("[server] own-name:", "client-" + str(self.sp))
            log("[server] clients:", [c.uid for c in self.clients])
            log("[client] clients", [v.name for k, v in self.server.clients.items()])
            return

        if command == "games":
            self.game_master.log_game()
            return

        if command.startswith("send"):
            parts = command.split(" ")
            if len(parts) < 3:
                log("Invalid command")
                return
            client_name = parts[1]
            message = " ".join(parts[2:])
            await self.send_to_client(client_name, pickle.dumps(Message(message)))
            return


async def input_handler(_network) -> None:
    while True:
        command = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
        await _network.process_input(command)


if __name__ == "__main__":
    server_port = int(input("Enter server_port: "))

    if server_port == 1234:
        bootstrap_port = -1
    else:
        bootstrap_port = 1234

    network = P2PNode(server_port, bootstrap_port)
    loop = asyncio.new_event_loop()

    loop.run_until_complete(asyncio.gather(
        loop.create_task(network.run()),
        loop.create_task(input_handler(network))
    ))
