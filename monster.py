import arkham
from deck import DeckItem

class MonsterProto (DeckItem):
    def __init__ (self, name, **attributes):
        DeckItem.__init__ (self, name, **attributes)

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

    # Resistances.  See check_hooks.py for definitions.
    def resistances (self):
        raise NotImplementedError ()

    def resistance (self, family):
        return self.resistances ().get (family, arkham.reslev_none)

class BasicMonster (MonsterProto):
    def __init__ (self, name,
                  evade_check,
                  horror_check, horror_damage,
                  combat_check, combat_damage,
                  **attributes):

        res = {}
        for fam in ("physical", "magical"):
            if fam in attributes:
                assert fam not in res
                lev = attributes[fam]
                res[fam] = lev
                del attributes[fam]
                assert lev in ["resistance", "immunity"]

        MonsterProto.__init__ (self, name, **attributes)

        self.m_evade_check = evade_check
        self.m_horror_check = horror_check
        self.m_horror_damage = horror_damage
        self.m_combat_check = combat_check
        self.m_combat_damage = combat_damage

        self.m_resistances \
            = dict (({"physical": arkham.family_physical,
                      "magical": arkham.family_magical}[fam],
                     {"resistance": arkham.reslev_resistance,
                      "immunity": arkham.reslev_immunity}[lev])
                    for fam, lev in res.iteritems ())

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

    def resistances (self):
        return self.m_resistances

class SimpleMonster (BasicMonster):
    def __init__ (self, name,
                  awareness,
                  (horror_rating, horror_damage),
                  toughness,
                  (combat_rating, combat_damage),
                  **attributes):
        BasicMonster.__init__ (self, name,
                               arkham.evade_check (awareness),
                               arkham.horror_check (horror_rating),
                               arkham.HarmSanity (horror_damage),
                               arkham.combat_check (combat_rating, toughness),
                               arkham.HarmStamina (combat_damage),
                               **attributes)
