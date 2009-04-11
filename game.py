import arkham
from loc import *

class EndGame (Exception):
    pass

class EndPhase (Exception):
    pass

class ModuleInstance:
    def __init__ (self, game, type):
        self.m_game = game
        self.m_type = type

    def game (self):
        return self.m_game

    def name (self):
        return self.m_type.name ()

    # Game construction phases.
    def construct (self):
        return self.m_type.construct (self.m_game)

    def post_construct (self):
        return self.m_type.post_construct (self.m_game)

    def before_turn_0 (self):
        return self.m_type.before_turn_0 (self.m_game)

    def turn_0 (self):
        return self.m_type.turn_0 (self.m_game)

    # Game play phases.
    def upkeep (self):
        return self.m_type.upkeep (self.m_game)

    def movement (self):
        return self.m_type.movement (self.m_game)

    def encounters (self):
        return self.m_type.encounters (self.m_game)

    def mythos (self):
        return self.m_type.mythos (self.m_game)

    # Combat phases.
    def pre_combat (self, combat, investigator, monster):
        return self.m_type.pre_combat (combat, investigator, monster)

    def combat_turn (self, combat, investigator, monster):
        return self.m_type.combat_turn (combat, investigator, monster)

    # Unconscious/Insane actions.
    def investigator_unconscious (self):
        return self.m_type.investigator_unconscious (self.m_game)

    def investigator_insane (self):
        return self.m_type.investigator_insane (self.m_game)

class Monster (ObjectWithLocation):
    def __init__ (self, proto):
        ObjectWithLocation.__init__ (self, None)
        self.m_proto = proto

    def name (self):
        return self.m_proto.name ()

    def movement (self, game):
        return self.m_proto.movement (game)

    def pre_combat (self, combat, investigator):
        return self.m_proto.pre_combat (combat, investigator)

    def combat_turn (self, combat, investigator):
        return self.m_proto.combat_turn (combat, investigator)

    def proto (self):
        return self.m_proto

    def attributes (self):
        return self.m_proto.attributes ()

    def discard (self):
        return self.m_proto.discard ()

class Item:
    def __init__ (self, proto):
        self.m_proto = proto
        self.m_exhausted = False

    def name (self):
        return self.m_proto.name ()

    def proto (self):
        return self.m_proto

    def attributes (self):
        return self.m_proto.attributes ()

    def hands (self):
        return self.m_proto.hands ()

    def exhausted (self):
        return self.m_exhausted

    def exhaust (self):
        assert not self.m_exhausted
        self.m_exhausted = True

    def discard (self):
        return self.m_proto.discard ()

    # Game phases
    def upkeep (self, game, owner):
        self.m_exhausted = False
        return self.m_proto.upkeep (game, owner, self)

    def movement (self, game, owner):
        return self.m_proto.movement (game, owner, self)

