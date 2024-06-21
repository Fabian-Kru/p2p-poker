"""

GameFoundMessage is used to inform peers that a game is currently looking for players.
GameFoundMessage is the answer to a GameFoundMessage

"""


class GameFoundMessage:
    def __init__(self, game):
        self.game = game

    def __str__(self):
        return "GameFoundMessage: " + str(self.game)

    def getGame(self):
        return self.game
