"""

GameUpdateMessage is used to update any game related content.

"""
from typing import Optional, Type

from game.game import Game


class GameUpdateMessage:
    def __init__(self, game: Game, game_state: Optional[str]) -> None:
        self.game = game
        self.game_state = game_state

    def __str__(self) -> str:
        return "GameUpdateMessage: " + self.game_state
