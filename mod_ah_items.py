import arkham
import checks
import fun
from itsup import *

def build (game, module):
    def plain_item (name, price, hands, bonuses, **attributes):
        after_use = attributes.pop ("after_use", None)
        extra_classes = tuple (attributes.pop ("extra_classes", ()))

        class PlainItem (arkham.InvestigatorItem):
            def __init__ (self):
                arkham.InvestigatorItem.__init__ (self, name, price,
                                                  hands, **attributes)
        PlainItem.__bases__ = PlainItem.__bases__ + extra_classes

        for check_base, bonus in bonuses.iteritems ():
            @game.bonus_hook.match \
                (fun.any, fun.any, fun.any,
                 arkham.match_proto (PlainItem), fun.val == check_base)
            def do (game, investigator, subject, item, check_base):
                return bonus

            if after_use:
                @game.item_after_use_hook.match \
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

    class Axe (arkham.InvestigatorItem, arkham.Weapon):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Axe", 3, 1)

    @game.bonus_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (Axe),
         fun.val == arkham.checkbase_combat)
    def do (game, investigator, subject, item, checkbase):
        # Do we have one extra hand capable of holding this axe?
        if investigator.find_wield (game, item, 1):
            return arkham.Bonus (3, arkham.family_physical)
        else:
            return arkham.Bonus (2, arkham.family_physical)


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

    @game.spend_clue_token_actions_hook.match \
        (fun.any, fun.any, fun.any,
         arkham.match_proto (ResearchMaterials), fun.any)
    def do (game, investigator, subject, item, checkbase):
        return [arkham.GameplayAction_Discard (item)]

    for count, item_proto in [
            (2, Axe ()),
            (2, MapOfArkham ()),
            (2, Motorcycle ()),
            (2, ResearchMaterials ()),
        ]:
        module.m_common_deck.register (item_proto, count)

    (itsup_init(game)

     # -------------------------------------------------------------------------
     .deck("Common Items")

     # xxx .18 Derringer cannot be lost or stolen unless you choose to
     # allow it.
     .item(".18 Derringer", 2, weapon)
     .hand(1) .usd(3)
     .bonus(combat, physical(2))

     .item(".38 Revolver", 2, weapon)
     .hand(1) .usd(4)
     .bonus(combat, physical(3))

     .item(2, ".45 Automatic", weapon)
     .usd(5) .hand(1)
     .bonus(combat, physical(4))

     .item("Ancient Tome", 2, tome)
     .usd(4)
     .movement(exhaust,
               lose(movement_points(2)),
               check(lore(-1),
                     [discard, draw("Spell Deck")]))

     .item("Bullwhip", 2, weapon)
     .hand(1) .usd(2)
     .bonus(combat, physical(1))
     .check_correction(combat, exhaust, reroll)

     .item("Cavalry Saber", 2, weapon)
     .hand(1) .usd(3)
     .bonus(combat, magical(2))

     .item("Cross", 2, weapon) # xxx is it a weapon?
     .hand(1) .usd(3)
     .bonus(combat, undead, magical(3))
     .bonus(horror, magical(1))

     .item("Dark Cloak", 2)
     .usd(2)
     .bonus(evade, indifferent(1))

     .item("Dynamite", 2, weapon)
     .hands(2) .usd(4)
     .bonus(combat, physical(8), discard)

     .item("Food", 2)
     .usd(1)
     .damage_correction(discard, reduce(stamina(1)))

     .item("Knife", 2, weapon)
     .hand(1) .usd(2)
     .bonus(combat, physical(1))

     .item("Lantern", 2)
     .usd(3)
     .bonus(luck, indifferent(1))

     .item("Lucky Cigarette Case", 2, weapon)
     .usd(1)
     .check_correction(discard, reroll)

     .item("Old Journal", 2, tome)
     .usd(1)
     .movement(exhaust,
               lose(movement_points(1)),
               check(lore(-1),
                     [discard, gain(clues(3))]))

     .item("Rifle", 2, weapon)
     .hands(2) .usd(6)
     .bonus(combat, physical(5))

     .item("Shotgun", 2, weapon)
     .hands(2) .usd(6)
     .bonus(combat, physical(4))
     .dice_roll_successes_bonus(r6, 1)

     .item("Tommy Gun", 2, weapon)
     .hands(2) .usd(7)
     .bonus(combat, physical(6))

     .item("Whiskey", 2)
     .usd(1)
     .damage_correction(discard, reduce(sanity(1)))

     # -------------------------------------------------------------------------
     .deck("Unique Items")

     .item("Alien Statue", 1)
     .usd(5)
     .movement(exhaust,
               lose(movement_points(2), sanity(1)),
               check(fixed(1),
                     [discard, select(gain(clues(3)),
                                      draw("Spell Deck"))],
                     [lose(stamina(2))]))

     .item("Ancient Tablet", 1)
     .usd(8)
     .movement(lose(movement_points(3)), discard,
               repeat(2, check(fixed(1),
                               [draw("Spell Deck")],
                               [gain(clues(2))])))

     .item("Blue Watcher of the Pyramid", 1)
     .usd(4)
     .check_correction(lose(sanity(2)), discard, pass_check)
     .combat_turn(likewise)

     .item("Book of Dzyan", 1)
     .usd(3)
     .movement(exhaust, lose(movement_points(2)),
               check(lore(-1),
                     [draw("Spell Deck"), lose(sanity(1)),
                      mark(2, discard)]))

     .item("Enchanted Jewelry", 1)
     .damage_correction(reduce(stamina(1)), mark(3, discard))

     .item("Healing Stone", 1)
     .upkeep(exhaust, if_hurt(stamina), gain(stamina(1)))
     .upkeep(exhaust, if_hurt(sanity), gain(sanity(1)))

     .item("Holy Water", 4, weapon)
     .hands(2) .usd(4)
     .bonus(combat, magical(6), discard)

     .item("Obsidian Statue", 1)
     .usd(4)
     .damage_correction(cancel(stamina), discard)
     .damage_correction(cancel(sanity), discard)

     .commit())

    # -------------------------------------------------------------------------

    class xxxDragonsEye (arkham.InvestigatorItem):
        """Any phase: Exhaust and lose 1 Sanity after drawing a gate
        or location card to draw a new card in its place
        count: 1"""
        pass


    class xxxElderSign (arkham.InvestigatorItem):
        """Any Phase: When sealing a gate, lose 1 Stamina and 1 Sanity
        and return this card to the box. You do not need to make a
        skill check or spend any Clue tokens to seal the gate. In
        addition, remove one doom token from the Ancient One's doom
        track.
        count: 4
        """
        pass


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
                        game.combat_won_hook (combat, owner, monster)

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
        """count:1"""
        pass

    class RubyOfRlyeh (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Ruby of R'lyeh", 8, 0)

        def movement_points_bonus (self, game, owner, item):
            # xxx why is it not done the same was as for Map and Motorcycle?
            return 3


    class SilverKey (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Silver Key", 4, 0)

    @game.perform_check_actions_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (SilverKey),
         fun.val == arkham.checkbase_evade, fun.any, fun.any)
    def do (game, investigator, subject, item,
            check_base, modifier, difficulty):
        """Any Phase: Put 1 Stamina token from the bank on Silver
        Key before making an Evade check to automatically pass
        it. Discard Silver Key after using it if there are 3
        Stamina tokens on it. """

        return [arkham.GameplayAction_Multiple \
                ([arkham.GameplayAction_PassCheck (),
                  arkham.GameplayAction_MarkItem \
                      (item, 3, arkham.GameplayAction_Discard (item))])]


    class WardingStatue (arkham.InvestigatorItem):
        def __init__ (self):
            arkham.InvestigatorItem.__init__ (self, "Warding Statue", 6, 0)

    @game.cause_combat_harm_actions_hook.match \
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
            (2, complex (arkham.InvestigatorItem, "Cabala of Saboth", 5,
                         2, None,
                         arkham.SkillCheck (arkham.checkbase_lore, -2),
                         # xxx should be SKILL deck
                         lambda game, owner, item: \
                             arkham.GameplayAction_DrawItem \
                                (module.m_common_deck))),
            (2, complex (arkham.InvestigatorItem, "Cultes des Goules", 3,
                         2, None,
                         arkham.SkillCheck (arkham.checkbase_lore, -2),
                         lambda game, owner, item: \
                             arkham.GameplayAction_Multiple ([
                                arkham.GameplayAction_DrawItem \
                                    (module.m_spell_deck),
                                arkham.GameplayAction_GainClues (1),
                                arkham.GameplayAction_CauseHarm \
                                    (game, owner, item,
                                     arkham.HarmSanity (2))]))),
            (2, plain_item ("Enchanted Blade", 6, 1,
                            {arkham.checkbase_combat:
                                 arkham.Bonus (4, arkham.family_magical)},
                            extra_classes = [arkham.Weapon])),
            (2, plain_item ("Enchanted Knife", 5, 1,
                            {arkham.checkbase_combat:
                                 arkham.Bonus (3, arkham.family_magical)},
                            extra_classes = [arkham.Weapon])),
            (1, FluteOfTheOuterGods ()),
            (1, plain_item ("Lamp of Alhazred", 7, 2,
                            {arkham.checkbase_combat:
                                 arkham.Bonus (5, arkham.family_magical)},
                            extra_classes = [arkham.Weapon])),
            (2, complex (arkham.InvestigatorItem, "Nameless Cults", 3,
                         1, None,
                         arkham.SkillCheck (arkham.checkbase_lore, -1),
                         lambda game, owner, item: \
                             arkham.GameplayAction_Multiple ([
                                arkham.GameplayAction_DrawItem \
                                    (module.m_spell_deck),
                                arkham.GameplayAction_CauseHarm \
                                    (game, owner, item,
                                     arkham.HarmSanity (1))]))),
            (1, complex (arkham.InvestigatorItem, "Necronomicon", 6,
                         2, None,
                         arkham.SkillCheck (arkham.checkbase_lore, -2),
                         lambda game, owner, item: \
                             arkham.GameplayAction_Multiple ([
                                arkham.GameplayAction_DrawItem \
                                    (module.m_spell_deck),
                                arkham.GameplayAction_CauseHarm \
                                    (game, owner, item,
                                     arkham.HarmSanity (2))]))),
            (1, plain_item ("Pallid Mask", 4, 0,
                            {arkham.checkbase_evade:
                                 arkham.Bonus (2, arkham.family_indifferent)})),
            (2, plain_item ("Powder of Ibn-Ghazi", 6, 2,
                            {arkham.checkbase_combat:
                                 arkham.Bonus (9, arkham.family_magical)},
                            after_use = lambda game, owner, item: \
                                arkham.GameplayAction_Multiple ([
                                    arkham.GameplayAction_CauseHarm \
                                        (game, owner, item,
                                         arkham.HarmSanity (1)),
                                    arkham.GameplayAction_Discard (item)]),
                            extra_classes = [arkham.Weapon])),
            (1, RubyOfRlyeh ()),
            (1, SilverKey ()),
            (1, plain_item ("Sword of Glory", 8, 2,
                            {arkham.checkbase_combat:
                                 arkham.Bonus (6, arkham.family_magical)},
                            extra_classes = [arkham.Weapon])),
            (2, complex (arkham.InvestigatorItem, "The King in Yellow", 2,
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
            cc = monster.combat_check ()
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
                                     arkham.GameplayAction_PassCheck ()]))
                          ])]


    def simple_bonus_spell (name, lore_mod, sanity_cost, hands, bonuses,
                            action_ctor = lambda combat, setup, teardown: \
                                arkham.GameplayAction_ForCombat \
                                        (combat, setup, teardown)):
        class SimpleBonusSpell (module.mod_spell.SpellItem):
            class Instance (module.mod_spell.SpellInst):
                def __init__ (self, parent):
                    module.mod_spell.SpellInst.__init__ \
                        (self, parent.name (), 0, hands)

            def __init__ (self):
                module.mod_spell.SpellItem.__init__ \
                    (self, name, 0, 0)

            def combat_turn (self, combat, owner, monster, item):
                if item.exhausted ():
                    return []

                inst = arkham.Item (SimpleBonusSpell.Instance (self))
                if not owner.find_wield (combat.game, inst, inst.hands ()):
                    return []

                return [arkham.GameplayAction_Multiple \
                            ([arkham.GameplayAction_Exhaust (item),
                              arkham.GameplayAction_CauseHarm \
                                  (combat.game, owner, item,
                                   arkham.HarmSanity (sanity_cost)),
                              arkham.GameplayAction_Conditional \
                                  (combat.game, owner, item,
                                   arkham.SkillCheck (arkham.checkbase_lore,
                                                      lore_mod),
                                   action_ctor \
                                       (combat,
                                        arkham.GameplayAction_WieldItem \
                                            (inst, True),
                                        arkham.GameplayAction_Discard (inst)))])]

        for checkbase, bonus in bonuses.iteritems ():
            if not callable (checkbase):
                checkbase = fun.val == checkbase
            @game.bonus_hook.match \
                (fun.any, fun.any, fun.any,
                 arkham.match_proto (SimpleBonusSpell.Instance),
                 checkbase)
            def do (game, investigator, subject, item, check_base):
                return bonus

        return SimpleBonusSpell ()


    class EnchantWeapon (module.mod_spell.SpellItem):
        def __init__ (self):
            module.mod_spell.SpellItem.__init__ \
                (self, "Enchant Weapon", 0, 0)

        def combat_turn (self, combat, owner, monster, item):
            if item.exhausted ():
                return []

            match_weapon = arkham.match_proto (arkham.Weapon)
            if not any (match_weapon (item) for item in owner.wields_items ()):
                return []

            return \
                [arkham.GameplayAction_Multiple \
                     ([arkham.GameplayAction_Exhaust (item),
                       arkham.GameplayAction_CauseHarm \
                           (combat.game, owner, item,
                            arkham.HarmSanity (1)),
                       arkham.GameplayAction_Conditional \
                           (combat.game, owner, item,
                            arkham.SkillCheck (arkham.checkbase_lore, 0),
                            arkham.GameplayAction_WithSelectedItem \
                                (match_weapon, "weapon",
                                 lambda item: \
                                     arkham.GameplayAction_ForCombat \
                                        (combat,
                                         arkham.GameplayAction_Flag \
                                             (item, "enchanted"),
                                         arkham.GameplayAction_Unflag \
                                             (item, "enchanted"))))
                       ])]

    @game.bonus_hook.match \
        (fun.any, fun.any, fun.any,
         arkham.match_flag ("enchanted"),
         fun.val == arkham.checkbase_combat,
         priority = 1)
    def do (game, investigator, subject, item, check_base):
        original_bonus = next ()
        original_bonus.set_family (arkham.family_magical)
        return original_bonus


    class xxxFindGate (module.mod_spell.SpellItem):
        """Movement Phase: Cast and exhaust to immediately return to
        Arkham from an Other World.  count:4"""
        pass


    class FleshWard (module.mod_spell.SpellItem):
        """Any Phase: Cast and exhaust to ignore all Stamina loss
        being dealt to you from one source. Discard this spell if the
        Ancient One awakens."""
        def __init__ (self):
            module.mod_spell.SpellItem.__init__ (self, "Flesh Ward", 0, 0)

    @game.damage_correction_actions_hook.match \
        (fun.any, fun.any, fun.any,
         arkham.match_proto (FleshWard), fun.any)
    def do (game, owner, subject, item, damage):
        if item.exhausted ():
            return []

        if arkham.health_stamina not in damage.aspects ():
            return []

        return [arkham.GameplayAction_Multiple \
                    ([arkham.GameplayAction_Exhaust (item),
                       arkham.GameplayAction_CauseHarm \
                           (game, owner, item,
                            arkham.HarmSanity (1)),
                       arkham.GameplayAction_Conditional \
                           (game, owner, item,
                            arkham.SkillCheck (arkham.checkbase_lore, -2),
                            arkham.GameplayAction_CancelDamage \
                                (damage, arkham.health_stamina))])]

    # xxxx Spells in general do "exhaust, cast" instead of "cast,
    # exhaust".  The program is buggy.

    class Heal (module.mod_spell.SpellItem):
        """Upkeep Phase: You may cast and exhaust. You or another
        investigator in your area gains Stamina equal to the successes
        you rolled on your Spell check. This Stamina cannot be split
        between multiple investigators."""
        def __init__ (self):
            module.mod_spell.SpellItem.__init__ (self, "Heal", 0, 0)

        def upkeep_2 (self, game, owner, item):
            if item.exhausted ():
                return []

            def qualifies (investigator):
                if investigator.location () != owner.location ():
                    return False
                h = investigator.health (arkham.health_stamina)
                return h.cur () < h.max ()

            if not any (qualifies (investigator)
                        for investigator in game.investigators ()):
                return []

            def success_action (successes):
                return arkham.GameplayAction_WithSelectedInvestigator \
                    (qualifies,
                     "you or other investigator on the same location",
                     lambda investigator: \
                         arkham.GameplayAction_Heal \
                                (arkham.Heal ({arkham.health_stamina:
                                                   successes})))

            return [arkham.GameplayAction_Multiple \
                        ([arkham.GameplayAction_Exhaust (item),
                           arkham.GameplayAction_CauseHarm \
                               (game, owner, item,
                                arkham.HarmSanity (1)),
                           arkham.GameplayAction_WithNumberOfSuccesses \
                               (game, owner, item,
                                arkham.SkillCheck (arkham.checkbase_lore, +1),
                                success_action)])]

    class MistsOfReleh (module.mod_spell.SpellItem):
        def __init__ (self):
            module.mod_spell.SpellItem.__init__ (self, "Mists of Releh", 0, 0)

    @game.perform_check_actions_hook.match \
        (fun.any, fun.any, fun.any, arkham.match_proto (MistsOfReleh),
         fun.val == arkham.checkbase_evade, fun.any, fun.any)
    def do (game, investigator, subject, item,
            check_base, modifier, difficulty):
        """Any Phase: Cast and exhaust to pass an Evade check. The
        casting modifier is equal to the monster's Awareness."""

        return [arkham.GameplayAction_Multiple \
                    ([arkham.GameplayAction_Exhaust (item),
                      arkham.GameplayAction_Conditional \
                          (game, investigator, item,
                           arkham.SkillCheck (arkham.checkbase_lore, modifier),
                           arkham.GameplayAction_PassCheck ())])]

    class RedSignOfShuddeMell (module.mod_spell.SpellItem):
        def __init__ (self):
            module.mod_spell.SpellItem.__init__ \
                (self, "Red Sign of Shudde M'ell", 0, 0)

        def combat_turn (self, combat, owner, monster, item):
            """Any Phase: Cast and exhaust to lower a monster's
            toughness by 1 (to a minimum of 1) and ignore one of its
            special abilities other than Magical Immunity until the
            end of this combat. """

            if item.exhausted ():
                return []

            a1 = r1 = a2 = r2 = None

            cc = monster.combat_check ()
            # xxx better solution: difficulty modifiers.  Make them
            # decorators.  Make everything that can be altered like
            # this the same way, based on some sort of decorator
            # object.  Action will be installation of a new decorator,
            # reaction will be removal of that same decorator.
            if fun.matchclass (arkham.SkillCheck) (cc) \
                    and cc.difficulty () > 1:
                a1 = arkham.GameplayAction_ReduceMonsterToughness \
                    (monster, 1, 1)
                r1 = arkham.GameplayAction_SetMonsterToughness \
                    (monster, cc.difficulty ())

            def build_candidates ():
                return list \
                    (ability
                     for ability, parameter \
                         in monster.special_abilities ().iteritems ()
                     if ability != arkham.monster_magical
                     or parameter != arkham.reslev_immunity)

            # xxx I believe this could be done the same way as above.
            # The decorator would filter out or include any abilities
            # that it wishes to.
            if len (build_candidates ()) > 0:
                class mem:
                    def set (self, content):
                        self._content = content
                    def get (self):
                        return self._content

                def build_action_ctor (m, action_ctor):
                    def ctor (candidate):
                        class Action (arkham.GameplayAction_One):
                            def __init__ (self, action):
                                arkham.GameplayAction_One.__init__ \
                                    (self, action, action.name ())

                            def perform (self, game, investigator):
                                m.set (candidate)
                                self.m_action.perform (game, investigator)
                        return Action (action_ctor (candidate))
                    return ctor

                class Reaction (arkham.GameplayAction):
                    def __init__ (self, name, ctor):
                        arkham.GameplayAction.__init__ (self, name)
                        self.m_ctor = ctor

                    def perform (self, game, investigator):
                        selected = m.get ()
                        self.m_ctor (selected).perform (game, investigator)

                m = mem ()

                a2 = arkham.GameplayAction_WithSelected \
                    (build_candidates,
                     "one of monster's special abilities " \
                         + "other than Magical Immunity",
                     build_action_ctor \
                         (m, lambda candidate:
                              arkham.GameplayAction_DropSpecialAbility \
                                (monster, candidate)),
                     arkham.MonsterSpecialAbility ("selected"))
                r2 = Reaction \
                    ("reintroduce once dropped special ability",
                     lambda selected:
                       arkham.GameplayAction_CancelSpecialAbilityCustomization \
                         (monster, selected))

            if a1 == None and a2 == None:
                return []

            return [
                arkham.GameplayAction_Multiple \
                    ([arkham.GameplayAction_Exhaust (item),
                      arkham.GameplayAction_CauseHarm \
                          (combat.game, owner, item, arkham.HarmSanity (1)),
                      arkham.GameplayAction_Conditional \
                          (combat.game, owner, item,
                           arkham.SkillCheck (arkham.checkbase_lore, -1),
                           arkham.GameplayAction_ForCombat \
                               (combat,
                                arkham.GameplayAction_Multiple ([a1, a2]),
                                arkham.GameplayAction_Multiple ([r1, r2])))])]

    class VoiceOfRa (module.mod_spell.SpellItem):
        class Instance (module.mod_spell.SpellInst):
            def __init__ (self, parent):
                module.mod_spell.SpellInst.__init__ \
                    (self, parent.name (), 0, 0)

        def __init__ (self):
            module.mod_spell.SpellItem.__init__ \
                (self, "Voice of Ra", 0, 0)

        def gen_bonus_action (self, game, owner, item):
            if item.exhausted ():
                return []

            inst = arkham.Item (VoiceOfRa.Instance (self))
            if not owner.find_wield (game, inst, inst.hands ()):
                return []

            return [arkham.GameplayAction_Multiple \
                        ([arkham.GameplayAction_Exhaust (item),
                          arkham.GameplayAction_CauseHarm \
                              (game, owner, item,
                               arkham.HarmSanity (1)),
                          arkham.GameplayAction_Conditional \
                              (game, owner, item,
                               arkham.SkillCheck (arkham.checkbase_lore, -1),
                               arkham.GameplayAction_ForTurn \
                                   (arkham.GameplayAction_WieldItem \
                                        (inst, True),
                                    arkham.GameplayAction_Discard (inst)))])]

        def combat_turn (self, combat, owner, monster, item):
            return self.gen_bonus_action (combat.game, owner, item)

        def movement (self, game, owner, item):
            return self.gen_bonus_action (game, owner, item)

    @game.bonus_hook.match \
        (fun.any, fun.any, fun.any,
         arkham.match_proto (VoiceOfRa.Instance),
         fun.any)
    def do (game, investigator, subject, item, check_base):
        return arkham.Bonus (1, arkham.family_magical)

    for count, item_proto in [
            (2, BindMonster ()),
            (4, simple_bonus_spell ("Dread Curse of Azathoth", -2, 2, 2,
                                    {arkham.checkbase_combat:
                                         arkham.Bonus (9, arkham.family_magical)})),
            (3, EnchantWeapon ()),
            (4, FleshWard ()),
            (3, Heal ()),
            (4, MistsOfReleh ()),
            (2, RedSignOfShuddeMell ()),
            (5, simple_bonus_spell ("Shrivelling", -1, 1, 1,
                                    {arkham.checkbase_combat:
                                         arkham.Bonus (6, arkham.family_magical)})),
            (3, VoiceOfRa ()),
            (6, simple_bonus_spell ("Wither", +0, 0, 1,
                                    {arkham.checkbase_combat:
                                         arkham.Bonus (3, arkham.family_magical)})),
        ]:
        module.m_spell_deck.register (item_proto, count)

    # -------------------------------------------------------------------------

    def skill_reroll (name, *what_to_reroll):
        class SkillReroll (module.mod_skill.SkillItem):
            def __init__ (self):
                module.mod_skill.SkillItem.__init__ (self, name, 0, 0)

        for checkbase in what_to_reroll:
            @game.check_correction_actions_hook.match \
                (fun.any, fun.any, fun.any,
                 arkham.match_proto (SkillReroll),
                 fun.val == checkbase, fun.any)
            def do (game, investigator, subject, item, checkbase, roll):
                return [arkham.GameplayAction_Multiple \
                            ([arkham.GameplayAction_Exhaust (item),
                              arkham.GameplayAction_Reroll \
                                  (subject, checkbase, roll)])]

        return SkillReroll ()

    def skill_correction (name, *what_to_correct):
        class SkillCorrection (module.mod_skill.SkillItem):
            def __init__ (self):
                module.mod_skill.SkillItem.__init__ (self, name, 0, 0)

    for count, item_proto in [
            (1, skill_reroll ("Bravery", arkham.checkbase_horror)),
            (1, skill_reroll ("Expert Occultist", arkham.checkbase_spell)),
        ]:
        module.m_skill_deck.register (item_proto, count)
