from treys import Card, Deck, Evaluator
import math

players = ["p1", "p2", "p3", "p4"]

ranks = {0: "2", 1: "3", 2: "4", 3: "5", 4: "6", 5: "7", 6: "8", 7: "9", 8: "T", 9: "J", 10: "Q", 11: "K", 12: "A"}
suits = {0: "s", 1: "h", 2: "d", 3: "c"}


def deal_cards():

    pass


def treys_card_to_int(card):

    return int(Card.get_rank_int(card) + 13 * math.log(Card.get_suit_int(card),2))


def int_to_trey_card(card_int):

    return Card.new(ranks[card_int % 13] + suits[card_int // 13])


if __name__ == "__main__":

    deck = Deck()
    test = deck.draw(5)
    Card.print_pretty_cards(test)

    for i in range(len(test)):
        test[i] = int_to_trey_card(treys_card_to_int(test[i]))

    Card.print_pretty_cards(test)



