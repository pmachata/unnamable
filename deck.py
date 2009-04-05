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
#  * draw: remove one card from the deck and return it
#  * give_back: re-insert once drawn card back to the deck
class Deck:
    def __init__ (self, name):
        self.m_name = name
        self.m_registered = {} # card -> count
        self.m_deck = []

    def name (self):
        return self.m_name

    def register (self, card, count):
        assert count > 0
        if card not in self.m_registered:
            self.m_registered[card] = 0
        self.m_registered[card] += count
        card.set_parental_deck (self)

    def registered_cards (self):
        return sum (([card] * count
                     for card, count in self.m_registered.iteritems ()), [])

    def cards (self):
        return list (self.m_deck)

    def draw (self, predicate = lambda arg: True):
        import random
        i, card = random.choice (list (enumerate (card
                                                  for card in self.m_deck
                                                  if predicate (card))))
        del self.m_deck[i]
        return card

    def give_back (self, card):
        self.m_deck.append (card)

    def activate (self, card):
        assert card in self.m_registered
        assert self.m_registered[card] > 0
        self.m_registered[card] -= 1
        self.m_deck.append (card)

    def withdraw (self, card):
        # xxx ugly linear lookup
        assert card in self.m_deck
        i = self.m_deck.index (card)
        del self.m_deck[i]
        self.m_registered[card] += 1

    # Seed the deck with all cards that don't have in_deck attribute
    # set to False.  (I.e. it's either True, or missing altogether.)
    def initialize (self):
        for card in self.registered_cards ():
            if ((not card.attributes ().has ("in_cup"))
                or card.attributes ().flag ("in_cup")):
                self.activate (card)


class DeckItem (Item):
    def __init__ (self, name, **kwargs):
        Item.__init__ (self, name, **kwargs)
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
