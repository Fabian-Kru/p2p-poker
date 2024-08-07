import pickle
from typing import Type

from data.game.GameUpdateMessage import GameUpdateMessage
from game.game import Game
from game.poker import Poker
from util.logging import log

active_game_master = None


class GameMaster:
    games: dict = {}  # game_id: {game: game_object,  poker: poker}
    node: Type['P2PNode'] = None

    @staticmethod
    def create_master(node: 'P2PNode'):
        global active_game_master
        active_game_master = GameMaster(node)
        return active_game_master

    @staticmethod
    def get_master():
        global active_game_master
        return active_game_master

    def __init__(self, node) -> None:
        self.games = {}
        self.node = node

    def client_disconnect(self, client_name: str) -> None:
        for k, game in self.games.items():
            g = game["game"]
            if client_name in g.clients:
                for clients in g.poker.players:
                    if clients != client_name:
                        self.handle_update(clients, clients,
                                           GameUpdateMessage(g, "client:disconnect", client_name))
                continue

    def add_client(self, game_id: str, client) -> None:
        for k, game in self.games.items():
            if k == game_id:
                g = game["game"]
                g.add_client_local(client)
                break

    def deliver_card_code(self, game_id, name: str, card_string: str) -> None:
        game = self.get_game_by_id(game_id)
        self.handle_update(game.master, game.master, GameUpdateMessage(game, "get:cards", name + ":" + card_string))

    def new_dealer_and_round(self, game):
        game.poker.set_next_player()
        log("[game] New dealer:", game.poker.next_player)
        self.handle_update(game.poker.next_player.name,
                           game.poker.next_player.name,
                           GameUpdateMessage(game, "new_dealer", game.poker.next_player.name))

    def new_round(self, game) -> None:
        for player in game.poker.players:
            self.handle_update(player, player, GameUpdateMessage(game, "new_round", None))
        self.start_round(game)

    def start_game(self, game):
        if game.game_id not in self.games.keys():
            log("[game] Game not found!")
            return
        log("[game] Starting game with id:", game.game_id)
        self.update_games(game.game_id, "started", True)

        if self.node.name not in game.clients:
            self.games[game.game_id]["game"].add_client_local(self.node.name)

        game.poker.set_players(game.clients)

        for players in game.clients:
            self.handle_update(players, players, GameUpdateMessage(game, "clients", game.clients))

        self.start_round(game)

    def start_round(self, game):
        player_cards = game.poker.deal_cards()

        for players in player_cards:
            self.handle_update(players, players, GameUpdateMessage(game, "dealer", game.master))

        for player_name in player_cards.keys():
            if player_name == game.master:
                continue
            update = GameUpdateMessage(game, "cards", player_cards[player_name])
            self.handle_update(player_name, player_name, update)

            if player_name in game.poker.get_active_players():
                update_cards = GameUpdateMessage(
                    game,
                    "receive:cards",
                    game.poker.get_card_codes(player_name, player_name) + [player_name]
                )
                self.handle_update(player_name, player_name, update_cards)
        game.poker.set_next_player()
        log("Es startet: ", game.poker.next_player.name)
        self.handle_update(game.poker.next_player.name, game.poker.next_player.name,
                           GameUpdateMessage(game, "next_player", game.poker.next_player.name))

    def handle_update(self, receiver: [str, None], player_name: str, update: GameUpdateMessage) -> None:
        if receiver is not None:
            update.set_receiver(receiver)

        if player_name == self.node.name:
            update.update_game_with_data(self.node.game_master)
        else:
            self.node.send_to_client(player_name, pickle.dumps(update, protocol=None))

    def update_games(self, game_id: str, key, value) -> None:
        for k, games in self.games.items():
            if k == game_id:
                log("[game] Updating game with id:", game_id, key, "=", value)
                self.games[game_id]["game"].data[key] = value
                break

    def create_game(self, game_id: str) -> Game:
        log("[game] Hosting game with id:", game_id)
        poker = Poker(self.node.name, game_id)
        game = Game(game_id, self.node.name, self.node.name, poker)
        game.set_master(self.node.name)
        game = self.add_game(game)
        return game

    def add_game(self, game: Game) -> Game:
        game.own_name = self.node.name
        game.poker.name = self.node.name
        log("[game] Game added with id:", game.game_id)
        self.games[game.game_id] = {"game": game}
        return game

    def get_or_add_game(self, game: Game) -> Game:
        for g in self.games.keys():
            if g == game.game_id:
                return self.games[g]["game"]
        log("[game] Game not found. Adding new game with id:", game.game_id)
        return self.add_game(game)

    def print_game(self) -> None:
        log("[game] Games:")
        for k, game in self.games.items():
            log(game["game"])
            if "poker" in game.keys():
                log(game["poker"])
            log("----")

    def get_current_game(self) -> Game:
        for k, game in self.games.items():
            return game["game"]

    def get_game_by_id(self, game_id) -> (Game, None):
        for k, game in self.games.items():
            if k == game_id:
                return game["game"]
        return None
