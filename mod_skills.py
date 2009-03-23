import arkham

class Skills:
    def __init__ (self, len, speed, sneak, fight, will, lore, luck):
        assert len > 0
        self.m_length = len #scale length
        self.m_speed = speed
        self.m_skills = dict (speed = speed,
                              sneak = sneak - len + 1,
                              fight = fight,
                              will = will - len + 1,
                              lore = lore,
                              luck = luck - len + 1)
        self.m_checks = dict (evade = "sneak",
                              horror = "will",
                              combat = "fight")

    def check (self, skill):
        if skill not in self.m_skills:
            skill = self.m_checks[skill]
        return self.m_skills[skill]

class Module (arkham.Module):
    def __init__ (self):
        arkham.Module.__init__ (self, "skills", "Skill Model")
        self.Skills = Skills

    def consistent (self, mod_index):
        return True
