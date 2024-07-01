from typing import Type

from game.game import Game
from util.logging import log


class GameMaster:

    def __init__(self) -> None:
        self.games = []

    def add_game(self, game: Game) -> None:
        log("[game] Game added with id:", game.game_id)
        self.games.append(game)

    def get_or_add_game(self, game: Game) -> Game:
        for g in self.games:
            if g.game_id == game.game_id:
                return g
        log("[game] Game not found. Adding new game with id:", game.game_id)
        self.add_game(game)
        return game

    def print_game(self) -> None:
        log("[game] Games:")
        for game in self.games:
            log(game)

