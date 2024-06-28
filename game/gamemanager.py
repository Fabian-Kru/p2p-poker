from typing import Type

from game.game import Game


class GameMaster:

    def __init__(self) -> None:
        self.games = []

    def add_game(self, game: Game) -> None:
        print("[game] Game added with id:", game.game_id)
        self.games.append(game)

    def print_game(self) -> None:
        print("[game] Games:")
        for game in self.games:
            print(game)

