import arkham
import item

class UniqueDeck (arkham.Deck):
    def __init__ (self):
        arkham.Deck.__init__ (self, "Unique Items", arkham.Item)

class ModuleProto (arkham.ModuleProto):
    def __init__ (self):
        arkham.ModuleProto.__init__ (self, "unique", "Unique Items")
        self.UniqueDeck = UniqueDeck

    def consistent (self, mod_index):
        return True

    def construct (self, game):
        game.add_deck (UniqueDeck)

    def before_turn_0 (self, game):
        game.deck (UniqueDeck).initialize ()
