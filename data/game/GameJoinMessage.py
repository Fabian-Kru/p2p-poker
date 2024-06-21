"""

GameJoinMessage is used to create a join-request.

"""


class GameJoinMessage:
    def __init__(self, game, player):
        self.game = game
        self.player = player

    def __str__(self):
        return "GameJoinMessage: " + str(self.game) + " " + str(self.player)

    def get_game(self):
        return self.game

    def get_player(self):
        return self.player
