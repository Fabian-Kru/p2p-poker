import asyncio
import random

from client import P2PClient
from server import P2PServer


class P2PNode:

    def __init__(self, s_port, start_port):
        self.server = P2PServer(s_port)
        self.bootstrap_port = start_port

    async def run(self):
        if bootstrap_port == -1:
            await self.server.start()
            return

        await asyncio.gather(
            asyncio.create_task(self.server.start()),
            asyncio.create_task(
                P2PClient(self.bootstrap_port, "client-" + str(int(random.random() * 100))).send_some_data())
        )


if __name__ == "__main__":
    server_port = int(input("Enter server_port: "))

    if server_port == 1234:
        bootstrap_port = -1
    elif server_port != 0:
        bootstrap_port = int(input("Enter bootstrap_port: "))
    else:
        bootstrap_port = 1234

    network = P2PNode(server_port, bootstrap_port)
    asyncio.run(network.run())
