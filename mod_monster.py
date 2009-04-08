# This module populates the cup with all monsters except those that
# have the "in_cup" attribute == False

import arkham

class MonsterCup (arkham.Deck):
    def __init__ (self):
        arkham.Deck.__init__ (self, "Monster Cup", arkham.Monster)

class ModuleProto (arkham.ModuleProto):
    def __init__ (self):
        arkham.ModuleProto.__init__ (self, "monster", "Monster Cup")
        self.MonsterCup = MonsterCup

    def consistent (self, mod_index):
        return True

    def construct (self, game):
        game.add_deck (MonsterCup)

    def before_turn_0 (self, game):
        game.deck (MonsterCup).initialize ()
