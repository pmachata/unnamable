import arkham

class Ancient:
    def __init__ (self, name):
        self.m_name = name

    def name (self):
        return self.m_name

    # Override in subclass
    def before_turn_0 (self, game):
        pass

class ModuleProto (arkham.ModuleProto):
    def __init__ (self):
        arkham.ModuleProto.__init__ (self, "ancient", "Ancient One")
        self.Ancient = Ancient
        self.m_ancients = []

    def consistent (self, mod_index):
        return True

    def register (self, ancient):
        self.m_ancients.append (ancient)

    def pick (self):
        import random
        ancient = random.choice (self.m_ancients) ()
        return ancient

    def before_turn_0 (self, game):
        ancient = self.pick ()
        game.add_extra_board_monster (ancient)
        ancient.before_turn_0 (game)
