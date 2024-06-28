"""

GameSearchMessage is used to find games local.

"""


class GameSearchMessage:
    def __init__(self, ttl, sender=None, game=None):
        self.sender = sender
        self.game = game
        self.ttl = ttl

    def __str__(self):
        return "GameSearchMessage: ttl=" + str(self.ttl) + " from " + str(self.sender) + "\n Game:" + str(self.game)
