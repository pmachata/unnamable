import arkham
import item

class SpellDeck (arkham.Deck):
    def __init__ (self):
        arkham.Deck.__init__ (self, "Spell Deck", arkham.Item)

class SpellItem (arkham.InvestigatorItem):
    pass

class SpellInst (arkham.InvestigatorItem):
    pass

class ModuleProto (arkham.ModuleProto):
    def __init__ (self):
        arkham.ModuleProto.__init__ (self, "spell", "Spell Deck")
        self.SpellDeck = SpellDeck
        self.SpellItem = SpellItem
        self.SpellInst = SpellInst

    def consistent (self, mod_index):
        return True

    def construct (self, game):
        game.add_deck (SpellDeck)

    def before_turn_0 (self, game):
        game.deck (SpellDeck).initialize ()
