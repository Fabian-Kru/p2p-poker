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

        self.table_state = {}
        self.players = {}
        self.card_state = {}
        self.round = 0

    def deal_cards(self):
        """
        Generates a dictionary with key lists for each player and cards with one number replaced to encode the cards.
        :return: the generated dictionary
        """

        self.table_state = {}
        deck = Deck()

        self.table_state["board"] = deck.draw(5)
        for player in self.players:
            self.table_state[player] = deck.draw(2)

        key_dict = {}
        
        for place in self.table_state:
            
            key_dict[place] = []
            
            for card_treys in self.table_state[place]:
                
                key_dict[place].append(self.generate_key_list(card_treys))

        n = 0
        code_dict = {}

        for player in players:

            code_dict[player] = {}

            for place in key_dict:

                code_dict[player][place] = []

                for key_list in key_dict[place]:

                    temp_list = key_list.copy()
                    temp_list[n] = 52
                    code_dict[player][place].append(temp_list)

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


if __name__ == "__main__":

    poker = Poker()

    cd = poker.deal_cards()

    Card.print_pretty_cards(poker.table_state["board"])

    board_list = []

    for i in range(5):
        card = poker.key_list_to_card(poker.decode_key_lists(cd["p1"]["board"][i], cd["p2"]["board"][i]))
        board_list.append(card)

    Card.print_pretty_cards(board_list)

    pprint(cd)