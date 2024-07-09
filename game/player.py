from game.game_util import Actions


class Player:

    def __init__(self, name):
        self.name = name
        self.chips = 1000
        self.bet = 0
        self.status = Actions.PLAYING
        self.played = False

    def next_round(self):
        self.played = False

    def new_round(self) -> None:
        self.bet = 0
        if self.chips == 0:
            self.status = Actions.CHIP_LESS

        if not self.status == Actions.CHIP_LESS:
            self.status = Actions.PLAYING

    def poker_raise(self, chips, current_bet) -> [Actions, int]:
        self.played = True
        """
        Changes the player attributes for as if they raised during play.
        :param current_bet: Amount of chips bet
        :param chips: Amount of chips raised
        :return: Returns the amount of chips or an Error if the raise is not possible.
        """
        print("current_bet", current_bet, "chips", chips)
        if self.status != Actions.PLAYING:
            return Actions.ERROR_NOT_PLAYING

        chips += current_bet - self.bet
        
        if chips > self.chips:
            return Actions.ERROR_NOT_ENOUGH_CHIPS

        self.chips -= chips
        self.bet += chips

        if self.chips == 0:
            self.status = Actions.ALL_IN

        return chips

    def poker_blinds(self, chips) -> [Actions, int]:
        """
        Changes the player attributes for as if they paid the blind during play.
        :param chips: Size of the blind
        :return: Returns the amount of chips or an Error if the raise is not possible.
        """

        if self.status != Actions.PLAYING:
            return Actions.ERROR_NOT_PLAYING

        if self.status != Actions.PLAYING:
            return Actions.ERROR_NOT_ENOUGH_CHIPS

        chips = min(chips, self.chips)

        self.chips -= chips
        self.bet += chips

        if self.chips == 0:
            self.status = Actions.ALL_IN

        return chips

    def poker_fold(self) -> [Actions, int]:
        """
        Player change for folding
        :return:
        """

        if self.status != Actions.PLAYING:
            return Actions.ERROR_NOT_PLAYING

        self.status = Actions.FOLDED

        return 0

    def poker_check(self):
        self.played = True
        return 0

    def poker_call(self, current_bet) -> [Actions, int]:
        self.played = True

        if self.status != Actions.PLAYING:
            return Actions.ERROR_NOT_PLAYING

        chips = current_bet - self.bet

        self.chips -= chips
        self.bet += chips

        if self.chips == 0:
            self.status = Actions.ALL_IN

        return chips

    def available_actions(self, current_bet) -> list:
        action_list = []

        if self.status == Actions.PLAYING:
            if current_bet - self.bet < self.chips:
                action_list.append("raise")

            if self.bet == current_bet:
                action_list.append("check")

            elif self.bet < current_bet:
                action_list += ["fold", "call"]

        return action_list

    def get_winnings(self, chips) -> (int, bool):

        if self.bet <= chips:
            temp = self.bet
            self.bet = 0
            return temp, True

        else:
            self.bet -= chips
            return chips, False

    def is_my_socket(self, client_name) -> bool:
        return self.name == client_name

    def __str__(self) -> str:
        return self.name + " " + str(self.chips) + " " + str(self.bet) + " " + str(self.status)