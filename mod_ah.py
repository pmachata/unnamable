import arkham
import maps
import fun

def find_location (game, flag):
    for location in game.all_locations ():
        if location.attributes ().flag (flag):
            return location
    return None

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
        common = mod_index.request ("common")

        success = ancient and monster and skills and terror and common
        if not success:
            ancient = None
            monster = None
            skills = None
            terror = None
            common = None

        self.mod_ancient = ancient
        self.mod_monster = monster
        self.mod_skills = skills
        self.mod_terror = terror
        self.mod_common = common

        return not not success

    def construct (self, game):

        self.m_monster_cup = game.deck (self.mod_monster.MonsterCup)
        self.m_common_deck = game.deck (self.mod_common.CommonDeck)

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

        import mod_ah_monsters
        mod_ah_monsters.build (game, self)

        import mod_ah_items
        mod_ah_items.build (game, self)

        # xxx Some of these will have special skills, and it will be
        # necessary to expand the definition.  For now, this condensed
        # form suffices.
        Ancient = self.mod_ancient.Ancient
        def ancient (name):
            class AH_Ancient (Ancient):
                def __init__ (self):
                    Ancient.__init__ (self, name)
            return AH_Ancient

        def Nyarlathotep (monster_cup):
            class Nyarlathotep (Ancient):
                def __init__ (self):
                    Ancient.__init__ (self, "Nyarlathotep")

                def before_turn_0 (self, game):
                    import random
                    masks = [monster
                             for monster in monster_cup.registered_cards ()
                             if monster.attributes ().flag ("mask")]

                    for mask in random.sample (masks, 5):
                        monster_cup.activate (mask)

                def before_battle (self, game):
                    # Any investigator with no Clue tokens is devoured.
                    for investigator in game.investigators ():
                        if investigator.clues () == 0:
                            investigator.devour (game, self)

            return Nyarlathotep

        for ancient in [ancient ("Azathoth"),
                        ancient ("Cthulhu"),
                        Nyarlathotep (self.m_monster_cup)]:
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

        if True:
            game.add_monster (self.m_monster_cup.draw \
                                  (lambda arg: arg.name () == "Maniac"),
                              loc)

    def mythos (self, game):
        # XXX For now just put new monster somewhere.  It may turn out
        # to be in "lost in time and space", but we don't care, it's
        # just a temporary solution.
        import random
        print "; ".join (mon.name () for mon in self.m_monster_cup.cards ())
        game.add_monster \
            (self.m_monster_cup.draw (),
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
