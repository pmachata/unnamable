import arkham
import item

class SkillDeck (arkham.Deck):
    def __init__ (self):
        arkham.Deck.__init__ (self, "Skill Deck", arkham.Item)

class SkillItem (arkham.InvestigatorItem):
    pass

class ModuleProto (arkham.ModuleProto):
    def __init__ (self):
        arkham.ModuleProto.__init__ (self, "skill", "Skill Deck")
        self.SkillDeck = SkillDeck
        self.SkillItem = SkillItem

    def consistent (self, mod_index):
        return True

    def construct (self, game):
        game.add_deck (SkillDeck)

    def before_turn_0 (self, game):
        game.deck (SkillDeck).initialize ()
