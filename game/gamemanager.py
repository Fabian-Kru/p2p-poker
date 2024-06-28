from typing import Type

from game.game import Game
from util.logging import log


class GameMaster:

    def __init__(self) -> None:
        self.games = []

    def add_game(self, game: Game) -> None:
        log("[game] Game added with id:", game.game_id)
        self.games.append(game)

    def print_game(self) -> None:
        log("[game] Games:")
        for game in self.games:
            log(game)

