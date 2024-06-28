"""

GameJoinMessage is used to create a join-request.

"""
from typing import Type

from game.game import Game


class GameJoinMessage:
    def __init__(self, game: Game, player) -> None:
        self.game = game
        self.player = player

    def __str__(self) -> str:
        return "GameJoinMessage: " + str(self.game) + " " + str(self.player)

    def get_game(self) -> Game:
        return self.game

    def get_player(self) -> str:
        return self.player
