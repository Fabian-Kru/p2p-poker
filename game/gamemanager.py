from typing import Type

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
                g.__add_client(client)
                break

    def start_game(self, game):
        if game.game_id not in self.games.keys():
            log("[game] Game not found!")
            return
        log("[game] Starting game with id:", game.game_id)
        self.update_games(game.game_id, "started", True)
        poker: Poker = self.games[game.game_id]["poker"]
        poker.connect_to_players(game.clients)

    def update_games(self, game_id: str, key, value) -> None:
        for k, games in self.games.items():
            if k == game_id:
                games["game"].data[key] = value
                break

    def create_game(self, game_id: str) -> Game:
        print("[game] Hosting game with id:", game_id)
        game = Game(game_id)
        game.set_master(self.node.name)
        game = self.add_game(game)
        poker = Poker(self.node.name)
        # TODO add poker-game data only visible to game_master
        self.update_games(game_id, "poker", poker)

        return game

    def add_game(self, game: Game) -> Game:
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
            log(game)
            log(game["game"])


