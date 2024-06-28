from treys import Card, Deck, Evaluator
import math
import random
from pprint import pprint
import player
import enums

ranks = {0: "2", 1: "3", 2: "4", 3: "5", 4: "6", 5: "7", 6: "8", 7: "9", 8: "T", 9: "J", 10: "Q", 11: "K", 12: "A"}
suits = {0: "s", 1: "h", 2: "d", 3: "c"}


class Poker:

    def __init__(self):

        self.card_state = {}
        self.players = {}
        self.code_state = {}
        self.round = 0
        self.next_player = ""
        self.name = ""
        self.open = False

    def new_round(self):
        self.round = 0
        self.card_state = {}
        self.code_state = {}
        self.open = False
        for player_name in self.players:
            player_name.new_round()

    def deal_cards(self):
        """
        Generates a dictionary with key lists for each player and cards with one number replaced to encode the cards.
        :return: the generated dictionary
        """

        self.card_state = {}
        deck = Deck()

        self.card_state["board"] = deck.draw(5)
        for player in self.players:
            self.card_state[player] = deck.draw(2)

        key_dict = {}
        
        for place in self.card_state:
            
            key_dict[place] = []
            
            for card_treys in self.card_state[place]:
                
                key_dict[place].append(self.generate_key_list(card_treys))

        n = 0
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


    def generate_key_list(self, card_treys):
        """
        Makes a list of numbers from 0 to 51 to encode the card received.
        :param card_treys: Takes a treys card
        :return: returns the list of 10 numbers
        """
        key_list = []
        card_int = self.card_treys_to_int(card_treys)

        for i in range(9):
            key_list.append(random.randrange(0,51))


        key_list.append((card_int - sum(key_list)) % 52)

        return key_list

    def decode_key_lists(self, key_list1, key_list2):
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

    def key_list_to_card(self, key_list):
        """
        Takes a key list and decodes it into a card
        :param key_list:
        :return: A treys card
        """
        return self.int_to_trey_card(sum(key_list) % 52)

    def card_treys_to_int(self, card_treys):
        """
        Turns an integer representation from the treys library into a 0 to 51 integer.
        :param card_treys:
        :return: 0-51 integer representation of card
        """

        return int(Card.get_rank_int(card_treys) + 13 * math.log(Card.get_suit_int(card_treys), 2))


    def int_to_trey_card(self, card_int):
        """
        Turns an 0-51 integer representation into a card from the treys library
        :param card_int:
        :return: A card from the treys library
        """

        return Card.new(ranks[card_int % 13] + suits[card_int // 13])

    def connect_to_players(self, player_list):

        next_is_next = False

        for player_tuple in player_list:
            if player_tuple[0] == self.name:
                self.players[player_tuple[0]] = player.Player(player_tuple[0], player_tuple[1])
                if next:
                    self.next_player = self.players[player_tuple[0]]
                    next_is_next = False
            else:
                self.players[player_tuple[0]] = player.Player(player_tuple[0], "")
                next_is_next = True

        if next_is_next:
            self.next_player = self.players[player_list[-1][0]]

    def request_card_codes(self, card_list):
        print(card_list)

    def next_round(self):

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
                    (self.request_card_codes("players"))

    def card_permission(self, card_string, socket):
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
                else:
                    return card_string in self.players and self.players[card_string].is_my_socket(socket)

    def get_card_codes(self, card_string, socket):

        if self.card_permission(card_string, socket):
            match card_string:
                case "b1":
                    return self.code_state["board"][0:2]
                case "b2":
                    return [self.code_state["board"][3]]
                case "b2":
                    return [self.code_state["board"][4]]
                case _:
                    return self.code_state[card_string]

    def receive_card_codes(self, card_string, code_list):
        if card_string in self.players:
            self.card_state[card_string] = []

            for card in zip(code_list, self.code_state[card_string]):
                self.card_state[card_string].append(self.key_list_to_card(self.decode_key_lists(card[0], card[1])))

        else:
            match card_string:
                case "b1":
                    self.card_state["board"] = []
                    for i in range(3):
                        self.card_state["board"].append(self.key_list_to_card(self.decode_key_lists(code_list[i], self.code_state["board"][i])))
                case "b2":
                    self.card_state["board"].append(self.key_list_to_card(self.decode_key_lists(code_list[0], self.code_state["board"][3])))
                case "b2":
                    self.card_state["board"].append(self.key_list_to_card(self.decode_key_lists(code_list[0], self.code_state["board"][4])))




if __name__ == "__main__":

    poker = Poker()

    cd = poker.deal_cards()

    Card.print_pretty_cards(poker.card_state["board"])

