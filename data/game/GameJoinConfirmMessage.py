"""

GameJoinConfirmMessage is used to confirm the join request related from GameJoinMessage.

"""
from typing import Type

from game.game import Game


class GameJoinConfirmMessage:
    def __init__(self, game: Game, player) -> None:
        self.game = game
        self.player = player

    def __str__(self) -> str:
        return "GameJoinConfirmMessage: " + str(self.game) + " " + str(self.player)

    def get_game(self) -> Game:
        return self.game

    def get_player(self) -> str:
        return self.player
