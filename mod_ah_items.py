import arkham
import checks
import fun

def build (game, module):

    def plain_item (name, price, hands, **bonuses):
        class PlainItem (arkham.InvestigatorItem):
            def __init__ (self):
                arkham.InvestigatorItem.__init__ (self, name, price, hands)

        for key, value in bonuses.iteritems ():
            @arkham.bonus_hook.match \
                (fun.any, fun.any, fun.any, arkham.match_proto (PlainItem), fun.matchvalue (key))
            def do (game, investigator, subject, item, skill_name):
                return value

        return PlainItem ()

    # xxx .18 Derringer cannot be lost or stolen unless you choose to
    # allow it.
    class Derringer18 (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, ".18 Derringer", 3, 1)

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Derringer18), fun.matchvalue ("combat"))
    def do (game, investigator, subject, item, skill_name):
        return 2

    # ---

    class xxxAncientTome:
        pass

    class Axe (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Axe", 3, 1)

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Axe), fun.matchvalue ("combat"))
    def do (game, investigator, subject, item, skill_name):
        # Do we have one extra hand capable of holding this axe?
        if investigator.find_wield (game, item, 1):
            return 3
        else:
            return 2

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

    # ---

    class xxxDynamite:
        """Bonus: +8 Combat check (Discard after use)"""
        pass

    class xxxFood:
        """Any phase: Discard Food to reduce any Stamina loss by 1."""
        pass

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

    # ---

    class Motorcycle (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Motorcycle", 4, 0)

        def movement (self, game, owner, item):
            if owner.movement_points () != None and not item.exhausted ():
                # i.e. the movement is not over yet
                return [arkham.GameplayAction_Multiple \
                            ([arkham.GameplayAction_Exhaust (item),
                              arkham.GameplayAction_GainMovementPoints (2)])]
            else:
                return []

    # ---

    class xxxOldJournal:
        """Movement: Exhaust and spend 1 movement point to make a Lore
        (-1) check. If you pass, gain 3 Clue tokens and discard Old
        Journal. If you fail, nothing happens."""
        pass

    # ---

    class ResearchMaterials (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Research Materials", 1, 0)

    @arkham.spend_clue_token_actions_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (ResearchMaterials), fun.any)
    def do (game, investigator, subject, item, skill_name):
        return [arkham.GameplayAction_Discard (item)]

    # ---

    class Shotgun (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Shotgun", 6, 2)

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Shotgun), fun.matchvalue ("combat"))
    def do (game, investigator, subject, item, skill_name):
        return 4

    @arkham.dice_roll_successes_bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Shotgun), fun.matchvalue ("combat"), fun.matchvalue (6))
    def do (game, investigator, subject, item, skill_name, dice):
        return 1

    # ---

    class xxxWhiskey:
        """Any phase: Discard Whiskey to reduce any Sanity loss by 1."""
        pass

    # ---

    for item_proto, count in [
            (Derringer18 (), 1),
            (plain_item (".38 Revolver", 4, 1, combat=3), 1),
            (plain_item (".45 Automatic", 5, 1, combat=4), 1),
            (Axe (), 1),
            (Bullwhip (), 1),
            (plain_item ("Cavalry Saber", 3, 1, combat=2), 1),
            (Cross (), 1),
            (plain_item ("Dark Cloak", 2, 0, evade=1), 1),
            (plain_item ("Knife", 2, 1, combat=1), 1),
            (plain_item ("Lantern", 3, 0, luck=1), 1),
            (LuckyCigaretteCase (), 1),
            (MapOfArkham (), 1),
            (Motorcycle (), 1),
            (ResearchMaterials (), 1),
            (plain_item ("Rifle", 6, 2, combat=5), 1),
            (Shotgun (), 1),
            (plain_item ("Tommy Gun", 7, 2, combat=6), 1)
        ]:
        module.m_common_deck.register (item_proto, count)
