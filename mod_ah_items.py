import arkham
import checks
import fun

def build (game, module):

    # xxx .18 Derringer cannot be lost or stolen unless you choose to
    # allow it.
    class Derringer18 (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, ".18 Derringer", 3, 1)

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Derringer18), fun.matchvalue ("combat"))
    def do (game, investigator, subject, item, skill_name):
        return 2

    module.m_common_deck.register (Derringer18 (), 1)

    # ---

    class Revolver38 (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, ".38 Revolver", 4, 1)

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Revolver38), fun.matchvalue ("combat"))
    def do (game, investigator, subject, item, skill_name):
        return 3

    module.m_common_deck.register (Revolver38 (), 1)

    # ---

    class Automatic45 (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, ".45 Automatic", 5, 1)

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Revolver38), fun.matchvalue ("combat"))
    def do (game, investigator, subject, item, skill_name):
        return 4

    module.m_common_deck.register (Automatic45 (), 1)

    # ---

    class xxxAncientTome:
        pass

    class xxxAxe:
        """Bonus: +2 Combat check (+3 instead if your other hand is empty)"""
        pass

    # ---

    class Bullwhip (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Bullwhip", 2, 1)

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Bullwhip), fun.matchvalue ("combat"))
    def do (game, investigator, subject, item, skill_name):
        return 1

    @arkham.check_correction_actions_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Bullwhip), fun.matchvalue ("combat"), fun.any)
    def do (game, investigator, subject, item, skill_name, roll):
        if not item.exhausted ():
            return [arkham.GameplayAction_Multiple \
                        ([arkham.GameplayAction_Exhaust (item),
                          arkham.GameplayAction_Reroll (subject, skill_name, roll)])]
        else:
            return []

    module.m_common_deck.register (Bullwhip (), 1)

    # ---

    class CavalrySaber (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Cavalry Saber", 3, 1)

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (CavalrySaber), fun.matchvalue ("combat"))
    def do (game, investigator, subject, item, skill_name):
        return 2

    module.m_common_deck.register (CavalrySaber (), 1)

    # ---

    class Cross (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Cross", 3, 1)

    @arkham.bonus_hook.match \
        (fun.any, fun.any, arkham.match_flag ("undead"),
         arkham.match_proto (Cross), fun.matchvalue ("combat"))
    def do (game, investigator, subject, item, skill_name):
        return 3

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Cross), fun.matchvalue ("horror"))
    def do (game, investigator, subject, item, skill_name):
        return 1

    module.m_common_deck.register (Cross (), 1)

    # ---

    class DarkCloak (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Dark Cloak", 2, 0)

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (DarkCloak), fun.matchvalue ("evade"))
    def do (game, investigator, subject, item, skill_name):
        return 1

    module.m_common_deck.register (DarkCloak (), 1)

    # ---

    class xxxDynamite:
        """Bonus: +8 Combat check (Discard after use)"""
        pass

    class xxxFood:
        """Any phase: Discard Food to reduce any Stamina loss by 1."""
        pass

    # ---

    class Knife (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Knife", 2, 1)

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Knife), fun.matchvalue ("combat"))
    def do (game, investigator, subject, item, skill_name):
        return 1

    module.m_common_deck.register (Knife (), 1)

    # ---

    class Lantern (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Lantern", 3, 0)

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Knife), fun.matchvalue ("luck"))
    def do (game, investigator, subject, item, skill_name):
        return 1

    module.m_common_deck.register (Lantern (), 1)

    # ---

    class LuckyCigaretteCase (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Lucky Cigarette Case", 1, 0)

    @arkham.check_correction_actions_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (LuckyCigaretteCase), fun.any, fun.any)
    def do (game, investigator, subject, item, skill_name, roll):
        return [arkham.GameplayAction_Multiple \
                    ([arkham.GameplayAction_Discard (item),
                      arkham.GameplayAction_Reroll (subject, skill_name, roll)])]

    module.m_common_deck.register (LuckyCigaretteCase (), 1)

    # ---

    class MapOfArkham (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Map of Arkham", 2, 0)

        def movement (self, game, owner, item):
            if owner.movement_points () != None and not item.exhausted ():
                # i.e. the movement is not over yet
                return [arkham.GameplayAction_Multiple \
                            ([arkham.GameplayAction_Exhaust (item),
                              arkham.GameplayAction_GainMovementPoints (1)])]
            else:
                return []

    module.m_common_deck.register (MapOfArkham (), 1)
