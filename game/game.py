from typing import Optional

from game.player import Player
from util.logging import log


class Game:

    game_id: str = None
    is_master: bool = False
    master: str = None
    data: dict = {}
    clients: list = []

    cards: list = []
    myself: Player = None

    def __init__(self, game_id, own_name, dont_log=False) -> None:
        if not dont_log:
            log("[game] Game created with id:", game_id)
        self.game_id = game_id
        self.myself = Player(own_name)

    def get_client_object(self):
        g = Game(self.game_id, self.myself, True)
        g.data = self.data
        g.is_master = False
        g.master = self.master
        return g

    def add_client_local(self, client):
        if client not in self.clients:
            self.clients.append(client)

    def update(self, data) -> None:
        self.data[data.game_object] = data.game_value
        log("[game] >GameUpdateMessage received", data)
        log("[game] Game state:", self.data)

        if data.game_object == "clients":
            self.clients = data.game_value
            del self.data[data.game_object]
        elif data.game_object == "cards":
            self.cards = data.game_value
            del self.data[data.game_object]
        elif data.game_object == "next_player":
            if data.game_value == self.myself.name:
                log("[game] It's my turn")

            del self.data[data.game_object]

        else:
            log("[game] Unknown game update message", data.game_object)

    def set_master(self, name: str) -> None:
        self.is_master = True
        self.master = name

    def __str__(self) -> str:
        return (
                "Game: "
                + self.game_id
                + " " + str(self.data)
                + " " + str(self.is_master)
                + " " + str(self.master)
                + " " + str(self.clients)
                + " " + str(self.cards)
        )
