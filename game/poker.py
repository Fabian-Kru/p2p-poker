import math
import random
import time

import treys
from treys import Card, Deck

from data.game.GameUpdateMessage import GameUpdateMessage
from game import player, gamemanager
from game.game_util import Actions
from util.logging import log

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
        self.card_requests = []
        self.triggerd = False

    def new_round(self):
        self.triggerd = False
        self.card_state = {}
        self.code_state = {}
        self.round = 0
        self.current_bet = 0
        self.open = False
        for _, players in self.players.items():
            players.new_round()

    def request_card_codes(self, card_string):
        self.card_requests.append(card_string)
        gamemanager.active_game_master.get_master().deliver_card_code(self.game_id, self.name, card_string)

    def set_next_player(self):

        next = False
        for name, player in self.players.items():

            print(player)

            if player.status == Actions.DEALER:
                next = True
            elif next:
                self.next_player = player
                return

        if next:
            self.next_player = self.players[list(self.players.keys())[0]]

    def deal_cards(self):
        """
        Generates a dictionary with key lists for each player and cards with one number replaced to encode the cards.
        :return: the generated dictionary
        """

        self.players[self.name].status = Actions.DEALER

        self.card_state = {}
        deck = Deck()

        self.card_state["board"] = deck.draw(5)

        for player_name in self.get_active_players():
            self.card_state[player_name] = deck.draw(2)

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

        for player_name in player_list:
            if player_name != self.name:
                self.players[player_name] = player.Player(player_name)
                if next:
                    self.next_player = self.players[player_name]
            else:
                self.players[player_name] = player.Player(player_name)


    def next_round(self, game_master, game):
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
                    for p in self.get_active_players():
                        self.request_card_codes(p)

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
        print(card_string, self.round, self.__card_permission(card_string, client_name))
        if self.__card_permission(card_string, client_name):
            match card_string:
                case "b1":
                    return self.code_state["board"][0:3]
                case "b2":
                    return [self.code_state["board"][3]]
                case "b3":
                    return [self.code_state["board"][4]]
                case _:
                    return self.code_state[card_string]

    def receive_card_codes(self, card_string, code_list, game_master, game):
        if card_string in self.card_requests:
            self.card_requests.remove(card_string)
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
                case "b3":
                    self.card_state["board"].append(
                        key_list_to_card(decode_key_lists(code_list[0], self.code_state["board"][4])))

        if self.round == 4 and not self.card_requests and not self.triggerd:
            self.triggerd = True
            log("[game] sending trigger_end")
            self.trigger_end()

    def player_action(self, game_master, game, player_name, action, chips) -> int:
        self.played = True
        print(self.players)
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
                                          player_name + ":" + str(chips) + ":" + str(self.current_bet) + ":" + str(
                                              old_bet))
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
                        GameUpdateMessage(game, "action:check", player_name + ":" + str(status))

                    )
            case "call":
                print("call")
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
                print("action not found")
                status = Actions.ERROR_ACTION_NOT_FOUND

        if self.get_active_player_number() == 1:
            for p in game.poker.players:
                game_master.handle_update(
                    p,
                    p,
                    GameUpdateMessage(game, "trigger_end", "trigger_end"))
        else:
            plist = []
            for pl, _ in self.players.items():
                plist.append(pl)
            next_player = plist[0]

            for i, players in enumerate(plist):
                if players == self.next_player.name:
                    ii = 1
                    next_player = plist[(i + ii) % len(plist)]

                    while next_player not in self.get_active_players_playing():
                        ii += 1
                        next_player = plist[(i + ii) % len(plist)]

                    self.next_player = self.players[next_player]
                    break

            print("next_player", next_player)
            if ("check" in self.players[next_player].available_actions(self.current_bet)
                    and self.players[next_player].played):
                print(self.name)
                for p in game.poker.players:
                    if p == self.name:
                        continue
                    game_master.handle_update(
                        p,
                        p,
                        GameUpdateMessage(game, "next_round", "next_round"))

                game_master.handle_update(
                    self.name,
                    self.name,
                    GameUpdateMessage(game, "next_round", "next_round"))

            else:
                for p in game.poker.players:
                    game_master.handle_update(
                        p,
                        p,
                        GameUpdateMessage(game, "next_player", next_player))

        self.check_open()
        return status

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

    def trigger_end(self) -> None:
        self.triggerd = True
        if self.get_active_player_number() > 1:

            values = {}

            for player_name in self.card_state:
                if player_name != "board":
                    values[player_name] = self.evaluator.evaluate(self.card_state[player_name],
                                                                  self.card_state["board"])

            chips_left_in_pot = True

            print("values ", values)

            while chips_left_in_pot:
                chips_left_in_pot = False

                winner = max(values, key=values.get)
                del values[winner]

                chips = self.players[winner].bet

                winnings = 0

                for player_name in self.players:
                    bet, bet_empty = self.players[player_name].get_winnings(chips)
                    winnings += bet
                    if not bet_empty:
                        chips_left_in_pot = True

                print(winner, winnings)
                self.players[winner].chips += winnings
        else:
            pot = 0
            for name, p in self.players.items():
                pot += p.bet
            winner = self.get_active_players()[0]
            self.players[winner].chips += pot
            print("Winner: ", winner)

    def get_active_player_number(self):
        return len(self.get_active_players())

    def get_active_players(self):
        list = []
        for name, player_obj in self.players.items():
            if player_obj.status == Actions.PLAYING or player_obj.status == Actions.ALL_IN:
                list.append(name)

        return list

    def get_active_players_playing(self):
        list = []
        for name, player_obj in self.players.items():
            if player_obj.status == Actions.PLAYING:
                list.append(name)

        return list

    def __str__(self):
        return "Poker: " + self.name + " \nPlayers:" + '\n'.join(
            [str(x) + "\n" for x in self.players.values()]) + " \nCard-State:" + str(
            self.card_state) + " \nCode-State:" + str(
            self.code_state) + " \nRound:" + str(self.round) + " \nNext:" + str(self.next_player) + " \nOpen:" + str(
            self.open) + " \nBet:" + str(
            self.current_bet)
