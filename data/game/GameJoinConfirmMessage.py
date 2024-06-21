"""

GameJoinConfirmMessage is used to confirm the join request related from GameJoinMessage.

"""


class GameJoinConfirmMessage:
    def __init__(self, game, player):
        self.game = game
        self.player = player

    def __str__(self):
        return "GameJoinConfirmMessage: " + str(self.game) + " " + str(self.player)

    def get_game(self):
        return self.game

    def get_player(self):
        return self.player
