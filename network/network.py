import asyncio
import random
import threading

from aioconsole import ainput

from client import P2PClient
from data.game.GameSearchMessage import GameSearchMessage
from server import P2PServer


class P2PNode:

    def __init__(self, _server_port, port):
        self.server = P2PServer(_server_port, self)
        self.clients = []
        self.bp = port
        self.sp = _server_port

    def connect_to_node(self, ip, port):
        c = P2PClient(self, port, "client-" + str(self.sp))
        print(f"[server] Connecting to {ip}:{port} with new client")
        self.clients.append(c)
        asyncio.ensure_future(c.send_some_data())

    async def broadcast_message_with_ttl(self, message, ttl):
        for i, client in enumerate(self.clients):
            if i < ttl:
                asyncio.ensure_future(client.send_message(message))

    async def broadcast_message(self, message):
        for c in self.clients:
            asyncio.ensure_future(c.send_message(message))

    async def run(self):
        if bootstrap_port == -1:
            await self.server.start(self, -1)
            return
        await asyncio.create_task(self.server.start(self, self.bp)),

    async def process_input(self, command):

        if command == "search_game":
            print("[server] Searching for game")
            # Send to all connected clients -> ttl of 1-2
            await self.server.broadcast_message(GameSearchMessage(ttl=2))
            return

        if command == "list":
            print("[server] server:", self.server.uid, "[client] client: client-" + str(self.sp))
            print("[server] clients:", [c.uid for c in self.clients])
            print("[client] clients", [v.name for k, v in self.server.clients.items()])
            return


async def input_handler(_network):
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
