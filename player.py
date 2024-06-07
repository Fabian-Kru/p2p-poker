from enums import *


class Player:

    def __init__(self, name, socket):

        self.name = name
        self.chips = 1000
        self.bet = 0
        self.status = PLAYING
        self.socket = socket

    def __str__(self):

        return self.name

    def new_game(self):
        """
        Re-initializes the player for a new game.
        :return:
        """

        self.chips = 1000
        self.bet = 0
        self.status = PLAYING

    def poker_raise(self, chips):
        """
        Changes the player attributes for as if they raised during play.
        :param chips: Amount of chips raised
        :return: Returns the amount of chips or an Error if the raise is not possible.
        """

        if self.status != PLAYING:
            return ERROR_NOT_PLAYING

        if chips > self.chips:
            return ERROR_NOT_ENOUGH_CHIPS

        self.chips -= chips
        self.bet += chips

        if self.chips == 0:
            self.status = ALL_IN

        return chips

    def poker_blinds(self, chips):
        """
        Changes the player attributes for as if they paid the blind during play.
        :param chips: Size of the blind
        :return: Returns the amount of chips or an Error if the raise is not possible.
        """

        if self.status != PLAYING:
            return ERROR_NOT_PLAYING

        if self.status != PLAYING:
            return ERROR_NOT_ENOUGH_CHIPS

        chips = min(chips, self.chips)

        self.chips -= chips
        self.bet += chips

    def poker_fold(self):
        """
        Player change for folding
        :return:
        """

        if self.status != PLAYING:
            return ERROR_NOT_PLAYING

        self.status = FOLDED

        return 0
