import socket, pickle, asyncio

from data import Message
from data.ClientMetaData import ClientMetaData


class P2PServer:

    def __init__(self, port):
        self.server = None
        self.clients = {}  # store known clients
        self.uid = "server-" + str(hash(socket.gethostname()))
        self.host = "127.0.0.1"
        self.port = port  # system will pick a random port, if port == 0

    async def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.port = self.server.getsockname()[1]
        self.server.listen()
        self.server.setblocking(False)
        print("Server started on port:", self.server.getsockname()[1])
        while True:
            client, _ = await asyncio.get_event_loop().sock_accept(self.server)
            asyncio.ensure_future(self.__handle_client(client))  # ensure_future -> run in background

    async def __handle_client(self, client):
        request = None
        while request != 'quit':
            request = await asyncio.get_event_loop().sock_recv(client, 1024)

            if not client.getpeername() in self.clients:
                self.clients[client.getpeername()] = (client, None)

            if request == b'':  # client disconnected
                print(f"{self.clients[client.getpeername()][1].name} disconnected!")
                del self.clients[client.getpeername()]
                break
            o = pickle.loads(request)  # deserialize object

            if isinstance(o, ClientMetaData) and self.clients[client.getpeername()][1] is None:
                self.clients[client.getpeername()] = (client, o)
                print(f"New client detected {client.getpeername()} as {o.name}")
            elif isinstance(o, Message.Message):
                print(f"{self.clients[client.getpeername()][1].name}: {o.message}")
            else:
                print(f"Unknown object received {o}")
            # TODO handle request, store client information, etc.
        client.close()
