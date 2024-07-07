from enums import *


class Player:

    def __init__(self, name):

        self.name = name
        self.chips = 1000
        self.bet = 0
        self.status = PLAYING

    def __str__(self):

        return self.name

    def new_round(self):
        self.bet = 0
        if self.chips == 0:
            self.status = CHIPLESS

        if not self.status == CHIPLESS:
            self.status = PLAYING

    def set_dealer(self):
        self.status = DEALER

    def new_game(self):
        """
        Re-initializes the player for a new game.
        :return:
        """

        self.chips = 1000
        self.bet = 0
        self.status = PLAYING

    def poker_raise(self, chips, current_bet):
        """
        Changes the player attributes for as if they raised during play.
        :param chips: Amount of chips raised
        :return: Returns the amount of chips or an Error if the raise is not possible.
        """

        if self.status != PLAYING:
            return ERROR_NOT_PLAYING

        chips += current_bet - self.bet
        
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

        if self.chips == 0:
            self.status = ALL_IN

        return chips

    def poker_fold(self):
        """
        Player change for folding
        :return:
        """

        if self.status != PLAYING:
            return ERROR_NOT_PLAYING

        self.status = FOLDED

        return 0

    def poker_check(self):
        return 0

    def poker_call(self, current_bet):

        if self.status != PLAYING:
            return ERROR_NOT_PLAYING

        chips = current_bet - self.bet

        self.chips -= chips
        self.bet += chips

        if self.chips == 0:
            self.status = ALL_IN

        return chips

    def available_actions(self, current_bet):
        action_list = []

        if self.status == PLAYING:
            if current_bet - self.bet < self.chips:
                action_list.append("raise")

            if self.bet == current_bet:
                action_list.append("check")

            elif self.bet < current_bet:
                action_list += ["fold", "call"]

        return action_list

    def get_winnings(self, chips):

        if self.bet <= chips:
            temp = self.bet
            self.bet = 0
            return temp, True

        else:
            self.bet -= chips
            return chips, False

    def is_my_socket(self, client_name):
        return self.name == client_name
