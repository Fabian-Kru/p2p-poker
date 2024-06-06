import asyncio

from client import P2PClient
from server import P2PServer


class P2PNetwork:

    def __init__(self, s_port, start_port):
        self.server = P2PServer(s_port)
        self.bootstrap_port = start_port

    async def run(self):
        server_task = asyncio.create_task(self.server.start())
        if server_port != 1234:  # first peer does not require a bootstrap-peer (it is the bootstrap-peer)
            await asyncio.create_task(P2PClient(self.bootstrap_port, "client-" + str(self.bootstrap_port)).send_some_data())

        await server_task


if __name__ == "__main__":
    server_port = int(input("Enter server_port: "))
    bootstrap_port = int(input("Enter bootstrap_port: "))

    network = P2PNetwork(server_port, bootstrap_port)
    asyncio.run(network.run())
