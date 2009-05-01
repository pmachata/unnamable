import obj
class Skill (obj.NamedObject):
    def __repr__ (self):
        return "<Skill \"%s\">" % self.name ()

skill_fight = Skill ("fight")
skill_lore = Skill ("lore")
skill_luck = Skill ("luck")
skill_sneak = Skill ("sneak")
skill_speed = Skill ("speed")
skill_will = Skill ("will")

class SkillScales:
    def __init__ (self, len, speed, sneak, fight, will, lore, luck):
        assert len > 0
        self.m_length = len #scale length
        self.m_skills = {
            skill_speed: speed,
            skill_sneak: sneak - len + 1,
            skill_fight: fight,
            skill_will: will - len + 1,
            skill_lore: lore,
            skill_luck: luck - len + 1}

    def skill (self, skill):
        return self.m_skills[skill]
