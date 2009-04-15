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

    def tome (name, price, movement_points, check, success_action):
        class Tome (arkham.InvestigatorItem):
            def __init__ (self):
                arkham.InvestigatorItem.__init__ (self, name, price, 0)

            def movement (self, game, owner, item):
                mp = owner.movement_points ()
                if mp != None and mp >= movement_points and not item.exhausted ():
                    """Exhaust and spend MOVEMENT_POINTS to make a
                    CHECK. If you pass, do ACTION and discard Ancient
                    Tome. If you fail, nothing happens."""
                    return [
                        arkham.GameplayAction_Multiple \
                            ([arkham.GameplayAction_Exhaust (item),
                              arkham.GameplayAction_SpendMovementPoints (movement_points),
                              arkham.GameplayAction_Conditional \
                                  (game, owner, item, check,
                                   arkham.GameplayAction_Multiple \
                                       ([success_action,
                                         arkham.GameplayAction_Discard (item)]))])
                        ]
                else:
                    return []

        return Tome ()

    # ---

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

    class Dynamite (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Dynamite", 4, 2)
            """Bonus: +8 Combat check (Discard after use)"""

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Dynamite), fun.matchvalue ("combat"))
    def do (game, investigator, subject, item, skill_name):
        return 8

    @arkham.item_after_use_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Dynamite), fun.matchvalue ("combat"))
    def do (game, investigator, subject, item, skill_name):
        investigator.discard_item (item)

    # ---

    class Food (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Food", 1, 0)

    @arkham.damage_correction_actions_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Food),
         lambda damage: arkham.health_stamina in damage.aspects ())
    def do (game, investigator, subject, item, damage):
        return [arkham.GameplayAction_Multiple \
                    ([arkham.GameplayAction_Discard (item),
                      arkham.GameplayAction_ReduceDamage (damage, arkham.health_stamina, 1)])]

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

    class Whiskey (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Whiskey", 1, 0)

    @arkham.damage_correction_actions_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Food),
         lambda damage: arkham.health_sanity in damage.aspects ())
    def do (game, investigator, subject, item, damage):
        return [arkham.GameplayAction_Multiple \
                    ([arkham.GameplayAction_Discard (item),
                      arkham.GameplayAction_ReduceDamage (damage, arkham.health_sanity, 1)])]

    # ---

    for count, item_proto in [
            (1, Derringer18 ()),
            (1, plain_item (".38 Revolver", 4, 1, combat=3)),
            (1, plain_item (".45 Automatic", 5, 1, combat=4)),
            (1, tome ("Ancient Tome", 4, 2,
                      arkham.SkillCheck ("lore", -1),
                      # xxx should be spell deck
                      arkham.GameplayAction_DrawItem (module.m_common_deck))),
            (1, Axe ()),
            (1, Bullwhip ()),
            (1, plain_item ("Cavalry Saber", 3, 1, combat=2)),
            (1, Cross ()),
            (1, plain_item ("Dark Cloak", 2, 0, evade=1)),
            (1, Dynamite ()),
            (1, Food ()),
            (1, plain_item ("Knife", 2, 1, combat=1)),
            (1, plain_item ("Lantern", 3, 0, luck=1)),
            (1, LuckyCigaretteCase ()),
            (1, MapOfArkham ()),
            (1, Motorcycle ()),
            (1, tome ("Old Journal", 1, 1,
                      arkham.SkillCheck ("lore", -1),
                      arkham.GameplayAction_GainClues (3))),
            (1, ResearchMaterials ()),
            (1, plain_item ("Rifle", 6, 2, combat=5)),
            (1, Shotgun ()),
            (1, plain_item ("Tommy Gun", 7, 2, combat=6)),
            (1, Whiskey ())
        ]:
        module.m_common_deck.register (item_proto, count)
