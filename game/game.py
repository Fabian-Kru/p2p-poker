from data.game.GameUpdateMessage import GameUpdateMessage
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

    def update(self, data, game_master) -> None:
        self.data[data.game_object] = data.game_value

        if data.game_object == "clients":
            self.clients = data.game_value
            self.poker.set_players(self.clients)
            log("[game] Players updated", self.clients)
            del self.data[data.game_object]
        elif data.game_object == "cards":
            self.cards = data.game_value
            self.poker.code_state = self.cards
            print("code_state")
            del self.data[data.game_object]
        elif data.game_object == "next_player":
            print("next_player", data.game_value)
            self.poker.next_player = self.poker.players[data.game_value]
            if data.game_value == self.own_name:
                log("[game] It's my turn")
            del self.data[data.game_object]
        elif data.game_object == "next_round":
            print("next_round", data.game_value)
            self.poker.next_round()
            del self.data[data.game_object]
        elif data.game_object == "action:raise":
            s = data.game_value.split(":")
            name = s[0]
            chips = int(s[1])
            current_bet = int(s[2])
            old_bet = int(s[3])

            if name == self.own_name:
                return
            print(name, chips, current_bet, old_bet)
            result = self.poker.players[name].poker_raise(chips, old_bet)
            self.poker.current_bet = current_bet

            log("[game] action:raise", name, chips, "result=", result, "old_bet=", old_bet)

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
            self.poker.players[name].poker_check()
            log("[game] action:check", data.game_value)
        elif data.game_object == "new_round":
            self.poker.new_round()
        elif data.game_object == "get:cards":
            s = data.game_value.split(":")
            card_string = s[0]
            client_name = s[1]
            to_send = self.poker.get_card_codes(card_string, client_name)
            if to_send is not None:  # TODO why None?
                game_master.handle_update(client_name, client_name, GameUpdateMessage(self, "receive:cards", to_send + [card_string]))
        elif data.game_object == "receive:cards":
            l = data.game_value
            card_string = l.pop(-1)
            self.poker.receive_card_codes(card_string, l)
            log("[game] receive:cards", card_string, l)
        elif data.game_object == "next_round":
            print("nextround")
            # self.poker.next_round()
            #log("[game] next_round")
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
