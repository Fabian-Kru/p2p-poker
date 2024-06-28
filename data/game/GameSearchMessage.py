"""

GameSearchMessage is used to find games local.

"""

from game.game import Game


class GameSearchMessage:
    def __init__(self, ttl: int, sender=None, game: Game = None) -> None:
        self.sender = sender
        self.game = game
        self.ttl = ttl

    def __str__(self) -> str:
        return "GameSearchMessage: ttl=" + str(self.ttl) + " from " + str(self.sender) + "\n Game:" + str(self.game)
