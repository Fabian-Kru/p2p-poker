import time
from time import sleep

from data.game.GameUpdateMessage import GameUpdateMessage
from util.logging import log
import treys
from treys import Card, Deck
import math
import random
from game import player, gamemanager
from game.game_util import Actions

ranks = {0: "2", 1: "3", 2: "4", 3: "5", 4: "6", 5: "7", 6: "8", 7: "9", 8: "T", 9: "J", 10: "Q", 11: "K", 12: "A"}
suits = {0: "s", 1: "h", 2: "d", 3: "c"}


def card_treys_to_int(card_treys: int):
    """
    Turns an integer representation from the treys library into a 0 to 51 integer.
    :param card_treys:
    :return: 0-51 integer representation of card
    """

    return int(Card.get_rank_int(card_treys) + 13 * math.log(Card.get_suit_int(card_treys), 2))


def int_to_trey_card(card_int: int):
    """
    Turns an 0-51 integer representation into a card from the treys library
    :param card_int:
    :return: A card from the treys library
    """

    return Card.new(ranks[card_int % 13] + suits[card_int // 13])


def key_list_to_card(key_list: list):
    """
    Takes a key list and decodes it into a card
    :param key_list:
    :return: A treys card
    """
    return int_to_trey_card(sum(key_list) % 52)


def decode_key_lists(key_list1: list, key_list2: list):
    """
    Takes to encoded key_lists into one decoded one
    :param key_list1:
    :param key_list2:
    :return: Decoded key list
    """
    for i in range(len(key_list1)):
        if key_list1[i] == 52:
            key_list1[i] = key_list2[i]

        elif key_list2[i] != 52 and key_list1[i] != key_list2[i]:
            print("These key lists are not the same.")
            return None

    return key_list1


def generate_key_list(card_treys: int):
    """
    Makes a list of numbers from 0 to 51 to encode the card received.
    :param card_treys: Takes a treys card
    :return: returns the list of 10 numbers
    """
    key_list = []
    card_int = card_treys_to_int(card_treys)

    for i in range(9):
        key_list.append(random.randrange(0, 51))

    key_list.append((card_int - sum(key_list)) % 52)

    return key_list


class Poker:

    def __init__(self, name, game_id):
        self.game_id = game_id
        self.card_state = {}
        self.players = {}
        self.code_state = {}
        self.log = []
        self.round = 0
        self.next_player = None
        self.name = name
        self.open = False
        self.current_bet = 0
        self.evaluator = treys.Evaluator()

    def new_round(self):
        self.card_state = {}
        self.code_state = {}
        self.round = 0
        self.current_bet = 0
        self.open = False
        for players in self.players:
            players.new_round()

    def request_card_codes(self, card_string):
        print(card_string)
        gamemanager.active_game_master.get_master().deliver_card_code(self.game_id, self.name, card_string)

    def deal_cards(self):
        """
        Generates a dictionary with key lists for each player and cards with one number replaced to encode the cards.
        :return: the generated dictionary
        """

        self.card_state = {}
        deck = Deck()

        self.card_state["board"] = deck.draw(5)
        for player_obj in self.players:
            self.card_state[player_obj] = deck.draw(2)

        key_dict = {}

        for place in self.card_state:

            key_dict[place] = []

            for card_treys in self.card_state[place]:
                key_dict[place].append(generate_key_list(card_treys))

        n = 0
        self.code_state = key_dict
        code_dict = {}

        for player_name in self.players:

            code_dict[player_name] = {}

            for place in key_dict:

                code_dict[player_name][place] = []

                for key_list in key_dict[place]:
                    temp_list = key_list.copy()
                    temp_list[n] = 52
                    code_dict[player_name][place].append(temp_list)

            n += 1

        return code_dict

    def set_players(self, player_list):

        next_is_next = False

        for player_name in player_list:
            if player_name != self.name:
                self.players[player_name] = player.Player(player_name)
                if next:
                    self.next_player = self.players[player_name]
                    next_is_next = False
            else:
                self.players[player_name] = player.Player(player_name)
                next_is_next = True

        if next_is_next:
            self.next_player = self.players[player_list[-1]]

    def next_round(self):
        print("next round")
        time.sleep(1)
        for players, player_obj in self.players.items():
            player_obj.next_round()

        self.round += 1

        if not self.open:
            match self.round:
                case 1:
                    self.request_card_codes("b1")

                case 2:
                    self.request_card_codes("b2")

                case 3:
                    self.request_card_codes("b3")

                case 4:
                    self.request_card_codes("players")
                    self.trigger_end()

    def __card_permission(self, card_string, client_name):
        match card_string:
            case "b1":
                return self.round >= 1
            case "b2":
                return self.round >= 2
            case "b3":
                return self.round >= 3
            case _:
                if self.round >= 4 or self.open:
                    return True
                elif card_string in self.players and self.players[card_string].is_my_socket(client_name):
                    return (self.players[card_string].status == Actions.PLAYING
                            or self.players[card_string].status == Actions.ALL_IN)

    def get_card_codes(self, card_string, client_name):

        if self.__card_permission(card_string, client_name):
            match card_string:
                case "b1":
                    return self.code_state["board"][0:2]
                case "b2":
                    return [self.code_state["board"][3]]
                case "b2":
                    return [self.code_state["board"][4]]
                case _:
                    return self.code_state[card_string]

        # TODO Fabian send karten

    def receive_card_codes(self, card_string, code_list):
        if card_string in self.players:
            self.card_state[card_string] = []

            for card in zip(code_list, self.code_state[card_string]):
                self.card_state[card_string].append(key_list_to_card(decode_key_lists(card[0], card[1])))

        else:
            match card_string:
                case "b1":
                    self.card_state["board"] = []
                    for i in range(3):
                        self.card_state["board"].append(
                            key_list_to_card(decode_key_lists(code_list[i], self.code_state["board"][i])))
                case "b2":
                    self.card_state["board"].append(
                        key_list_to_card(decode_key_lists(code_list[0], self.code_state["board"][3])))
                case "b2":
                    self.card_state["board"].append(
                        key_list_to_card(decode_key_lists(code_list[0], self.code_state["board"][4])))

        # TODO Implement receiving cards

    def player_action(self, game_master, game, player_name, action, chips) -> int:
        self.played = True
        player_obj = self.players[player_name]
        log("Player action: ", player_obj, action, chips)
        match action:
            case "raise":
                old_bet = self.current_bet

                status = player_obj.poker_raise(chips, old_bet)
                if status >= 0:
                    self.current_bet += chips
                for p in game.poker.players:
                    if p == player_name:
                        continue
                    game_master.handle_update(
                        p,
                        p,
                        GameUpdateMessage(game, "action:raise",
                                          player_name + ":" + str(chips) + ":" + str(self.current_bet) + ":" + str(old_bet))
                    )
            case "blinds":
                status = player_obj.poker_blinde(chips)
                if chips > self.current_bet:
                    self.current_bet = chips
                for p in game.poker.players:
                    if p == player_name:
                        continue
                    game_master.handle_update(
                        p,
                        p,
                        GameUpdateMessage(game, "action:blinds",
                                          player_name + ":" + str(status) + ":" + str(chips) + ":" + str(
                                              self.current_bet))
                    )
            case "fold":
                status = player_obj.poker_fold()
                for p in game.poker.players:
                    if p == player_name:
                        continue
                    game_master.handle_update(
                        p,
                        p,
                        GameUpdateMessage(game, "action:fold",
                                          player_name + ":" + str(status) + ":" + str(chips) + ":" + str(
                                              self.current_bet))
                    )
            case "check":
                status = player_obj.poker_check()  # for check -> next_player
                for p in game.poker.players:
                    if p == player_name:
                        continue
                    game_master.handle_update(
                        p,
                        p,
                        GameUpdateMessage(game, "action:check", player_name)

                    )
            case "call":
                status = player_obj.poker_call(self.current_bet)
                for p in game.poker.players:
                    if p == player_name:
                        continue
                    game_master.handle_update(
                        p,
                        p,
                        GameUpdateMessage(game, "action:call",
                                          player_name + ":" + str(status) + ":" + str(chips) + ":" + str(
                                              self.current_bet))
                    )
            case _:
                status = Actions.ERROR_ACTION_NOT_FOUND
        # da diese Methode immer aufgerufen wird, wenn ein Zug zu ende ist -> nächster Spieler

        plist = []
        for pl, _ in self.players.items():
            plist.append(pl)
        next_player = plist[0]

        for i, players in enumerate(plist):
            if players == self.next_player.name:
                next_player = plist[(i + 1) % len(plist)]
                self.next_player = next_player
                for p in game.poker.players:
                    game_master.handle_update(
                        p,
                        p,
                        GameUpdateMessage(game, "next_player", next_player)
                    )
                break

        if ("check" in self.players[next_player].available_actions(self.current_bet)
                and self.players[next_player].played):
            for p in game.poker.players:
                print(p)
                game_master.handle_update(
                      p,
                      p,
                      GameUpdateMessage(game, "next_round", next_player)
                )

        if self.active_players() == 1:
            self.trigger_end()

        self.check_open()
        return status

    # TODO aufrufen

    def check_open(self):

        playing_num = 0
        in_game_num = 0

        for name, player_obj in self.players.items():
            if player_obj.status == Actions.PLAYING:
                playing_num += 1
                in_game_num += 1
                if playing_num >= 2:
                    break

            if player_obj.status == Actions.ALL_IN:
                in_game_num += 1

        if playing_num == 1 and in_game_num > 1:
            self.open = True
            self.request_card_codes("players")

    def trigger_end(self):

        values = {}

        for player_name in self.card_state:
            if player_name != "board":
                values[player_name] = self.evaluator.evaluate(self.card_state[player_name], self.card_state["board"])

        chips_left_in_pot = True

        while chips_left_in_pot:
            chips_left_in_pot = False

            winner = max(values, key=values.get)
            print(values)
            del values[winner]
            print(winner)

            chips = self.players[winner].bet
            print(chips)

            winnings = 0

            for player_name in self.players:
                bet, bet_empty = self.players[player_name].get_winnings(chips)
                print(player_name, bet)
                winnings += bet
                if not bet_empty:
                    chips_left_in_pot = True

            self.players[winner].chips += winnings

    def active_players(self):
        n = 0
        for name, player_obj in self.players.items():
            if player_obj.status == Actions.PLAYING or player_obj.status == Actions.ALL_IN:
                n += 1
        return n

    def __str__(self):
        return "Poker: " + self.name + " \nPlayers:" + '\n'.join(
            [str(x) + "\n" for x in self.players.values()]) + " \nCard-State:" + str(
            self.card_state) + " \nCode-State:" + str(
            self.code_state) + " \nRound:" + str(self.round) + " \nNext:" + str(self.next_player) + " \nOpen:" + str(
            self.open) + " \nBet:" + str(
            self.current_bet)
