from util.logging import log


class Game:

    game_id: str = None
    is_master: bool = False
    master: str = None
    data: dict = {}
    clients: list = []

    def __init__(self, game_id) -> None:
        log("[game] Game created with id:", game_id)
        self.game_id = game_id

    def get_client_object(self):
        g = Game(self.game_id)
        g.data = self.data
        g.is_master = False
        g.master = self.master
        return g

    def __add_client(self, client):
        if client not in self.clients:
            self.clients.append(client)

    def update(self, data) -> None:
        self.data[data.game_object] = data.game_value
        log("[game] >GameUpdateMessage received", data)
        log("[game] Game state:", self.data)

        if data.game_object == "clients":
            self.clients = data.game_value
            del self.data[data.game_object]

    def set_master(self, name: str) -> None:
        self.is_master = True
        self.master = name

    def __str__(self) -> str:
        return "Game: " + self.game_id + " " + str(self.data) + " " + str(self.is_master) + " " + str(self.master) + " " + str(self.clients)