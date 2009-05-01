import fun
import arkham

def build (game, module):

    class ElderThing (arkham.SimpleMonster):
        def __init__ (self):
            arkham.SimpleMonster.__init__ \
                (self, "Elder Thing",
                 -2, (-3, 2), 2, (+0, 1))

    @game.combat_check_fail_hook.match \
        (fun.any, fun.any, arkham.match_proto (ElderThing))
    def do (game, investigator, monster):
        print """XXX When you fail a Combat check against Elder
        Thing, you must discard 1 of your Weapons or Spells (your
        choice), if able."""
        arkham.cause_combat_harm_hook (game, investigator, monster)

    class Maniac (arkham.BasicMonster):
        def __init__ (self, mod_terror):
            terror_at_least_6 = mod_terror.terror_at_least_p (6)
            arkham.BasicMonster.__init__ \
                (self, "Maniac",
                 arkham.evade_check (-1),
                 arkham.pass_check,
                 arkham.harm_none,
                 arkham.ConditionalCheck (terror_at_least_6,
                                          arkham.combat_check (+1, 1),
                                          arkham.combat_check (-2, 1)),
                 arkham.ConditionalHarm (terror_at_least_6,
                                         arkham.HarmStamina (1),
                                         arkham.HarmStamina (3)),
                 endless = True) # XXX only if terror_track >= 6!


    class MiGo (arkham.SimpleMonster):
        def __init__ (self):
            arkham.SimpleMonster.__init__ \
                (self, "Mi-Go",
                 -2, (-1, 2), 1, (+0, 1),
                 endless = True) # Not technically endless, but
                                 # goes to the cup after it's
                                 # killed.

    @game.combat_check_pass_hook.match \
        (fun.any, fun.any, arkham.match_proto (MiGo))
    def do (game, investigator, monster):
        print """XXX If you pass a Combat check against Migo,
        return it to the box and draw 1 Unique Item."""
        raise arkham.EndCombat (True)


    class Nightgaunt (arkham.BasicMonster):
        def __init__ (self):
            class Harm (arkham.Harm):
                def deal (self, game, investigator, monster):
                    print """XXX you are drawn through the nearest
                    open gate. If two or more gates are the same
                    distance from you, you choose which gate you
                    are drawn through."""

                def description (self, game, investigator, monster):
                    return "draw through the nearest open gate"

            arkham.BasicMonster.__init__ \
                (self, "Nightgaunt",
                 arkham.evade_check (-2),
                 arkham.horror_check (-1), arkham.HarmSanity (1),
                 arkham.combat_check (-2, 2), Harm ())


    # The rules say: """Before making a Horror check, pass a
    # Luck(-1) check or be devoured. If you pass, gain 2 Clue
    # tokens. In either case, return the Black Man to the cup."""
    # This monster has no horror or combat damange at all.
    #
    # I think it means that if I fail to avoid this monster, I
    # won't get any combat damage.  The combat will then ensue as
    # described above, by Luck check.
    class TheBlackMan (arkham.MonsterProto):
        def __init__ (self):
            arkham.MonsterProto.__init__ \
                (self, "The Black Man",
                 in_cup = False,
                 mask = True,
                 endless = True)

        def evade_check (self):
            return arkham.evade_check (-3)

        def horror_check (self):
            return arkham.SpecialCheck ()

        def combat_check (self):
            return arkham.SpecialCheck ()

        def horror_harm (self):
            return arkham.SpecialHarm ()

        def combat_harm (self):
            return arkham.SpecialHarm ()

    @game.fight_hook.match \
        (fun.any, fun.any, arkham.match_proto (TheBlackMan))
    def do (combat, investigator, monster):
        if arkham.SkillCheck (arkham.checkbase_luck, -1) \
                .check (combat.game, investigator, monster):
            investigator.gain_clues (2)
            raise arkham.EndCombat (True)
        else:
            investigator.devour (combat.game, monster)
            raise arkham.EndCombat (False)

    @game.cause_combat_harm_hook.match \
        (fun.any, fun.any, arkham.match_proto (TheBlackMan))
    def do (combat, investigator, monster):
        pass

    @game.combat_won_hook.match \
        (fun.any, fun.any, arkham.match_proto (TheBlackMan))
    def do (combat, investigator, monster):
        arkham.endless_combat_won_hook (combat, investigator, monster)

    @game.combat_lost_hook.match \
        (fun.any, fun.any, arkham.match_proto (TheBlackMan))
    def do (combat, investigator, monster):
        arkham.endless_combat_won_hook (combat, investigator, monster)

    class TheBloatedWoman (arkham.SimpleMonster):
        def __init__ (self):
            arkham.SimpleMonster.__init__ \
                (self, "The Bloated Woman",
                 -1, (-1, 2), 2, (-2, 2),
                 in_cup = False,
                 mask = True,
                 endless = True)

    @game.fight_hook.match \
        (fun.any, fun.any, arkham.match_proto (TheBloatedWoman))
    def do (combat, investigator, monster):
        """Before making a Horror check, pass a Will(-2) check or
        or automatically fail the Horror check and the Combat check."""
        if not arkham.SkillCheck (arkham.checkbase_will, -2) \
                .check (combat.game, investigator, monster):
            arkham.horror_check_fail_hook (combat, investigator, monster)
            arkham.combat_check_fail_hook (combat, investigator, monster)
            arkham.combat_loop_hook (combat, investigator, monster)
        else:
            arkham.normal_fight_hook (combat, investigator, monster)


    for count, monster in [
        (3, arkham.SimpleMonster ("Byakhee",
                                  -2, (-1, 1), 1, (+0, 2))),
        (2, arkham.SimpleMonster ("Chthonian",
                                  +1, (-2, 2), 3, (-3, 3))),
        (6, arkham.BasicMonster ("Cultist",
                                 arkham.evade_check (-3),
                                 arkham.pass_check,
                                 arkham.harm_none,
                                 arkham.combat_check (+1, 1),
                                 arkham.HarmStamina (1))),
        (3, arkham.SimpleMonster ("Dark Young",
                                  -2, (+0, 3), 3, (-1, 3),
                                  physical = "resistance",
                                  nightmarish = 1)),
        (1, arkham.SimpleMonster ("Dhole",
                                  -1, (-10, 40), 3, (-3, 4),
                                  physical = "resistance",
                                  magical = "resistance",
                                  nightmarish = 1,
                                  overwhelming = 1)),
        (2, arkham.BasicMonster ("Dimensional Shambler",
                                 arkham.evade_check (-3),
                                 arkham.horror_check (-2),
                                 arkham.HarmSanity (1),
                                 arkham.combat_check (-2, 1),
                                 module.harm_lost)),
        (2, ElderThing ()),
        (2, arkham.BasicMonster ("Fire Vampire",
                                 arkham.evade_check (+0),
                                 arkham.pass_check,
                                 arkham.harm_none,
                                 arkham.combat_check (+2, 1),
                                 arkham.HarmStamina (2))),
        (1, arkham.SimpleMonster ("Flying Polyp",
                                  +0, (-2, 4), 3, (-3, 3),
                                  physical = "resistance",
                                  nightmarish = 1,
                                  overwhelming = 1)),
        (2, arkham.SimpleMonster ("Formless Spawn",
                                  +0, (-1, 2), 2, (-2, 2))),
        (2, arkham.SimpleMonster ("Ghost",
                                  -3, (-2, 2), 1, (-3, 2),
                                  physical = "immunity",
                                  undead = True)),
        (3, arkham.SimpleMonster ("Ghoul",
                                  -3, (+0, 1), 1, (-1, 1),
                                  ambush = True)),
        (1, arkham.SimpleMonster ("God Of The Bloody Tongue",
                                  +1, (-3, 3), 4, (-4, 4),
                                  in_cup = False,
                                  mask = True,
                                  endless = True,
                                  overwhelming = 1,
                                  nightmarish = 1)),
        (2, arkham.SimpleMonster ("Gug",
                                  -2, (-1, 2), 3, (-2, 4),
                                  overwhelming = 1)),
        (1, arkham.BasicMonster \
             ("Haunter Of The Dark",
              arkham.evade_check (-3),
              arkham.horror_check (-1),
              arkham.HarmSanity (2),
              arkham.ConditionalCheck\
                  (lambda game, investigator: \
                       ### Temporary...
                       game.environment () == "Blackest Night",
                   arkham.combat_check (-5, 2),
                   arkham.combat_check (-2, 2)),
              arkham.HarmStamina (2),
              in_cup = False,
              mask = True,
              endless = True)),
        (1, arkham.SimpleMonster ("High Priest",
                                  -2, (+1, 1), 2, (-2, 2),
                                  magical = "immunity")),
        (2, arkham.SimpleMonster ("Hound Of Tindalos",
                                  -1, (-2, 4), 2, (-1, 3),
                                  physical = "immunity")),
        (3, Maniac (module.mod_terror)),
        (3, MiGo ()),
        (2, Nightgaunt ()),
        (2, arkham.SimpleMonster ("Shoggoth",
                                  -1, (-1, 3), 3, (-1, 3),
                                  physical = "resistance",
                                  nightmarish = 1)),
        (2, arkham.SimpleMonster ("Star Spawn",
                                  -1, (-3, 2), 3, (-3, 3))),
        (1, TheBlackMan ()),
        (1, TheBloatedWoman ()),
        (1, arkham.BasicMonster \
             ("The Dark Pharoah",
              arkham.evade_check (-1),
              arkham.horror_check (-1),
              arkham.HarmSanity (1),
              arkham.SkillCheck (arkham.checkbase_lore, -3, 2),
              arkham.HarmStamina (3),
              in_cup = False,
              mask = True,
              endless = True)),
        (1, arkham.SimpleMonster ("Vampire",
                                  -3, (+0, 2), 2, (-3, 3),
                                  undead = True,
                                  physical = "resistance")),
        (2, arkham.SimpleMonster ("Warlock",
                                  -2, (-1, 1), 2, (-3, 1),
                                  magical = "immunity")),
        (2, arkham.BasicMonster ("Witch",
                                 arkham.evade_check (-1),
                                 arkham.pass_check,
                                 arkham.harm_none,
                                 arkham.combat_check (-3, 1),
                                 arkham.HarmStamina (2),
                                 magical = "resistance")),
        (2, arkham.SimpleMonster ("Zombie",
                                  +1, (-1, 1), 1, (-1, 2),
                                  undead = True)),
        ]:
        module.m_monster_cup.register (monster, count)
