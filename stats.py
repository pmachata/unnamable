import arkham

class Statset:
    def __init__ (self, len, speed, sneak, fight, will, lore, luck):
        assert len > 0
        self.m_length = len #scale length
        self.m_speed = speed
        self.m_sneak = sneak - len + 1
        self.m_fight = fight
        self.m_will = will - len + 1
        self.m_lore = lore
        self.m_luck = luck - len + 1

class Module (arkham.Module):
    def __init__ (self):
        arkham.Module.__init__ (self, "statset", "Basic Stats")
        self.Statset = Statset

    def consistent (self, mod_index):
        return True
