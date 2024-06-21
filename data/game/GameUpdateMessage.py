"""

GameUpdateMessage is used to update any game related content.

"""


class GameUpdateMessage:
    def __init__(self, game_state):
        self.game_state = game_state

    def __str__(self):
        return "GameUpdateMessage: " + self.game_state
