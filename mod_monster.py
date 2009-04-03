# This module populates the cup with all monsters except those that
# have the "in_cup" attribute == False

import arkham

class ModuleProto (arkham.ModuleProto):
    def __init__ (self):
        arkham.ModuleProto.__init__ (self, "monster", "Populate Monster Cup")
        self.m_ancients = []

    def consistent (self, mod_index):
        return True

    def before_turn_0 (self, game):
        for monster in game.registered_monsters ():
            if ((not monster.attributes ().has ("in_cup"))
                or monster.attributes ().flag ("in_cup")):
                game.put_monster_in_cup (monster)
