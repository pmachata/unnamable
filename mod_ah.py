import arkham
import maps
import fight
import fun

def find_location (game, flag):
    for location in game.all_locations ():
        if location.attributes ().flag (flag):
            return location
    return None

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

class GameplayAction_InvestigatorScrewed (arkham.GameplayAction):
    def __init__ (self, location):
        arkham.GameplayAction.__init__ (self, "move to %s and lose half the stuff" % location.name ())
        self.m_location = location

    def perform (self, game, investigator):
        investigator.move_to (self.m_location)
        print "lose half items" # xxx
        print "lose half clue tokens" # xxx
        print "lose all retainers" # xxx

    def bound_location (self):
        return self.m_location

class GameplayAction_Insane (GameplayAction_InvestigatorScrewed):
    def __init__ (self, location):
        GameplayAction_InvestigatorScrewed.__init__ (self, location)

    def perform (self, game, investigator):
        GameplayAction_InvestigatorScrewed.perform (self, game, investigator)
        investigator.add_sanity (1)

class GameplayAction_Unconscious (GameplayAction_InvestigatorScrewed):
    def __init__ (self, location):
        GameplayAction_InvestigatorScrewed.__init__ (self, location)

    def perform (self, game, investigator):
        GameplayAction_InvestigatorScrewed.perform (self, game, investigator)
        investigator.add_stamina (1)


def has_token (what):
    def match (arg):
        #return arg.has_token (what) XXX
        return False
    return match

@arkham.dice_roll_successful_hook.match (fun.any, has_token ("blessing"), fun.any, fun.any)
def do (game, investigator, skill, roll):
    return roll >= 4

@arkham.dice_roll_successful_hook.match (fun.any, has_token ("curse"), fun.any, fun.any)
def do (game, investigator, skill, roll):
    return roll >= 6

