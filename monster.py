from checks import *
from damage import *
from obj import *

class MonsterProto (ObjectWithAttributes):
    def __init__ (self, name, **attributes):
        ObjectWithAttributes.__init__ (self)
        self.m_name = name
        self.apply_attributes (attributes)

    def name (self):
        return self.m_name

    # Override in subclass
    def movement (self, game):
        raise NotImplementedError ()

    # Combat phases.
    def pre_combat (self, combat, investigator):
        return []

    def combat_turn (self, combat, investigator):
        return []

    # We just need those.
    def evade_check (self):
        raise NotImplementedError ()

    def horror_check (self):
        raise NotImplementedError ()

    def combat_check (self):
        raise NotImplementedError ()

    def horror_damage (self):
        raise NotImplementedError ()

    def combat_damage (self):
        raise NotImplementedError ()

class BasicMonster (MonsterProto):
    def __init__ (self, name,
                  evade_check,
                  horror_check, horror_damage,
                  combat_check, combat_damage,
                  **attributes):
        MonsterProto.__init__ (self, name, **attributes)
        self.m_evade_check = evade_check
        self.m_horror_check = horror_check
        self.m_horror_damage = horror_damage
        self.m_combat_check = combat_check
        self.m_combat_damage = combat_damage

    def evade_check (self):
        return self.m_evade_check

    def horror_check (self):
        return self.m_horror_check

    def combat_check (self):
        return self.m_combat_check

    def horror_damage (self):
        return self.m_horror_damage

    def combat_damage (self):
        return self.m_combat_damage

class SimpleMonster (BasicMonster):
    def __init__ (self, name,
                  awareness,
                  (horror_rating, horror_damage),
                  toughness,
                  (combat_rating, combat_damage),
                  **attributes):
        BasicMonster.__init__ (self, name,
                               evade_check (awareness),
                               horror_check (horror_rating),
                               DamageSanity (horror_damage),
                               combat_check (combat_rating, toughness),
                               DamageStamina (combat_damage),
                               **attributes)
