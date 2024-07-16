from data.game.GameUpdateMessage import GameUpdateMessage
from game.game_util import Actions
from util.logging import log

from tui import tui


class Game:

    game_id: str = None
    is_master: bool = False
    master: str = None
    data: dict = {}
    clients: list = []

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
            if self.is_master:
                tui.get_tui().create_game(True)

    def update(self, data, game_master) -> None:
        self.data[data.game_object] = data.game_value

        if data.game_object == "clients":
            self.clients = data.game_value
            self.poker.set_players(self.clients)
            log("[game] Players updated", self.clients)
            del self.data[data.game_object]
        elif data.game_object == "cards":
            self.poker.code_state = data.game_value
            del self.data[data.game_object]
        elif data.game_object == "next_player":
            self.poker.next_player = self.poker.players[data.game_value]
            del self.data[data.game_object]

            if data.game_value == self.own_name:
                tui.get_tui().draw_game(True)
            else:
                tui.get_tui().draw_game(False)
        elif data.game_object == "next_round":
            self.poker.next_round(game_master, self)
            self.poker.next_player = self.poker.players[self.poker.get_active_players_playing()[0]]  # TODO change with

            # changing dealer
            log("next_round", data.game_value, "next_player:", self.poker.next_player)
            del self.data[data.game_object]

            if self.poker.next_player.name == self.own_name:
                tui.get_tui().draw_game(True)
            else:
                tui.get_tui().draw_game(False)
        elif data.game_object == "action:raise":
            s = data.game_value.split(":")
            name = s[0]
            chips = int(s[1])
            current_bet = int(s[2])
            old_bet = int(s[3])

            if name == self.own_name:
                return
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
            client_name = s[0]
            card_string = s[1]

            to_send = self.poker.get_card_codes(card_string, client_name)

            log("[game] get:cards", client_name, card_string, to_send)
            if to_send is not None:
                game_master.handle_update(client_name, client_name, GameUpdateMessage(self, "receive:cards", to_send + [card_string]))
        elif data.game_object == "receive:cards":
            l = data.game_value
            card_string = l.pop(-1)
            self.poker.receive_card_codes(card_string, l, game_master, self)
            log("[game] receive:cards", card_string, l)
            tui.get_tui().draw_game(self.poker.next_player.name == self.own_name)
        elif data.game_object == "trigger_end":
            self.poker.trigger_end()
            log("[game] trigger_end")
        elif data.game_object == "client:disconnect":
            self.poker.players[data.game_value].status = Actions.DISCONNECTED
            log("[game] client:disconnect", data.game_value)
        elif data.game_object == "dealer":
            self.poker.players[data.game_value].status = Actions.DEALER
            self.master = data.game_value
            if self.own_name == data.game_value:
                self.is_master = True
            else:
                self.is_master = False
            log("[game] dealer", data.game_value)
            self.poker.set_next_player()
        elif data.game_object == "new_dealer":
            self.master = data.game_value
            if self.own_name == data.game_value:
                self.is_master = True
            else:
                self.is_master = False
            game_master.new_round(self)
            log("[game] new_dealer", data.game_value)
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

        )
