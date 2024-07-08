from enum import Enum


class Actions(Enum):
    PLAYING = 0
    FOLDED = 1
    ALL_IN = 2
    CHIP_LESS = 3
    DEALER = 4
    DISCONNECTED = 5
    ERROR_NOT_ENOUGH_CHIPS = -1
    ERROR_NOT_PLAYING = -2
    ERROR_ACTION_NOT_FOUND = -3

    def __str__(self):
        return self.name


