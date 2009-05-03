import arkham
from obj import NamedObject, SubjectProto
from deck import DeckItem

class ResistanceLevel (NamedObject):
    def __init__ (self, name, modifier):
        NamedObject.__init__ (self, name)
        self.m_modifier = modifier

    def modify (self, bonus):
        return arkham.Bonus (self.m_modifier (bonus.value ()), bonus.family ())

reslev_none = ResistanceLevel ("none", lambda val: val)
reslev_resistance = ResistanceLevel ("resistance", lambda val: (val + 1) / 2)
reslev_immunity = ResistanceLevel ("immunity", lambda val: 0)

class Family (NamedObject):
    pass

family_indifferent = Family ("indifferent")
family_physical = Family ("physical")
family_magical = Family ("magical")

class MonsterSpecialAbility (NamedObject):
    pass

class MonsterResistance (MonsterSpecialAbility):
    def __init__ (self, family):
        MonsterSpecialAbility.__init__ (self, family.name ())
        self.m_family = family

    def family (self):
        return self.m_family

monster_physical = MonsterResistance (family_physical)
monster_magical = MonsterResistance (family_magical)

monster_nightmarish = MonsterSpecialAbility ("nightmarish")
monster_overwhelming = MonsterSpecialAbility ("overwhelming")

class MonsterProto (DeckItem, SubjectProto):
    def __init__ (self, name, special_abilities = {}, **attributes):
        DeckItem.__init__ (self, name, **attributes)
        SubjectProto.__init__ (self, special_abilities)

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

    def horror_harm (self):
        raise NotImplementedError ()

    def combat_harm (self):
        raise NotImplementedError ()

class BasicMonster (MonsterProto):
    def __init__ (self, name,
                  evade_check,
                  horror_check, horror_harm,
                  combat_check, combat_harm,
                  special_abilities = set (),
                  **attributes):

        for fam in ("physical", "magical"):
            assert fam not in attributes

        MonsterProto.__init__ (self, name, special_abilities, **attributes)

        self.m_evade_check = evade_check
        self.m_horror_check = horror_check
        self.m_horror_harm = horror_harm
        self.m_combat_check = combat_check
        self.m_combat_harm = combat_harm

    def evade_check (self):
        return self.m_evade_check

    def horror_check (self):
        return self.m_horror_check

    def combat_check (self):
        return self.m_combat_check

    def horror_harm (self):
        return self.m_horror_harm

    def combat_harm (self):
        return self.m_combat_harm

class SimpleMonster (BasicMonster):
    def __init__ (self, name,
                  awareness,
                  (horror_rating, horror_damage),
                  toughness,
                  (combat_rating, combat_damage),
                  special_abilities = set (),
                  **attributes):
        BasicMonster.__init__ (self, name,
                               arkham.evade_check (awareness),
                               arkham.horror_check (horror_rating),
                               arkham.HarmSanity (horror_damage),
                               arkham.combat_check (combat_rating, toughness),
                               arkham.HarmStamina (combat_damage),
                               special_abilities,
                               **attributes)
