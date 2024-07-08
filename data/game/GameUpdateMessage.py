"""

GameUpdateMessage is used to update any game related content.

"""
from typing import Optional, Type


class GameUpdateMessage:
    receiver = None

    def __init__(self, game, game_object: any, game_value: any) -> None:
        self.game = game
        self.game_object = game_object
        self.game_value = game_value

    def set_receiver(self, receiver: Type) -> None:
        self.receiver = receiver

    def update_game_with_data(self) -> None:
        self.game.update(self)

    def __str__(self):
        return "GameUpdateMessage: " + str(self.game) + " " + str(self.game_object) + " " + str(self.game_value)
