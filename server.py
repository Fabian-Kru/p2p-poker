import socket, pickle, asyncio


class P2PServer:

    def __init__(self):
        self.server = None
        self.client_storage = []  # store known clients
        self.uid = "server-" + str(hash(socket.gethostname()))
        self.host = "127.0.0.1"
        self.port = 9072

    def start(self):
        if self.server is None:
            asyncio.run(self.__start())

    async def __start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.server.setblocking(False)
        loop = asyncio.get_event_loop()
        while True:
            client, _ = await loop.sock_accept(self.server)
            await loop.create_task(self.__handle_client(client))

    async def __handle_client(self, client):
        loop = asyncio.get_event_loop()
        request = None
        while request != 'quit':
            request = (await loop.sock_recv(client, 1024))
            o = pickle.loads(request)  # deserialize object
            print("Received: ", o)
            o.count = o.count + 1
            o.name = self.uid  # send own name back
            await loop.sock_sendall(client, pickle.dumps(o))
            break
            # TODO handle request, store client information, etc.
        client.close()
