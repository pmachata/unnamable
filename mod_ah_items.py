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

    class Tome (arkham.InvestigatorItem):
        pass

    def complex (klass, name, price, movement_points, harm, check,
                 success_action_ctor, fail_action_ctor = lambda game, owner, item: None):
        class ComplexItem (klass):
            def __init__ (self):
                klass.__init__ (self, name, price, 0)

            def movement (self, game, owner, item):
                mp = owner.movement_points ()
                # We don't check whether the investigator can sustain
                # the harm before offering the action, because the
                # player may wish to perform that action nonetheless.
                # Besides the investigator can have a couple aces up
                # his sleeve, such as a card that reduces caused
                # damage by 1.  Checking accurately for that is not
                # worth the trouble.
                if mp != None and mp >= movement_points and not item.exhausted ():
                    """Exhaust and spend MOVEMENT_POINTS to make a
                    CHECK. If you pass, do ACTION and discard Ancient
                    Tome. If you fail, nothing happens."""
                    return [
                        arkham.GameplayAction_Multiple \
                            ([arkham.GameplayAction_Exhaust (item),
                              arkham.GameplayAction_SpendMovementPoints (movement_points),
                              arkham.GameplayAction_CauseHarm (game, owner, item, harm) if harm else None,
                              arkham.GameplayAction_Conditional \
                                  (game, owner, item, check,
                                   arkham.GameplayAction_Multiple \
                                       ([success_action_ctor (game, owner, item),
                                         arkham.GameplayAction_Discard (item)]),
                                   fail_action_ctor (game, owner, item))])
                        ]
                else:
                    return []

        return ComplexItem ()

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
        (fun.any, fun.any, fun.any, arkham.match_proto (Whiskey),
         lambda damage: arkham.health_sanity in damage.aspects ())
    def do (game, investigator, subject, item, damage):
        return [arkham.GameplayAction_Multiple \
                    ([arkham.GameplayAction_Discard (item),
                      arkham.GameplayAction_ReduceDamage (damage, arkham.health_sanity, 1)])]

    # ---

    # xxx fix combat=3 etc. won't work!
    for count, item_proto in [
            (1, Derringer18 ()),
            (1, plain_item (".38 Revolver", 4, 1, combat=3)),
            (1, plain_item (".45 Automatic", 5, 1, combat=4)),
            (1, complex (Tome, "Ancient Tome", 4, 2, None,
                         arkham.SkillCheck (arkham.checkbase_lore, -1),
                         # xxx should be spell deck
                         lambda game, owner, item: \
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
            (1, complex (Tome, "Old Journal", 1, 1, None,
                         arkham.SkillCheck (arkham.checkbase_lore, -1),
                         lambda game, owner, item: \
                             arkham.GameplayAction_GainClues (3))),
            (1, ResearchMaterials ()),
            (1, plain_item ("Rifle", 6, 2, combat=5)),
            (1, Shotgun ()),
            (1, plain_item ("Tommy Gun", 7, 2, combat=6)),
            (1, Whiskey ())
        ]:
        module.m_common_deck.register (item_proto, count)

    # -------------------------------------------------------------------------

    class AncientTablet (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Ancient Tablet", 8, 0)

        def movement (self, game, owner, item):
            movement_points = 3
            mp = owner.movement_points ()
            if mp != None and mp >= movement_points and not item.exhausted ():
                """Spend 3 movement points and discard Ancient Tablet
                to roll 2 dice.  For every success rolled, draw 1
                Spell.  For every failure rolled, gain 2 Clue tokens."""
                return [
                    arkham.GameplayAction_Multiple \
                        ([arkham.GameplayAction_SpendMovementPoints (movement_points),
                          arkham.GameplayAction_Discard (item),
                          arkham.GameplayAction_Repeat \
                              (2, arkham.GameplayAction_Conditional \
                                   (game, owner, item,
                                    arkham.SkillCheck (arkham.CheckBase_Fixed (1), 0),
                                    # xxx should be spell deck
                                    arkham.GameplayAction_DrawItem (module.m_common_deck),
                                    arkham.GameplayAction_GainClues (3)))])
                    ]
            else:
                return []

    # xxx implement Gate-closing checks
    # xxx this cannot be used against ancient one
    class BlueWatcherOfThePyramid (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ \
                (self, "Blue Watcher of the Pyramid", 4, 0)

        def combat_turn (self, game, owner, monster, item):
            """Lose 2 Stamina and discard Blue Watcher of the Pyramid
            to automatically succeed at a Combat check or a Fight
            check or Lore check made to close a gate."""
            return [
                arkham.GameplayAction_Multiple \
                    ([arkham.GameplayAction_CauseHarm (game, owner, monster,
                                                       arkham.HarmSanity (2)),
                      arkham.GameplayAction_Discard (item),
                      arkham.GameplayAction_SucceedCombatCheck ()
                      ])
                ]
    @arkham.check_correction_actions_hook.match \
        (fun.any, fun.any, fun.any,
         arkham.match_proto (BlueWatcherOfThePyramid),
         fun.matchvalue (arkham.checkbase_combat), fun.any)
    def do (game, investigator, subject, item, skill_name, roll):
        return item.combat_turn (game, investigator, subject)

    class BookOfDzyan (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ \
                (self, "Book of Dzyan", 3, 0)

        def movement (self, game, owner, item):
            """Movement: Exhaust and spend 2 movement points to make a
            Lore (-1) check. If you pass, draw 1 Spell, lose 1 Sanity,
            and put 1 Stamina token from the bank on Book of Dzyan. If
            there are 2 Stamina tokens on it, discard Book of
            Dzyan. If you fail, nothing happens. """
            movement_points = 3
            mp = owner.movement_points ()
            if mp != None and mp >= movement_points and not item.exhausted ():
                return [
                    arkham.GameplayAction_Multiple \
                        ([arkham.GameplayAction_Exhaust (item),
                          arkham.GameplayAction_SpendMovementPoints (movement_points),
                          arkham.GameplayAction_Conditional \
                              (game, owner, item,
                               arkham.SkillCheck (arkham.checkbase_lore, -1),
                               arkham.GameplayAction_Multiple \
                                   ([# xxx should be spell deck
                                     arkham.GameplayAction_DrawItem (module.m_common_deck),
                                     arkham.GameplayAction_CauseHarm \
                                         (game, owner, item, arkham.HarmSanity (1)),
                                     arkham.GameplayAction_MarkItem \
                                         (item, 2,
                                          arkham.GameplayAction_Discard (item))]))])
                    ]
            else:
                return []

    for count, item_proto in [
            (1, complex (arkham.InvestigatorItem, "Alien Statue", 5,
                         2, arkham.HarmSanity (1),
                         arkham.SkillCheck (arkham.CheckBase_Fixed (1), 0),
                         lambda game, owner, item: \
                             (arkham.GameplayAction_Select
                                  ([arkham.GameplayAction_GainClues (3),
                                    # xxx should be spell deck
                                    arkham.GameplayAction_DrawItem (module.m_common_deck)])),
                         lambda game, owner, item: \
                             arkham.GameplayAction_CauseHarm \
                                 (game, owner, item, arkham.HarmSanity (2)))),
            (1, AncientTablet ()),
            (1, BlueWatcherOfThePyramid ()),
            (1, BookOfDzyan ()),
        ]:
        module.m_unique_deck.register (item_proto, count)
