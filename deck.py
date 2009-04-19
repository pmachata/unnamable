from item import *

# There are two parts of a deck: potential cards, and cards that
# actually end up being in the deck.  Potential cards are all cards
# known to game (such as all allies), but not all of them are in the
# deck (i.e. the ally got dropped from the deck as a result of terror
# track increase).  If Deck is used to model monster cup, potential
# cards are all monsters known to game, and the deck is a monster cup.
#
# Vocabulary:
#  * registered cards: have arity (each card comes in N copies)
#  * deck: subset of registered cards
#  * register: add new card to registered cards
#  * activate: move one registered card to deck
#  * withdraw: move one card from deck back to registered cards
#  * draw: remove one card from the deck and return its instance
#  * give_back: re-insert once drawn card back to the deck
class Deck:
    def __init__ (self, name, ctor):
        self.m_name = name
        self.m_registered = {} # card -> count
        self.m_deck = []
        self.m_ctor = ctor

    def name (self):
        return self.m_name

    def register (self, card_proto, count):
        assert count > 0
        if card_proto not in self.m_registered:
            self.m_registered[card_proto] = 0
        self.m_registered[card_proto] += count
        card_proto.set_parental_deck (self)

    def registered_cards (self):
        return sum (([card] * count
                     for card, count in self.m_registered.iteritems ()), [])

    def cards (self):
        return list (self.m_deck)

    def draw (self, predicate = lambda arg: True):
        import random
        i, card = random.choice ([(i, card)
                                  for i, card in enumerate (self.m_deck)
                                  if predicate (card)])
        del self.m_deck[i]
        return self.m_ctor (card)

    def give_back (self, card_proto):
        self.m_deck.append (card_proto)

    def activate (self, card_proto):
        assert card_proto in self.m_registered
        assert self.m_registered[card_proto] > 0
        self.m_registered[card_proto] -= 1
        self.m_deck.append (card_proto)

    def withdraw (self, card_proto):
        # xxx ugly linear lookup
        assert card_proto in self.m_deck
        i = self.m_deck.index (card_proto)
        del self.m_deck[i]
        self.m_registered[card_proto] += 1

    # Seed the deck with all cards that don't have in_deck attribute
    # set to False.  (I.e. it's either True, or missing altogether.)
    def initialize (self):
        for card_proto in self.registered_cards ():
            if ((not card_proto.attributes ().has ("in_cup"))
                or card_proto.attributes ().flag ("in_cup")):
                self.activate (card_proto)


class DeckItem (ItemProto):
    def __init__ (self, name, **kwargs):
        ItemProto.__init__ (self, name, **kwargs)
        self.m_parental_deck = None

    def discard (self):
        self.m_parental_deck.give_back (self)

    def set_parental_deck (self, parental_deck):
        assert self.m_parental_deck == None
        self.m_parental_deck = parental_deck

class InvestigatorItem (DeckItem):
    def __init__ (self, name, price, hands, **attributes):
        DeckItem.__init__ (self, name, **attributes)

        assert hands >= 0
        self.m_price = price
        self.m_hands = hands

    def hands (self):
        return self.m_hands

    def price (self):
        return self.m_price
