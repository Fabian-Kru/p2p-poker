"""

GameFoundMessage is used to inform peers that a game is currently looking for players.
GameFoundMessage is the answer to a GameFoundMessage

"""
from typing import Type, List

from game.game import Game


class GameFoundMessage:
    def __init__(self, game: Game) -> None:
        self.game = game

    def __str__(self) -> str:
        return "GameFoundMessage: " + str(self.game)

    def getGame(self) -> Game:
        return self.game
