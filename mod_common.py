import arkham
import item

class CommonItem (arkham.InvestigatorItem):
    pass

class CommonDeck (arkham.Deck):
    def __init__ (self):
        arkham.Deck.__init__ (self, "Common Items", arkham.Item)
        self.Item = CommonItem

class ModuleProto (arkham.ModuleProto):
    def __init__ (self):
        arkham.ModuleProto.__init__ (self, "common", "Common Items")
        self.CommonDeck = CommonDeck

    def consistent (self, mod_index):
        return True

    def construct (self, game):
        game.add_deck (CommonDeck)

    def before_turn_0 (self, game):
        game.deck (CommonDeck).initialize ()
