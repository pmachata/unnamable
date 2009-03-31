# This module populates the cup with all monsters except those that
# have the "in_cup" attribute == False

import arkham

class Module (arkham.Module):
    def __init__ (self):
        arkham.Module.__init__ (self, "monster", "Populate Monster Cup")
        self.m_ancients = []

    def consistent (self, mod_index):
        return True

    def before_turn_0 (self, game):
        for monster in game.registered_monsters ():
            if ((not monster.attributes ().has ("in_cup"))
                or monster.attributes ().flag ("in_cup")):
                game.put_monster_in_cup (monster)
