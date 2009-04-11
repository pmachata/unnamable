import fun
import fight
import arkham

# xxx should be published by module so that it's possible to override it
lose_in_time_and_space = fun.Function (arkham.Game, arkham.Investigator,
                                       name="lose_in_time_and_space", trace=arkham.trace)
@lose_in_time_and_space.match (fun.any, fun.any)
def do (game, investigator):
    place = find_location (game, "lost_in_time_and_space")
    if place != None:
        game.move_investigator (investigator, place)
    investigator.delay ()

class DamageLost (arkham.Damage):
    def deal (self, game, investigator, monster):
        lose_in_time_and_space (game, investigator)

    def description (self, game, investigator, monster):
        return "lost in time and space"

damage_lost = DamageLost ()

def build (game, module):

    class ElderThing (arkham.SimpleMonster):
        def __init__ (self):
            arkham.SimpleMonster.__init__ \
                (self, "Elder Thing",
                 -2, (-3, 2), 2, (+0, 1))

    @fight.combat_check_fail_hook.match (fun.any, fun.any, arkham.match_proto (ElderThing))
    def do (game, investigator, monster):
        print """XXX When you fail a Combat check against Elder
        Thing, you must discard 1 of your Weapons or Spells (your
        choice), if able."""
        fight.deal_combat_damage_hook (game, investigator, monster)

    class Maniac (arkham.BasicMonster):
        def __init__ (self, mod_terror):
            terror_at_least_6 = mod_terror.terror_at_least_p (6)
            arkham.BasicMonster.__init__ \
                (self, "Maniac",
                 arkham.evade_check (-1),
                 arkham.pass_check,
                 arkham.damage_none,
                 arkham.ConditionalCheck (terror_at_least_6,
                                          arkham.combat_check (+1, 1),
                                          arkham.combat_check (-2, 1)),
                 arkham.ConditionalDamage (terror_at_least_6,
                                           arkham.DamageStamina (1),
                                           arkham.DamageStamina (3)),
                 endless = True) # XXX only if terror_track >= 6!


    class MiGo (arkham.SimpleMonster):
        def __init__ (self):
            arkham.SimpleMonster.__init__ \
                (self, "Mi-Go",
                 -2, (-1, 2), 1, (+0, 1),
                 endless = True) # Not technically endless, but
                                 # goes to the cup after it's
                                 # killed.

    @fight.combat_check_pass_hook.match (fun.any, fun.any, arkham.match_proto (MiGo))
    def do (game, investigator, monster):
        print """XXX If you pass a Combat check against Migo,
        return it to the box and draw 1 Unique Item."""
        raise fight.EndCombat (True)


    class Nightgaunt (arkham.BasicMonster):
        def __init__ (self):
            class Damage (arkham.Damage):
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
                 arkham.horror_check (-1), arkham.DamageSanity (1),
                 arkham.combat_check (-2, 2), Damage ())


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

        def horror_damage (self):
            return arkham.SpecialDamage ()

        def combat_damage (self):
            return arkham.SpecialDamage ()

    @fight.fight_hook.match (fun.any, fun.any, arkham.match_proto (TheBlackMan))
    def do (combat, investigator, monster):
        if arkham.SkillCheck ("luck", -1).check (combat.game, investigator, monster):
            investigator.gain_clues (2)
            raise fight.EndCombat (True)
        else:
            investigator.devour (combat.game, monster)
            raise fight.EndCombat (False)

    @fight.deal_combat_damage_hook.match (fun.any, fun.any, arkham.match_proto (TheBlackMan))
    def do (combat, investigator, monster):
        pass

    @fight.combat_won_hook.match (fun.any, fun.any, arkham.match_proto (TheBlackMan))
    def do (combat, investigator, monster):
        fight.endless_combat_won_hook (combat, investigator, monster)

    @fight.combat_lost_hook.match (fun.any, fun.any, arkham.match_proto (TheBlackMan))
    def do (combat, investigator, monster):
        fight.endless_combat_won_hook (combat, investigator, monster)

    class TheBloatedWoman (arkham.SimpleMonster):
        def __init__ (self):
            arkham.SimpleMonster.__init__ \
                (self, "The Bloated Woman",
                 -1, (-1, 2), 2, (-2, 2),
                 in_cup = False,
                 mask = True,
                 endless = True)

    @fight.fight_hook.match (fun.any, fun.any, arkham.match_proto (TheBloatedWoman))
    def do (combat, investigator, monster):
        """Before making a Horror check, pass a Will(-2) check or
        or automatically fail the Horror check and the Combat check."""
        if not arkham.SkillCheck ("will", -2).check (combat.game, investigator, monster):
            fight.horror_check_fail_hook (combat, investigator, monster)
            fight.combat_check_fail_hook (combat, investigator, monster)
            fight.combat_loop_hook (combat, investigator, monster)
        else:
            fight.normal_fight_hook (combat, investigator, monster)


    for count, monster in [
        (3, arkham.SimpleMonster ("Byakhee",
                                  -2, (-1, 1), 1, (+0, 2))),
        (2, arkham.SimpleMonster ("Chthonian",
                                  +1, (-2, 2), 3, (-3, 3))),
        (6, arkham.BasicMonster ("Cultist",
                                 arkham.evade_check (-3),
                                 arkham.pass_check,
                                 arkham.damage_none,
                                 arkham.combat_check (+1, 1),
                                 arkham.DamageStamina (1))),
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
                                 arkham.DamageSanity (1),
                                 arkham.combat_check (-2, 1),
                                 damage_lost)),
        (2, ElderThing ()),
        (2, arkham.BasicMonster ("Fire Vampire",
                                 arkham.evade_check (+0),
                                 arkham.pass_check,
                                 arkham.damage_none,
                                 arkham.combat_check (+2, 1),
                                 arkham.DamageStamina (2))),
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
        (1, arkham.BasicMonster ("Haunter Of The Dark",
                                 arkham.evade_check (-3),
                                 arkham.horror_check (-1),
                                 arkham.DamageSanity (2),
                                 arkham.ConditionalCheck\
                                     (lambda game, investigator: \
                                          ### Temporary...
                                          game.environment () == "Blackest Night",
                                      arkham.combat_check (-5, 2),
                                      arkham.combat_check (-2, 2)),
                                 arkham.DamageStamina (2),
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
        (1, arkham.BasicMonster ("The Dark Pharoah",
                                 arkham.evade_check (-1),
                                 arkham.horror_check (-1),
                                 arkham.DamageSanity (1),
                                 arkham.SkillCheck ("lore", -3, 2),
                                 arkham.DamageStamina (3),
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
                                 arkham.damage_none,
                                 arkham.combat_check (-3, 1),
                                 arkham.DamageStamina (2),
                                 magical = "resistance")),
        (2, arkham.SimpleMonster ("Zombie",
                                  +1, (-1, 1), 1, (-1, 2),
                                  undead = True)),
        ]:
        module.m_monster_cup.register (monster, count)