class Game:
    def __init__ (self, modules, ui):
        self.m_modules = [ModuleInstance (self, mod) for mod in modules]
        self.m_ui = ui

        self.m_neighborhoods = []
        self.m_locations = []

        self.m_all_investigators = set () # All known investigators.
        self.m_investigators = [] # Active investigators.

        self.m_decks = {}

        # Monsters in play
        self.m_loc_monsters = {} # location->monster
        self.m_monsters_extra = [] # ancient ones, heralds, etc.

        # Keeps track of which investigator dealt with monsters in
        # which location, so as to avoid double deal_with (first time
        # around as a result of leave_location, second as a result of
        # being in a location with monsters when the turn ends.)
        self.m_dealt_with = None

        if len (modules) == 0:
            raise RuntimeError ("No modules to play with!")

        assert self.m_ui != None

    def add_neighborhood (self, neighborhood):
        assert neighborhood not in self.m_neighborhoods
        self.m_neighborhoods.append (neighborhood)

    def all_neighborhoods (self):
        return list (self.m_neighborhoods)

    def add_location (self, location):
        assert location not in self.m_locations
        self.m_locations.append (location)

    def all_locations (self):
        return list (self.m_locations)

    def all_investigators (self):
        # Return a copy of internal list of all investigators.
        return list (self.m_all_investigators)

    def add_deck (self, deck_class):
        assert deck_class not in self.m_decks
        deck = deck_class ()
        print "adding deck", deck.name (), deck
        self.m_decks[deck_class] = deck

    def deck (self, deck_class):
        return self.m_decks[deck_class]

    def investigators (self):
        # Return a copy of internal list of used investigator.
        return list (self.m_investigators)

    def add_investigator (self, investigator):
        self.m_all_investigators.add (investigator)

    def use_investigator (self, it):
        assert it in self.m_all_investigators
        self.m_investigators.append (it)
        print "%s playing" % it.name ()

    def drop_investigator (self, investigator):
        del self.m_investigators[self.m_investigators.index (investigator)]
        if self.m_investigators == []:
            raise EndGame ()

    def add_extra_board_monster (self, monster):
        print "%s is extra board monster" % monster.name ()
        self.m_monsters_extra.append (monster)

    def add_monster (self, monster, location):
        assert monster.proto () != None # make sure we got an instance
        if location not in self.m_loc_monsters:
            self.m_loc_monsters[location] = []
        print "%s appears at %s" % (monster.proto ().name (), location.name ())
        self.m_loc_monsters[location].append (monster)
        monster.move_to (location)

    def remove_monster (self, monster):
        location = monster.location ()
        assert location in self.m_loc_monsters
        print "%s removed from %s" % (monster.name (), location.name ())
        monsters = self.m_loc_monsters[location]
        assert monster in monsters
        del monsters[monsters.index (monster)]
        monster.move_to (None)

    def monsters_at (self, location):
        if location not in self.m_loc_monsters:
            return []
        else:
            return list (self.m_loc_monsters[location])

    def setup_game (self):
        print "-- setting up the game --"
        for modi in self.m_modules:
            print "call construct in %s" % modi.name ()
            modi.construct ()
        if len (self.m_all_investigators) == 0:
            raise RuntimeError ("No Investigator's to play with!")

        for modi in self.m_modules:
            modi.post_construct ()

        self.m_ui.setup_players (self)
        if len (self.m_investigators) == 0:
            raise RuntimeError ("No Investigator's selected!")

        print "player 1 is %s" % self.m_investigators[0].name ()

        for modi in self.m_modules:
            modi.before_turn_0 ()

        for investigator in self.m_investigators:
            investigator.prepare_pass_1 (self)

        for investigator in self.m_investigators:
            investigator.prepare_pass_2 (self)

        for investigator in self.m_investigators:
            self.m_ui.setup_investigator (self, investigator)

        for modi in self.m_modules:
            modi.turn_0 ()

        print "-- entering the game loop --"
        try:
            while True:
                print
                print
                print
                print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                print "+                                                       +"
                print "+ NEW TURN                                              +"
                print "+                                                       +"
                print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                print
                # This phase is not in the original game, but I figure
                # it might be handy if something needs to be done
                # before the first module fires its upkeep.
                for investigator in self.m_investigators:
                    self.perform_selected_action \
                        (investigator, investigator.turn_start (self))

                print "-- upkeep --"
                actions = sum ((modi.upkeep ()
                                for modi in self.m_modules), [])
                for investigator in self.m_investigators:
                    self.perform_selected_action \
                        (investigator, actions + investigator.upkeep (self))

                print "-- movement --"

                self.m_dealt_with = set ()
                actions = sum ((modi.movement ()
                                for modi in self.m_modules), [])
                for investigator in self.m_investigators:
                    try:
                        while True:
                            if not self.perform_selected_action \
                                    (investigator,
                                     actions + investigator.movement (self)):
                                break
                    except EndPhase:
                        pass

                    if (investigator, investigator.location ()) \
                            not in self.m_dealt_with:
                        print "need to deal with monsters"
                        self.deal_with_monsters (investigator)
                        print "dealt with monsters"
                    else:
                        print "skipping second dealing with monsters"

                # XXX This brings the disctinction between "arkham"
                # and "other-world" location into the core.  Currently
                # don't mind, but may need to revamp the loop later.
                def in_arkham (inv):
                    if not inv.location ().attributes ().flag ("other_world"):
                        return 1
                    else:
                        return 0
                investigators = list (self.m_investigators)
                investigators.sort (cmp = lambda x, y: \
                                        in_arkham (x) - in_arkham (y))

                print "-- encounters --"
                actions = sum ((modi.encounters ()
                                for modi in self.m_modules), [])
                for investigator in investigators:
                    self.perform_selected_action \
                        (investigator, actions + investigator.encounters (self))

                print "-- mythos --"
                actions = sum ((modi.mythos ()
                                for modi in self.m_modules), [])
                for investigator in self.m_investigators:
                    self.perform_selected_action \
                        (investigator, actions + investigator.mythos (self))

        except EndGame:
            pass

    def perform_selected_action (self, investigator, actions):
        if actions:
            assert len (actions) > 0
            if len (actions) == 1:
                action = actions[0]
                print "(choosing the only available action, %s)" % action.name ()
            else:
                action = self.m_ui.select_action (self, investigator, actions)
            action.perform (self, investigator)
            return action
        else:
            return None

    def pre_combat (self, combat, investigator, monster):
        print "-- pre_combat --"
        actions = []
        actions.extend (investigator.pre_combat (combat, monster))
        actions.extend (monster.pre_combat (combat, investigator))
        actions.extend (sum ((modi.pre_combat (combat, investigator, monster)
                              for modi in self.m_modules), []))
        self.perform_selected_action (investigator, actions)

    def combat_turn (self, combat, investigator, monster):
        print "-- combat_turn --"
        actions = []
        actions.extend (investigator.combat_turn (combat, monster))
        actions.extend (monster.combat_turn (combat, investigator))
        actions.extend (sum ((modi.combat_turn (combat, investigator, monster)
                              for modi in self.m_modules), []))
        self.perform_selected_action (investigator, actions)

    def investigator_unconscious (self, investigator):
        print "-- investigator_unconscious --"
        actions = []
        actions.extend (investigator.investigator_unconscious (self))
        actions.extend (sum ((modi.investigator_unconscious ()
                              for modi in self.m_modules), []))
        self.perform_selected_action (investigator, actions)

    def investigator_insane (self, investigator):
        print "-- investigator_insane --"
        actions = []
        actions.extend (investigator.investigator_insane (self))
        actions.extend (sum ((modi.investigator_insane ()
                              for modi in self.m_modules), []))
        self.perform_selected_action (investigator, actions)

    def investigator_unconscious_insane (self, investigator):
        return self.devour (investigator)

    def fight (self, investigator, monster):
        combat = arkham.Combat (self)
        print "game.fight"
        try:
            try:
                while True:
                    # Several actions can be performed before the
                    # combat ensues.
                    combat.check_ends (investigator, monster)
                    self.pre_combat (combat, investigator, monster)

            except arkham.ContinueCombat:
                investigator.lose_movement_points ()
                combat.check_ends (investigator, monster)
                arkham.fight_hook (combat, investigator, monster)
                assert False

        except arkham.EndCombat, e:
            succ = e.success ()
            if succ == None:
                pass
            elif succ:
                arkham.combat_won_hook (combat, investigator, monster)
            else:
                arkham.combat_lost_hook (combat, investigator, monster)

    def move_monster (self, monster, location):
        if location not in self.m_loc_monsters:
            self.m_loc_monsters[location] = []
        self.m_loc_monsters[location].append (monster)
        monster.move_to (location)

    def move_investigator (self, investigator, location):
        if self.leave_location (investigator):
            investigator.move_to (location)
            self.enter_location (investigator)

    def deal_with_monsters (self, investigator):
        monsters = set ()
        actions = set ()
        monster_actions = {}
        location = investigator.location ()

        while investigator.alive ():
            if location != investigator.location ():
                # XXX needs clarification: if monster e.g. sends the
                # investigator through the nearest open gate (or
                # otherwise changes his location), does that mean that
                # the investigator still needs to deal with other
                # monsters in that location?
                break

            n_monsters = set (self.monsters_at (location))
            d_monsters = monsters.difference (n_monsters) # recently dropped
            i_monsters = monsters.union (n_monsters) - monsters # recently introduced
            monsters.update (i_monsters)

            for monster in i_monsters:
                action = GameplayAction_DealWithMonster (monster)
                monster_actions[monster] = action
                actions.add (action)

            for monster in d_monsters:
                action = monster_actions[monster]
                if action in actions:
                    actions.remove (action)

            action = self.perform_selected_action (investigator, list (actions))
            if action == None:
                break
            actions.remove (action)

        self.m_dealt_with.add ((investigator, location))
        print "deal_with_monsters finished"

    # Retur False if investigator can't leave the location.
    def leave_location (self, investigator):
        location = investigator.location ()
        print "%s attempts to leave %s" % (investigator.name (), location.name ())
        self.deal_with_monsters (investigator)
        ret = investigator.alive () and investigator.movement_points () > 0
        if not ret:
            print "%s can't leave %s" % (investigator.name (), location.name ())
        return ret

    def enter_location (self, investigator):
        print "%s entered %s" % (investigator.name (), investigator.location ().name ())
        self.m_dealt_with = set ()

    def environment (self):
        # XXX Haunter Of The Dark currently asks for that, but that
        # binds environment cards too tightly into the system.  Need
        # to come up with better solution.
        return None

    def devour (self, investigator):
        # XXX not implemented
        print "NYI: %s should be devoured" % investigator.name ()

from monster import *
from actions import *
