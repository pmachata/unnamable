import arkham
import maps
import fight
import fun

class Investigator (arkham.Investigator):
    def __init__ (self, mod_ah, *args):
        arkham.Investigator.__init__ (self, *args)
        self.mod_ah = mod_ah

    def lost_in_time_and_space (self, game, monster):
        # XXX This doesn't work.  We need to be able to lose in time
        # and space also investigators from other modules, which won't
        # necessarily depend on "ah".
        game.move_investigator (self, self.mod_ah.lost_in_time_and_space_place)

class DamageLost (arkham.Damage):
    def deal (self, game, investigator, monster):
        investigator.lost_in_time_and_space (game, monster)
damage_lost = DamageLost ()

class Module (arkham.Module):
    def __init__ (self):
        arkham.Module.__init__ (self, "ah", "Arkham Horror")
        self.mod_ancient = None
        self.mod_statset = None
        self.mod_terror = None

    def consistent (self, mod_index):
        ancient = mod_index.request ("ancient")
        statset = mod_index.request ("statset")
        monster = mod_index.request ("monster")
        terror = mod_index.request ("terror")
        success = ancient and statset and monster and terror
        if not success:
            ancient = None
            statset = None
            monster = None
            terror = None

        self.mod_ancient = ancient
        self.mod_statset = statset
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
                    if location.attributes.get ("terror_close") == level:
                        print "close location %s" % location.name () # XXX

        self.mod_terror.track.add_event (TerrorTrack_AHEvents ())

        maps.in_neighborhood (maps.neighborhood (game))
        merchant_district = maps.location ("Merchant District", street = True)
        unvisited_isle = maps.location ("Unvisited Isle", unstable = True)
        river_docks = maps.location ("River Docks")
        the_unnamable = maps.location ("The Unnamable", unstable = True)

        maps.in_neighborhood (maps.neighborhood (game))
        miskatonic_u = maps.location ("Miskatonic University", street = True)
        science_building = maps.location ("Science Building", unstable = True)
        administration = maps.location ("Administration")
        library = maps.location ("Library")

        maps.in_neighborhood (maps.neighborhood (game))
        uptown = maps.location ("Uptown", street = True)
        st_mary = maps.location ("St. Mary's Hospital", seeker_avoids = True)
        magick_shop = maps.location ("Ye Olde Magick Shoppe", terror_close = 9)
        woods = maps.location ("Woods", unstable = True)

        maps.in_neighborhood (maps.neighborhood (game))
        southside = maps.location ("Southside", street = True)
        historical_society = maps.location ("Historical society", unstable = True)
        south_church = maps.location ("South Church")
        ma_s_boarding = maps.location ("Ma's Boarding House")

        maps.in_neighborhood (maps.neighborhood (game))
        french_hill = maps.location ("French Hill", street = True)
        silver_twilight = maps.location ("Silver Twilight Lodge", unstable = True)
        witch_house = maps.location ("The Witch House", unstable = True)

        maps.in_neighborhood (maps.neighborhood (game))
        rivertown = maps.location ("Rivertown", street = True)
        general_store = maps.location ("General Store", terror_close = 3)
        black_cave = maps.location ("Black Cave", unstable = True)
        graveyard = maps.location ("Graveyard", unstable = True)

        maps.in_neighborhood (maps.neighborhood (game))
        easttown = maps.location ("Easttown", street = True)
        police_station = maps.location ("Police Station")
        velmas_dinner = maps.location ("Velma's Dinner")
        hibbs_roadhouse = maps.location ("Hibb's Roadhouse", unstable = True)

        maps.in_neighborhood (maps.neighborhood (game))
        downtown = maps.location ("Downtown", street = True)
        independence_sq = maps.location ("Independence Square", unstable = True)
        arkham_asylum = maps.location ("Arkham Asylum", seeker_avoids = True)
        bank_of_arkham = maps.location ("Bank of Arkham")

        maps.in_neighborhood (maps.neighborhood (game))
        northside = maps.location ("Northside", street = True)
        train_station = maps.location ("Train Station")
        newspaper = maps.location ("Newspaper")
        curiosity_shop = maps.location ("Curiositie Shoppe", terror_close = 6)

        maps.in_neighborhood (None)
        maps.location ("Sky", sky = True)
        maps.location ("Lost in Time and Space", lost_in_time_and_space = True)

        (maps.draw_from (merchant_district)
         .out (unvisited_isle, black = True, white = True).back ()
         .out (the_unnamable, black = True, white = True).back ()
         .out (river_docks, black = True, white = True).back ())

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
            Investigator (self,
                "\"Ashcan\" Pete", 4, 6, 1, 3,
                self.mod_statset.Statset (4,
                                          3, 6, 5,
                                          5, 3, 3),
                river_docks
            )
        )

        class ElderThing (arkham.SimpleMonster):
            def __init__ (self):
                arkham.SimpleMonster.__init__ \
                    (self, "Elder Thing",
                     -2, (-3, 2), 2, (+0, 1))
        @fight.combat_check_fail_hook.match (fun.any, fun.any, fun.matchclass (ElderThing))
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
                     arkham.pass_check, None,
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
        @fight.combat_check_pass_hook.match (fun.any, fun.any, fun.matchclass (MiGo))
        def do (game, investigator, monster):
            print """XXX If you pass a Combat check against Migo,
            return it to the box and draw 1 Unique Item."""
            raise fight.EndCombat ()


        class Nightgaunt (arkham.BasicMonster):
            def __init__ (self):
                class Damage (arkham.Damage):
                    def deal (self, game, investigator, monster):
                        print """XXX you are drawn through the nearest
                        open gate. If two or more gates are the same
                        distance from you, you choose which gate you
                        are drawn through."""
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
        class TheBlackMan (arkham.Monster):
            def __init__ (self):
                arkham.Monster.__init__ \
                    (self, "The Black Man",
                     in_cup = False,
                     mask = True,
                     endless = True)
            def evade_check (self):
                return arkham.evade_check (-3)

        @fight.fight_hook.match (fun.any, fun.any, fun.matchclass (TheBlackMan))
        def do (game, investigator, monster):
            if not arkham.SkillCheck ("luck", -1).check (game, investigator):
                investigator.devour (game, monster)
            else:
                investigator.gain_clues (2)
            raise fight.EndCombat ()

        @fight.deal_combat_damage_hook.match (fun.any, fun.any, fun.matchclass (TheBlackMan))
        def do (game, investigator, monster):
            pass


        class TheBloatedWoman (arkham.SimpleMonster):
            def __init__ (self):
                arkham.SimpleMonster.__init__ \
                    (self, "The Bloated Woman",
                     -1, (-1, 2), 2, (-2, 2),
                     in_cup = False,
                     mask = True,
                     endless = True)

        @fight.fight_hook.match (fun.any, fun.any, fun.matchclass (TheBloatedWoman))
        def do (game, investigator, monster):
            """Before making a Horror check, pass a Will(-2) check or
            or automatically fail the Horror check and the Combat check."""
            if not arkham.SkillCheck ("will", -2).check (game, investigator):
                fight.horror_check_fail_hook (game, investigator, monster)
                fight.combat_check_fail_hook (game, investigator, monster)
                fight.combat_loop_hook (game, investigator, monster)
            else:
                fight.normal_fight_hook (game, investigator, monster)


        for count, monster in [
            (3, arkham.SimpleMonster ("Byakhee",
                                      -2, (-1, 1), 1, (+0, 2))),
            (2, arkham.SimpleMonster ("Chthonian",
                                      +1, (-2, 2), 3, (-3, 3))),
            (6, arkham.BasicMonster ("Cultist",
                                     arkham.evade_check (-3),
                                     arkham.pass_check, None,
                                     arkham.combat_check (+1, 1),
                                     arkham.DamageStamina (1))),
            (3, arkham.SimpleMonster ("Dark Young",
                                      -2, (+0, 3), 3, (-1, 3),
                                      physical = "resistance",
                                      nightmarish = 1)),
            (1, arkham.SimpleMonster ("Dhole",
                                      -1, (-1, 4), 3, (-3, 4),
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
                                     arkham.pass_check, None,
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
                                     arkham.pass_check, None,
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
                         if monster.attributes.flag ("mask")]

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
            place = None
            for location in game.all_locations ():
                if location.attributes.flag (flag):
                    place = location
                    break

            assert place != None

            for location in game.all_locations ():
                if location.attributes.flag ("street") and location != place:
                    (maps.draw_from (place)
                     .to (location,
                          white = True, black = True,
                          no_investigator = True)
                     # does it also lead back?
                     #.back (no_investigator = True)
                     )

            return place

        append_special_place ("sky")
        self.lost_in_time_and_space_place \
            = append_special_place ("lost_in_time_and_space")

    def before_turn_0 (self, game):
        for location in game.all_locations ():
            if location.attributes.flag ("unstable"):
                location.add_clue_tokens (1)
