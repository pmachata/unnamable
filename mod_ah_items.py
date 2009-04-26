import arkham
import checks
import fun

def build (game, module):

    def plain_item (name, price, hands, bonuses, **attributes):
        def pop_attrib (attr, default):
            if attr not in attributes:
                return default
            ret = attributes[attr]
            del attributes[attr]
            return ret
        after_use = pop_attrib ("after_use", None)

        class PlainItem (arkham.InvestigatorItem):
            def __init__ (self):
                arkham.InvestigatorItem.__init__ (self, name, price, hands, **attributes)

        for check_base, bonus in bonuses.iteritems ():
            @arkham.bonus_hook.match \
                (fun.any, fun.any, fun.any,
                 arkham.match_proto (PlainItem), fun.val == check_base)
            def do (game, investigator, subject, item, check_base):
                return bonus

            if after_use:
                @arkham.item_after_use_hook.match \
                    (fun.any, fun.any, fun.any,
                     arkham.match_proto (PlainItem), fun.val == check_base)
                def do (game, investigator, subject, item, check_base):
                    return after_use (game, investigator, item)

        return PlainItem ()

    class Tome (arkham.InvestigatorItem):
        pass

    def complex (cls, name, price, movement_points, harm, check,
                 success_action_ctor,
                 fail_action_ctor = lambda game, owner, item: None):

        class ComplexItem (cls):
            def __init__ (self):
                cls.__init__ (self, name, price, 0)

            def movement (self, game, owner, item):
                mp = owner.movement_points ()
                # We don't check whether the investigator can sustain
                # the harm before offering the action, because the
                # player may wish to perform that action nonetheless.
                # Besides the investigator can have a couple aces up
                # his sleeve, such as a card that reduces caused
                # damage by 1.  Checking accurately for that is not
                # worth the trouble.
                if mp != None and mp >= movement_points \
                        and not item.exhausted ():
                    """Exhaust and spend MOVEMENT_POINTS to make a
                    CHECK. If you pass, do ACTION and discard Ancient
                    Tome. If you fail, nothing happens."""
                    return [
                        arkham.GameplayAction_Multiple \
                            ([arkham.GameplayAction_Exhaust (item),
                              arkham.GameplayAction_SpendMovementPoints \
                                  (movement_points),
                              arkham.GameplayAction_CauseHarm \
                                  (game, owner, item, harm) if harm else None,
                              arkham.GameplayAction_Conditional \
                                  (game, owner, item, check,
                                   arkham.GameplayAction_Multiple \
                                       ([success_action_ctor \
                                             (game, owner, item),
                                         arkham.GameplayAction_Discard \
                                             (item)]),
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
        (fun.any, fun.any, fun.any, arkham.match_proto (Derringer18),
         fun.val == arkham.checkbase_combat)
    def do (game, investigator, subject, item, skill_name):
        return arkham.Bonus (2, arkham.family_physical)


    class Axe (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Axe", 3, 1)

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Axe),
         fun.val == arkham.checkbase_combat)
    def do (game, investigator, subject, item, skill_name):
        # Do we have one extra hand capable of holding this axe?
        if investigator.find_wield (game, item, 1):
            return arkham.Bonus (3, arkham.family_physical)
        else:
            return arkham.Bonus (2, arkham.family_physical)


    class Bullwhip (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Bullwhip", 2, 1)

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Bullwhip),
         fun.val == arkham.checkbase_combat)
    def do (game, investigator, subject, item, skill_name):
        return arkham.Bonus (1, arkham.family_physical)

    @arkham.check_correction_actions_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Bullwhip),
         fun.val == arkham.checkbase_combat, fun.any)
    def do (game, investigator, subject, item, skill_name, roll):
        if not item.exhausted ():
            return [arkham.GameplayAction_Multiple \
                        ([arkham.GameplayAction_Exhaust (item),
                          arkham.GameplayAction_Reroll \
                              (subject, skill_name, roll)])]
        else:
            return []


    class Cross (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Cross", 3, 1)

    @arkham.bonus_hook.match \
        (fun.any, fun.any, arkham.match_flag ("undead"),
         arkham.match_proto (Cross),
         fun.val == arkham.checkbase_combat)
    def do (game, investigator, subject, item, skill_name):
        return arkham.Bonus (3, arkham.family_magical)

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Cross),
         fun.val == arkham.checkbase_horror)
    def do (game, investigator, subject, item, skill_name):
        return arkham.Bonus (1, arkham.family_magical)


    class Food (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Food", 1, 0)

    @arkham.damage_correction_actions_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Food),
         lambda damage: arkham.health_stamina in damage.aspects ())
    def do (game, investigator, subject, item, damage):
        return [arkham.GameplayAction_Multiple \
                    ([arkham.GameplayAction_Discard (item),
                      arkham.GameplayAction_ReduceDamage \
                          (damage, arkham.health_stamina, 1)])]


    class LuckyCigaretteCase (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ \
                (self, "Lucky Cigarette Case", 1, 0)

    @arkham.check_correction_actions_hook.match \
        (fun.any, fun.any, fun.any,
         arkham.match_proto (LuckyCigaretteCase), fun.any, fun.any)
    def do (game, investigator, subject, item, skill_name, roll):
        return [arkham.GameplayAction_Multiple \
                    ([arkham.GameplayAction_Discard (item),
                      arkham.GameplayAction_Reroll \
                          (subject, skill_name, roll)])]


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


    class ResearchMaterials (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Research Materials", 1, 0)

    @arkham.spend_clue_token_actions_hook.match \
        (fun.any, fun.any, fun.any,
         arkham.match_proto (ResearchMaterials), fun.any)
    def do (game, investigator, subject, item, skill_name):
        return [arkham.GameplayAction_Discard (item)]


    class Shotgun (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Shotgun", 6, 2)

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Shotgun),
         fun.val == arkham.checkbase_combat)
    def do (game, investigator, subject, item, skill_name):
        return arkham.Bonus (4, arkham.family_physical)

    @arkham.dice_roll_successes_bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Shotgun),
         fun.val == arkham.checkbase_combat,
         fun.val == 6)
    def do (game, investigator, subject, item, skill_name, dice):
        return 1


    class Whiskey (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Whiskey", 1, 0)

    @arkham.damage_correction_actions_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Whiskey),
         lambda damage: arkham.health_sanity in damage.aspects ())
    def do (game, investigator, subject, item, damage):
        return [arkham.GameplayAction_Multiple \
                    ([arkham.GameplayAction_Discard (item),
                      arkham.GameplayAction_ReduceDamage \
                          (damage, arkham.health_sanity, 1)])]


    for count, item_proto in [
            (1, Derringer18 ()),
            (1, plain_item (".38 Revolver", 4, 1,
                            {arkham.checkbase_combat:
                                 arkham.Bonus (3, arkham.family_physical)})),
            (1, plain_item (".45 Automatic", 5, 1,
                            {arkham.checkbase_combat:
                                 arkham.Bonus (4, arkham.family_physical)})),
            (1, complex (Tome, "Ancient Tome", 4, 2, None,
                         arkham.SkillCheck (arkham.checkbase_lore, -1),
                         # xxx should be spell deck
                         lambda game, owner, item: \
                             arkham.GameplayAction_DrawItem \
                                (module.m_common_deck))),
            (1, Axe ()),
            (1, Bullwhip ()),
            (1, plain_item ("Cavalry Saber", 3, 1,
                            {arkham.checkbase_combat:
                                 arkham.Bonus (2, arkham.family_physical)})),
            (1, Cross ()),
            (1, plain_item ("Dark Cloak", 2, 0,
                            {arkham.checkbase_evade:
                                 arkham.Bonus (1, arkham.family_indifferent)})),
            (1, plain_item ("Dynamite", 4, 2,
                            {arkham.checkbase_combat:
                                 arkham.Bonus (8, arkham.family_physical)},
                            after_use = lambda game, owner, item: \
                                arkham.GameplayAction_Discard (item))),
            (1, Food ()),
            (1, plain_item ("Knife", 2, 1,
                            {arkham.checkbase_combat:
                                 arkham.Bonus (1, arkham.family_physical)})),
            (1, plain_item ("Lantern", 3, 0,
                            {arkham.checkbase_luck:
                                 arkham.Bonus (1, arkham.family_indifferent)})),
            (1, LuckyCigaretteCase ()),
            (1, MapOfArkham ()),
            (1, Motorcycle ()),
            (1, complex (Tome, "Old Journal", 1, 1, None,
                         arkham.SkillCheck (arkham.checkbase_lore, -1),
                         lambda game, owner, item: \
                             arkham.GameplayAction_GainClues (3))),
            (1, ResearchMaterials ()),
            (1, plain_item ("Rifle", 6, 2,
                            {arkham.checkbase_combat:
                                 arkham.Bonus (5, arkham.family_physical)})),
            (1, Shotgun ()),
            (1, plain_item ("Tommy Gun", 7, 2,
                            {arkham.checkbase_combat:
                                 arkham.Bonus (6, arkham.family_physical)})),
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
                        ([arkham.GameplayAction_SpendMovementPoints \
                              (movement_points),
                          arkham.GameplayAction_Discard (item),
                          arkham.GameplayAction_Repeat \
                              (2, arkham.GameplayAction_Conditional \
                                   (game, owner, item,
                                    arkham.SkillCheck \
                                        (arkham.CheckBase_Fixed (1), 0),
                                    # xxx should be spell deck
                                    arkham.GameplayAction_DrawItem \
                                        (module.m_common_deck),
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

        @classmethod
        def bonus_action (cls, game, owner, monster, item):
            """Lose 2 Stamina and discard Blue Watcher of the Pyramid
            to automatically succeed at a Combat check or a Fight
            check or Lore check made to close a gate."""
            return [
                arkham.GameplayAction_Multiple \
                    ([arkham.GameplayAction_CauseHarm \
                          (game, owner, item, arkham.HarmSanity (2)),
                      arkham.GameplayAction_Discard (item),
                      arkham.GameplayAction_SucceedCombatCheck ()
                      ])
                ]

        def combat_turn (self, combat, owner, monster, item):
            return BlueWatcherOfThePyramid.bonus_action \
                (combat.game, owner, monster, item)

    @arkham.check_correction_actions_hook.match \
        (fun.any, fun.any, fun.any,
         arkham.match_proto (BlueWatcherOfThePyramid),
         fun.val == arkham.checkbase_combat, fun.any)
    def do (game, investigator, subject, item, skill_name, roll):
        return BlueWatcherOfThePyramid.bonus_action \
            (game, investigator, subject, item)


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
                          arkham.GameplayAction_SpendMovementPoints \
                              (movement_points),
                          arkham.GameplayAction_Conditional \
                              (game, owner, item,
                               arkham.SkillCheck (arkham.checkbase_lore, -1),
                               arkham.GameplayAction_Multiple \
                                   ([# xxx should be spell deck
                                     arkham.GameplayAction_DrawItem \
                                         (module.m_common_deck),
                                     arkham.GameplayAction_CauseHarm \
                                         (game, owner, item,
                                          arkham.HarmSanity (1)),
                                     arkham.GameplayAction_MarkItem \
                                         (item, 2,
                                          arkham.GameplayAction_Discard \
                                              (item))]))])
                    ]
            else:
                return []


    class xxxDragonsEye (arkham.InvestigatorItem):
        """Any phase: Exhaust and lose 1 Sanity after drawing a gate
        or location card to draw a new card in its place"""
        pass


    class xxxElderSign (arkham.InvestigatorItem):
        """Any Phase: When sealing a gate, lose 1 Stamina and 1 Sanity
        and return this card to the box. You do not need to make a
        skill check or spend any Clue tokens to seal the gate. In
        addition, remove one doom token from the Ancient One's doom
        track."""
        pass


    class EnchantedJewelry (arkham.InvestigatorItem):
        """ Any Phase: Put 1 Stamina token from the bank on Enchanted
        Jewelry to avoid losing 1 Stamina. If there are 3 Stamina
        tokens on it, discard Enchanted Jewelry.  Price: $3"""
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Enchanted Jewelry", 3, 0)

    @arkham.damage_correction_actions_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (EnchantedJewelry),
         lambda damage: arkham.health_stamina in damage.aspects ())
    def do (game, investigator, subject, item, damage):
        return [arkham.GameplayAction_Multiple \
                    ([arkham.GameplayAction_ReduceDamage \
                          (damage, arkham.health_stamina, 1),
                      arkham.GameplayAction_MarkItem \
                          (item, 3, arkham.GameplayAction_Discard (item))])]


    # xxx this cannot be used against ancient one
    class FluteOfTheOuterGods (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ \
                (self, "Flute of the Outer Gods", 8, 0)

        def combat_turn (self, combat, owner, monster, item):
            """Any Phase: Lose 3 Sanity and 3 Stamina and discard
            Flute of the Outer Gods before making a Combat check to
            defeat all monsters in your current area. This does not
            affect Ancient Ones."""

            class GameplayAction_DefeatAllOnLocation \
                    (arkham.LocationBoundGameplayAction):
                def __init__ (self):
                    arkham.LocationBoundGameplayAction.__init__ \
                        (self, owner.location (),
                         "defeat all monsters in location")

                def perform (self, game, investigator):
                    for monster in game.monsters_at (owner.location ()):
                        arkham.combat_won_hook (combat, owner, monster)

            return [
                arkham.GameplayAction_Multiple \
                    ([arkham.GameplayAction_CauseHarm \
                          (game, owner, item,
                           arkham.HarmDamage (
                                arkham.Damage (
                                    {arkham.health_sanity: 3,
                                     arkham.health_stamina: 3}))),
                      GameplayAction_DefeatAllOnLocation (),
                      arkham.GameplayAction_Discard (item)])
                ]


    class xxxGateBox (arkham.InvestigatorItem):
        """Any Phase: When you return to Arkham from an Other World,
        you can return to any location with an open gate, not just
        those leading to the Other World you were in."""
        pass


    class HealingStone (arkham.InvestigatorItem):
        """Upkeep: You may gain 1 Stamina or 1 Sanity.
        xxx: Discard Healing Stone if the Ancient One awakens."""
        def __init__ (self):
            arkham.InvestigatorItem.__init__ \
                (self, "Healing Stone", 8, 0)

        def upkeep (self, game, owner, item):
            # Only allow one action per upkeep.  We can't exhaust,
            # since upkeep is where the card should be refreshed.
            item_turn = getattr (item, "turn", -1)
            cur_turn = game.turn_number ()
            item.turn = cur_turn
            if cur_turn <= item_turn:
                return []

            aspects = owner.health_aspects ()
            ret = []
            for aspect in (arkham.health_sanity, arkham.health_stamina):
                if aspect in aspects:
                    health = owner.health (aspect)
                    if health.cur () < health.max ():
                        ret.append \
                            (arkham.GameplayAction_Heal \
                                 (arkham.Heal ({aspect: 1})))
            return ret


    class HolyWater (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Holy Water", 4, 2)
            """Bonus: +6 Combat check (Discard after use)"""

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (HolyWater),
         fun.val == arkham.checkbase_combat)
    def do (game, investigator, subject, item, skill_name):
        return 6

    @arkham.item_after_use_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (HolyWater),
         fun.val == arkham.checkbase_combat)
    def do (game, investigator, subject, item, skill_name):
        investigator.discard_item (item)


    class ObsidianStatue (arkham.InvestigatorItem):
        """Any Phase: Discard Obsidian Statue to cancel all Stamina or
        Sanity loss being dealt to you from one source. """
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Obsidian Statue", 4, 0)

    @arkham.damage_correction_actions_hook.match \
        (fun.any, fun.any, fun.any,
         arkham.match_proto (ObsidianStatue), fun.any)
    def do (game, investigator, subject, item, damage):
        has_stamina = arkham.health_stamina in damage.aspects ()
        has_sanity = arkham.health_sanity in damage.aspects ()
        if has_stamina or has_sanity:
            mul = [arkham.GameplayAction_Discard (item)]
            if has_stamina:
                mul.append (arkham.GameplayAction_CancelDamage \
                              (damage, arkham.health_stamina))
            if has_sanity:
                mul.append (arkham.GameplayAction_CancelDamage \
                              (damage, arkham.health_stamina))
            return [arkham.GameplayAction_Multiple (mul)]
        else:
            return []


    class RubyOfRlyeh (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Ruby of R'lyeh", 8, 0)

        def movement_points_bonus (self, game, owner, item):
            return 3


    class SilverKey (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Silver Key", 4, 0)

    @arkham.perform_check_actions_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (SilverKey),
         fun.val == arkham.checkbase_evade, fun.any, fun.any)
    def do (game, investigator, subject, item,
            check_base, modifier, difficulty):
        """Any Phase: Put 1 Stamina token from the bank on Silver
        Key before making an Evade check to automatically pass
        it. Discard Silver Key after using it if there are 3
        Stamina tokens on it. """

        return [arkham.GameplayAction_Multiple \
                ([arkham.GameplayAction_SucceedCheck (check_base),
                  arkham.GameplayAction_MarkItem \
                      (item, 3, arkham.GameplayAction_Discard (item))])]


    class WardingStatue (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Warding Statue", 6, 0)

    @arkham.cause_combat_harm_actions_hook.match \
        (fun.any, fun.any, fun.any,
         arkham.match_proto (WardingStatue),
         fun.and_ (fun.matchclass (arkham.HarmDamage),
                   lambda harm: \
                       arkham.health_stamina in harm.damage ().aspects ()))
    def do (combat, investigator, monster, item, harm):
        """Any Phase: Discard Warding Statue after failing a Combat
        check to reduce the monster's combat damage to 0 Stamina.
        xxx This can also be used to cancel an Ancient One's entire
        attack for 1 turn."""
        return [arkham.GameplayAction_Multiple \
                    ([arkham.GameplayAction_CancelDamage \
                          (harm.damage (), arkham.health_stamina),
                      arkham.GameplayAction_Discard (item)])]

    for count, item_proto in [
            (1, complex (arkham.InvestigatorItem, "Alien Statue", 5,
                         2, arkham.HarmSanity (1),
                         arkham.SkillCheck (arkham.CheckBase_Fixed (1), 0),
                         lambda game, owner, item: \
                             (arkham.GameplayAction_Select
                                  ([arkham.GameplayAction_GainClues (3),
                                    # xxx should be spell deck
                                    arkham.GameplayAction_DrawItem \
                                        (module.m_common_deck)])),
                         lambda game, owner, item: \
                             arkham.GameplayAction_CauseHarm \
                                 (game, owner, item, arkham.HarmSanity (2)))),
            (1, AncientTablet ()),
            (1, BlueWatcherOfThePyramid ()),
            (1, BookOfDzyan ()),
            (1, complex (arkham.InvestigatorItem, "Cabala of Saboth", 5,
                         2, None,
                         arkham.SkillCheck (arkham.checkbase_lore, -2),
                         # xxx should be SKILL deck
                         lambda game, owner, item: \
                             arkham.GameplayAction_DrawItem \
                                (module.m_common_deck))),
            (1, complex (arkham.InvestigatorItem, "Cultes des Goules", 3,
                         2, None,
                         arkham.SkillCheck (arkham.checkbase_lore, -2),
                         lambda game, owner, item: \
                             arkham.GameplayAction_Multiple ([
                                # xxx should be spell deck
                                arkham.GameplayAction_DrawItem \
                                    (module.m_common_deck),
                                arkham.GameplayAction_GainClues (1),
                                arkham.GameplayAction_CauseHarm \
                                    (game, owner, item,
                                     arkham.HarmSanity (2))]))),
            (1, plain_item ("Enchanted Blade", 6, 1,
                            {arkham.checkbase_combat:
                                 arkham.Bonus (4, arkham.family_magical)})),
            (1, EnchantedJewelry ()),
            (1, plain_item ("Enchanted Knife", 5, 1,
                            {arkham.checkbase_combat:
                                 arkham.Bonus (3, arkham.family_magical)})),
            (1, FluteOfTheOuterGods ()),
            (1, HealingStone ()),
            (1, HolyWater ()),
            (1, plain_item ("Lamp of Alhazred", 7, 2,
                            {arkham.checkbase_combat:
                                 arkham.Bonus (5, arkham.family_magical)})),
            (1, complex (arkham.InvestigatorItem, "Nameless Cults", 3,
                         1, None,
                         arkham.SkillCheck (arkham.checkbase_lore, -1),
                         lambda game, owner, item: \
                             arkham.GameplayAction_Multiple ([
                                # xxx should be spell deck
                                arkham.GameplayAction_DrawItem \
                                    (module.m_common_deck),
                                arkham.GameplayAction_CauseHarm \
                                    (game, owner, item,
                                     arkham.HarmSanity (1))]))),
            (1, complex (arkham.InvestigatorItem, "Necronomicon", 6,
                         2, None,
                         arkham.SkillCheck (arkham.checkbase_lore, -2),
                         lambda game, owner, item: \
                             arkham.GameplayAction_Multiple ([
                                # xxx should be spell deck
                                arkham.GameplayAction_DrawItem \
                                    (module.m_common_deck),
                                arkham.GameplayAction_CauseHarm \
                                    (game, owner, item,
                                     arkham.HarmSanity (2))]))),
            (1, ObsidianStatue ()),
            (1, plain_item ("Pallid Mask", 4, 0,
                            {arkham.checkbase_evade:
                                 arkham.Bonus (2, arkham.family_indifferent)})),
            (1, plain_item ("Powder of Ibn-Ghazi", 6, 2,
                            {arkham.checkbase_combat:
                                 arkham.Bonus (9, arkham.family_magical)},
                            after_use = lambda game, owner, item: \
                                arkham.GameplayAction_Multiple ([
                                    arkham.GameplayAction_CauseHarm \
                                        (game, owner, item,
                                         arkham.HarmSanity (1)),
                                    arkham.GameplayAction_Discard (item)]))),
            (1, RubyOfRlyeh ()),
            (1, SilverKey ()),
            (1, plain_item ("Sword of Glory", 8, 2,
                            {arkham.checkbase_combat:
                                 arkham.Bonus (6, arkham.family_magical)})),
            (1, complex (arkham.InvestigatorItem, "The King in Yellow", 2,
                         2, None,
                         arkham.SkillCheck (arkham.checkbase_lore, -2),
                         lambda game, owner, item: \
                             arkham.GameplayAction_Multiple ([
                                arkham.GameplayAction_GainClues (4),
                                arkham.GameplayAction_CauseHarm \
                                    (game, owner, item,
                                     arkham.HarmSanity (1))]))),
            (1, WardingStatue ()),
        ]:
        module.m_unique_deck.register (item_proto, count)

    # -------------------------------------------------------------------------

    class BindMonster (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ \
                (self, "Bind Monster", 0, 0)

        def combat_turn (self, combat, owner, monster, item):
            """Cast and Discard this spell to pass one Combat
            check. You must roll successes equal to the monster's
            toughness to cast this spell.
            xxx This spell doesn't work on Ancient Ones."""
            cc = monster.proto ().combat_check ()
            if fun.matchclass (arkham.SkillCheck) (cc):
                d = cc.difficulty ()
                return [
                    arkham.GameplayAction_Multiple \
                        ([arkham.GameplayAction_CauseHarm \
                              (combat.game, owner, item, arkham.HarmSanity (2)),
                          arkham.GameplayAction_Conditional \
                              (combat.game, owner, item,
                               arkham.SkillCheck (arkham.checkbase_lore, +4, d),
                               arkham.GameplayAction_Multiple \
                                   ([arkham.GameplayAction_Discard (item),
                                     arkham.GameplayAction_SucceedCombatCheck ()]))
                          ])]


    class DreadCurseOfAzathoth (module.mod_spell.SpellItem):
        class Instance (module.mod_spell.SpellInst):
            def __init__ (self, parent):
                module.mod_spell.SpellInst.__init__ \
                    (self, parent.name (), 0, 2)

        def __init__ (self):
            module.mod_spell.SpellItem.__init__ \
                (self, "Dread Curse of Azathoth", 0, 0)

        def combat_turn (self, combat, owner, monster, item):
            if item.exhausted ():
                return []

            inst = arkham.Item (DreadCurseOfAzathoth.Instance (self))
            if not owner.find_wield (combat.game, inst, inst.hands ()):
                return []

            return [arkham.GameplayAction_Multiple \
                        ([arkham.GameplayAction_Exhaust (item),
                          arkham.GameplayAction_CauseHarm \
                              (combat.game, owner, item,
                               arkham.HarmSanity (2)),
                          arkham.GameplayAction_Conditional \
                              (combat.game, owner, item,
                               arkham.SkillCheck (arkham.checkbase_lore, -2),
                               arkham.GameplayAction_Multiple \
                                   ([arkham.GameplayAction_WieldItem \
                                         (inst, True),
                                     arkham.GameplayAction_WhenCombatEnds \
                                         (combat,
                                          arkham.GameplayAction_Discard (inst))
                                     ]))])]

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any,
         arkham.match_proto (DreadCurseOfAzathoth.Instance),
         fun.val == arkham.checkbase_combat)
    def do (game, investigator, subject, item, check_base):
        return arkham.Bonus (9, arkham.family_magical)


    for count, item_proto in [
            (1, BindMonster ()),
            (1, DreadCurseOfAzathoth ()),
        ]:
        module.m_spell_deck.register (item_proto, count)
