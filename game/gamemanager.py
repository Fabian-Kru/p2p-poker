import asyncio
import pickle
from typing import Type

from data.game.GameUpdateMessage import GameUpdateMessage
from game.game import Game
from game.poker import Poker
from util.logging import log


class GameMaster:

    games: dict = {}  # game_id: {game: game_object,  poker: poker}
    node: Type['P2PNode'] = None

    def __init__(self, node) -> None:
        self.games = {}
        self.node = node

    def add_client(self, game_id: str, client) -> None:
        for k, game in self.games.items():
            if k == game_id:
                g = game["game"]
                g.add_client_local(client)
                break

    def start_game(self, game):
        if game.game_id not in self.games.keys():
            log("[game] Game not found!")
            return
        log("[game] Starting game with id:", game.game_id)
        self.update_games(game.game_id, "started", True)
        print(self.games[game.game_id].keys())
        poker: Poker = self.games[game.game_id]["poker"]

        if self.node.name not in game.clients:
            self.games[game.game_id]["game"].add_client_local(self.node.name)

        print(game.clients)
        poker.connect_to_players(game.clients)
        player_cards = poker.deal_cards()
        print(player_cards)
        for player_name in player_cards.keys():
            print("[game] Dealing cards to:", player_name, player_cards[player_name][player_name])
            update = GameUpdateMessage(game, "cards", player_cards[player_name][player_name])
            self.handle_update(player_name, player_name, update)
        for player_name in player_cards.keys():
            self.handle_update(player_name, player_name, GameUpdateMessage(game, "next_player", poker.next_player.name))

    def handle_update(self, receiver: [str, None], player_name: str, update: GameUpdateMessage) -> None:

        if receiver is not None:
            update.set_receiver(receiver)

        # send not to self
        if player_name == self.node.name:
            update.update_game_with_data()
        else:
            asyncio.ensure_future(
                self.node.send_to_client(player_name, pickle.dumps(update)))

    def update_games(self, game_id: str, key, value) -> None:
        for k, games in self.games.items():
            if k == game_id:
                print("[game] Updating game with id:", game_id, key, "=", value)
                self.games[game_id]["game"].data[key] = value
                print(self.games[game_id]["game"])
                break

    def create_game(self, game_id: str) -> Game:
        print("[game] Hosting game with id:", game_id)
        game = Game(game_id, self.node.name)
        game.set_master(self.node.name)
        game = self.add_game(game)
        poker = Poker(self.node.name)
        # TODO add poker-game data only visible to game_master
        self.games[game_id]["poker"] = poker
        print(self.games[game_id].keys())
        return game

    def add_game(self, game: Game) -> Game:
        log("[game] Game added with id:", game.game_id)
        self.games[game.game_id] = {"game": game}
        return game

    def get_or_add_game(self, game: Game) -> Game:
        print(">>",self.games.keys(), game.game_id)
        for g in self.games.keys():
            if g == game.game_id:
                return self.games[g]["game"]
        log("[game] Game not found. Adding new game with id:", game.game_id)
        return self.add_game(game)

    def print_game(self) -> None:
        log("[game] Games:")
        for k, game in self.games.items():
            log(game["game"])
            log(game["poker"])
            log("----")

    def get_current_game(self) -> Game:
        for k, game in self.games.items():
            return game["game"]

    def get_current_poker(self) -> Game:
        for k, game in self.games.items():
            return game["poker"]