class ModuleProto (arkham.ModuleProto):
    def __init__ (self):
        arkham.ModuleProto.__init__ (self, "ah", "Arkham Horror")
        self.mod_ancient = None
        self.mod_skills = None
        self.mod_terror = None

    def consistent (self, mod_index):
        ancient = mod_index.request ("ancient")
        monster = mod_index.request ("monster")
        skills = mod_index.request ("skills")
        terror = mod_index.request ("terror")
        success = ancient and monster and skills and terror
        if not success:
            ancient = None
            monster = None
            skills = None
            terror = None

        self.mod_ancient = ancient
        self.mod_skills = skills
        self.mod_terror = terror
        return not not success

    def construct (self, game):

        class TerrorTrack_AHEvents (arkham.TrackEvent):
            def event (self, game, owner, level):
                print "drop ally" # XXX
                if level == 10:
                    print "relax monster limit" # XXX
                elif level > 10:
                    print "add to doom track" # XXX

                for location in game.all_locations ():
                    if location.attributes ().get ("terror_close") == level:
                        print "close location %s" % location.name () # XXX

        self.mod_terror.track.add_event (TerrorTrack_AHEvents ())

        maps.in_neighborhood (maps.neighborhood (game))
        merchant_district = maps.location ("Merchant District", street = True)
        unvisited_isle = maps.location ("Unvisited Isle", unstable = True)
        river_docks = maps.location ("River Docks")
        the_unnamable = maps.location ("The Unnamable", unstable = True)
        (maps.draw_from (merchant_district)
         .out (unvisited_isle, black = True, white = True).back ()
         .out (the_unnamable, black = True, white = True).back ()
         .out (river_docks, black = True, white = True).back ())

        maps.in_neighborhood (maps.neighborhood (game))
        miskatonic_u = maps.location ("Miskatonic University", street = True)
        science_building = maps.location ("Science Building", unstable = True)
        administration = maps.location ("Administration")
        library = maps.location ("Library")
        (maps.draw_from (miskatonic_u)
         .out (science_building, black = True, white = True).back ()
         .out (administration, black = True, white = True).back ()
         .out (library, black = True, white = True).back ())

        maps.in_neighborhood (maps.neighborhood (game))
        uptown = maps.location ("Uptown", street = True)
        st_mary = maps.location ("St. Mary's Hospital",
                                 hospital = True, seeker_avoids = True)
        magick_shop = maps.location ("Ye Olde Magick Shoppe", terror_close = 9)
        woods = maps.location ("Woods", unstable = True)
        (maps.draw_from (uptown)
         .out (st_mary, black = True, white = True).back ()
         .out (magick_shop, black = True, white = True).back ()
         .out (woods, black = True, white = True).back ())

        maps.in_neighborhood (maps.neighborhood (game))
        southside = maps.location ("Southside", street = True)
        historical_society = maps.location ("Historical society", unstable = True)
        south_church = maps.location ("South Church")
        ma_s_boarding = maps.location ("Ma's Boarding House")
        (maps.draw_from (southside)
         .out (historical_society, black = True, white = True).back ()
         .out (south_church, black = True, white = True).back ()
         .out (ma_s_boarding, black = True, white = True).back ())

        maps.in_neighborhood (maps.neighborhood (game))
        french_hill = maps.location ("French Hill", street = True)
        silver_twilight = maps.location ("Silver Twilight Lodge", unstable = True)
        witch_house = maps.location ("The Witch House", unstable = True)
        (maps.draw_from (french_hill)
         .out (silver_twilight, black = True, white = True).back ()
         .out (witch_house, black = True, white = True).back ())

        maps.in_neighborhood (maps.neighborhood (game))
        rivertown = maps.location ("Rivertown", street = True)
        general_store = maps.location ("General Store", terror_close = 3)
        black_cave = maps.location ("Black Cave", unstable = True)
        graveyard = maps.location ("Graveyard", unstable = True)
        (maps.draw_from (rivertown)
         .out (general_store, black = True, white = True).back ()
         .out (black_cave, black = True, white = True).back ()
         .out (graveyard, black = True, white = True).back ())

        maps.in_neighborhood (maps.neighborhood (game))
        easttown = maps.location ("Easttown", street = True)
        police_station = maps.location ("Police Station")
        velmas_dinner = maps.location ("Velma's Dinner")
        hibbs_roadhouse = maps.location ("Hibb's Roadhouse", unstable = True)
        (maps.draw_from (easttown)
         .out (police_station, black = True, white = True).back ()
         .out (velmas_dinner, black = True, white = True).back ()
         .out (hibbs_roadhouse, black = True, white = True).back ())

        maps.in_neighborhood (maps.neighborhood (game))
        downtown = maps.location ("Downtown", street = True)
        independence_sq = maps.location ("Independence Square", unstable = True)
        arkham_asylum = maps.location ("Arkham Asylum",
                                       asylum = True, seeker_avoids = True)
        bank_of_arkham = maps.location ("Bank of Arkham")
        (maps.draw_from (downtown)
         .out (independence_sq, black = True, white = True).back ()
         .out (arkham_asylum, black = True, white = True).back ()
         .out (bank_of_arkham, black = True, white = True).back ())

        maps.in_neighborhood (maps.neighborhood (game))
        northside = maps.location ("Northside", street = True)
        train_station = maps.location ("Train Station")
        newspaper = maps.location ("Newspaper")
        curiosity_shop = maps.location ("Curiositie Shoppe", terror_close = 6)
        (maps.draw_from (northside)
         .out (train_station, black = True, white = True).back ()
         .out (newspaper, black = True, white = True).back ()
         .out (curiosity_shop, black = True, white = True).back ())

        maps.in_neighborhood (None)
        maps.location ("Sky", sky = True)
        maps.location ("Lost in Time and Space", lost_in_time_and_space = True)

        (maps.draw_from (downtown)
         .to (northside, black = True).back (white = True)
         .to (merchant_district, black = True).back (white = True)
         .to (miskatonic_u, black = True).back (white = True)
         .out (french_hill).back ()
         .to (uptown, black = True).back (white = True)
         .to (southside, black = True).back (white = True)
         .to (french_hill, black = True).back (white = True)
         .to (rivertown, black = True).back (white = True)
         .to (easttown, black = True).back (white = True)
         .to (downtown, black = True).back (white = True)
         .to (merchant_district).back ()
         .to (rivertown).back ())

        game.add_investigator (
            arkham.Investigator (
                "\"Ashcan\" Pete", 4, 6, 1, 3,
                self.mod_skills.Skills (4,
                                        3, 6, 5,
                                        5, 3, 3),
                river_docks
            )
        )

        # xxx hack
        def monster_match (klass):
            def match (arg):
                return fun.matchclass (arkham.Monster) (arg) \
                    and fun.matchclass (klass) (arg.proto ())
            return match

        class ElderThing (arkham.SimpleMonster):
            def __init__ (self):
                arkham.SimpleMonster.__init__ \
                    (self, "Elder Thing",
                     -2, (-3, 2), 2, (+0, 1))

        @fight.combat_check_fail_hook.match (fun.any, fun.any, monster_match (ElderThing))
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

        @fight.combat_check_pass_hook.match (fun.any, fun.any, monster_match (MiGo))
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

        @fight.fight_hook.match (fun.any, fun.any, monster_match (TheBlackMan))
        def do (combat, investigator, monster):
            if arkham.SkillCheck ("luck", -1).check (combat.game, investigator):
                investigator.gain_clues (2)
                raise fight.EndCombat (True)
            else:
                investigator.devour (combat.game, monster)
                raise fight.EndCombat (False)

        @fight.deal_combat_damage_hook.match (fun.any, fun.any, monster_match (TheBlackMan))
        def do (combat, investigator, monster):
            pass

        @fight.combat_won_hook.match (fun.any, fun.any, monster_match (TheBlackMan))
        def do (combat, investigator, monster):
            fight.endless_combat_won_hook (combat, investigator, monster)

        @fight.combat_lost_hook.match (fun.any, fun.any, monster_match (TheBlackMan))
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

        @fight.fight_hook.match (fun.any, fun.any, monster_match (TheBloatedWoman))
        def do (combat, investigator, monster):
            """Before making a Horror check, pass a Will(-2) check or
            or automatically fail the Horror check and the Combat check."""
            if not arkham.SkillCheck ("will", -2).check (combat.game, investigator):
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
            (3, Maniac (self.mod_terror)),
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
            game.register_monster (monster, count)

        # Some of these will have special skills, and it will be
        # necessary to expand the definition.  For now, this condensed
        # form suffices.
        Ancient = self.mod_ancient.Ancient
        def ancient (name):
            class AH_Ancient (Ancient):
                def __init__ (self):
                    Ancient.__init__ (self, name)
            return AH_Ancient

        class Nyarlathotep (Ancient):
            def __init__ (self):
                Ancient.__init__ (self, "Nyarlathotep")

            def before_turn_0 (self, game):
                import random
                masks = [monster for monster in game.registered_monsters ()
                         if monster.attributes ().flag ("mask")]

                for mask in random.sample (masks, 5):
                    game.put_monster_in_cup (mask)

            def before_battle (self, game):
                # Any investigator with no Clue tokens is devoured.
                for investigator in game.investigators ():
                    if investigator.clues () == 0:
                        investigator.devour (game, self)

        for ancient in [ancient ("Azathoth"),
                        ancient ("Cthulhu"),
                        Nyarlathotep]:
            self.mod_ancient.register (ancient)

    def post_construct (self, game):
        def append_special_place (flag):
            place = find_location (game, flag)
            assert place != None

            for location in game.all_locations ():
                if location.attributes ().flag ("street") and location != place:
                    (maps.draw_from (place)
                     .to (location,
                          white = True, black = True,
                          no_investigator = True)
                     # does it also lead back?
                     #.back (no_investigator = True)
                     )

            return place

        append_special_place ("sky")
        append_special_place ("lost_in_time_and_space")

    def before_turn_0 (self, game):
        for location in game.all_locations ():
            if location.attributes ().flag ("unstable"):
                location.add_clue_tokens (1)

    def turn_0 (self, game):
        # XXX draw a mythos card and resolve it as usual.  If a Rumor
        # is drawn, discard it and draw again until you draw a mythos
        # card that isn't a Rumor.

        # For now just play ordinary mythos phase.
        self.mythos (game)

        loc = None
        for location in game.all_locations ():
            if location.name () == "River Docks":
                loc = location
                break
        assert loc != None

        if False:
            for monster in game.monster_cup ():
                if monster.name () == "The Black Man":
                    game.monster_from_cup (monster, loc)
                    break

    def mythos (self, game):
        # XXX For now just put new monster somewhere.  It may turn out
        # to be in "lost in time and space", but we don't care, it's
        # just a temporary solution.
        import random
        print "; ".join (mon.name () for mon in game.monster_cup ())
        game.monster_from_cup \
            (random.choice (game.monster_cup ()),
             random.choice ([location
                             for location in game.all_locations ()
                             if not location.attributes ().flag ("street")]))
        return []

    def investigator_unconscious (self, game):
        return [GameplayAction_Unconscious (location)
                for location in game.all_locations ()
                             if location.attributes ().flag ("hospital")]

    def investigator_insane (self, game):
        return [GameplayAction_Insane (location)
                for location in game.all_locations ()
                             if location.attributes ().flag ("asylum")]
