
from util.logging import log


class Game:

    game_id: str = None
    is_master: bool = False
    master: str = None
    data: dict = {}
    clients: list = []

    cards: list = []
    poker = None

    def __init__(self, game_id, own_name, master, poker, dont_log=False) -> None:
        if not dont_log:
            log("[game] Game created with id:", game_id)
        self.game_id = game_id
        self.master = master
        self.own_name = own_name
        self.poker = poker

    def set_master(self, name: str) -> None:
        self.is_master = True
        self.master = name

    def get_client_object(self):
        g = Game(self.game_id, self.own_name, self.master, self.poker, True)
        g.data = self.data
        g.is_master = False
        g.master = self.master
        return g

    def add_client_local(self, client):
        if client not in self.clients:
            self.clients.append(client)

    def update(self, data) -> None:
        self.data[data.game_object] = data.game_value

        if data.game_object == "clients":
            self.clients = data.game_value
            self.poker.set_players(self.clients)
            log("[game] Players updated", self.clients)
            del self.data[data.game_object]
        elif data.game_object == "cards":
            self.cards = data.game_value
            del self.data[data.game_object]
        elif data.game_object == "next_player":
            self.poker.next_player = self.poker.players[data.game_value]
            print("[game] Next player is", data.game_value)
            if data.game_value == self.own_name:
                log("[game] It's my turn")
                # TODO send next_player in list that he is the next player (after own game_action)
            del self.data[data.game_object]

        elif data.game_object == "action:raise":
            s = data.game_value.split(":")
            name = s[0]
            chips = int(s[1])
            old_bet = int(s[2])

            if name == self.own_name:
                return
            print(name, self.own_name)

            result = self.poker.players[name].poker_raise(chips, old_bet)
            log("[game] action:raise", name, chips, "result=", result)

        elif data.game_object == "action:fold":
            s = data.game_value.split(":")
            name = s[0]
            status = int(s[1])
            self.poker.players[name].poker_fold()
            log("[game] action:fold", name, status)

        elif data.game_object == "action:blinds":
            s = data.game_value.split(":")
            name = s[0]
            status = int(s[1])
            chips = int(s[2])
            current_bet = int(s[3])
            self.poker.players[name].poker_blinds(chips)
            self.poker.players[name].current_bet = current_bet
            log("[game] action:blinds", name, chips, status)

        elif data.game_object == "action:fold":
            s = data.game_value.split(":")
            name = s[0]
            status = int(s[1])
            self.poker.players[name].poker_fold()
            log("[game] action:fold", name, status)

        elif data.game_object == "action:call":
            s = data.game_value.split(":")
            name = s[0]
            status = int(s[1])
            chips = int(s[2])
            self.poker.players[name].poker_call(self.poker.current_bet)
            log("[game] action:call", name, chips, status)
        elif data.game_object == "action:check":
            s = data.game_value.split(":")
            name = s[0]
            status = int(s[1])
            chips = int(s[2])
            log("[game] action:check", name, chips, status)
        elif data.game_object == "new_round":
            self.poker.new_round()
        elif data.game_object == "request:cards":
            s = data.game_value.split(":")
            name = s[0]
            card = s[1]
            log("[game] request:cards", name, card)
            #poker.get_card_codes -> poker.receive_card_codes
        else:
            log("[game] Unknown game update message", data.game_object)

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
