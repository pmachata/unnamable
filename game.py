import fun
import arkham
import fight_hooks
import check_hooks
import damage_hooks

class EndGame (Exception):
    pass

class EndPhase (Exception):
    pass

def with_proto (pred):
    def match (arg):
        return pred (arg.proto ())
    return match

def match_proto (cls):
    return with_proto (fun.matchclass (cls))


class Game (fight_hooks.FightHooks, check_hooks.CheckHooks,
            damage_hooks.DamageHooks):
    def __init__ (self, modules, ui):
        fight_hooks.FightHooks.__init__ (self)
        check_hooks.CheckHooks.__init__ (self, Game)
        damage_hooks.DamageHooks.__init__ (self, Game)

        if len (modules) == 0:
            raise RuntimeError ("No modules to play with!")

        assert ui is not None

        self.m_modules = [arkham.Module (self, mod) for mod in modules]
        self.m_ui = ui
        self.m_turn = 0

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

        # Per-turn callbacks.  lambda -> how many times (0 for endless)
        self.m_per_turn = {}

    def turn_number (self):
        return self.m_turn

    def register_per_turn (self, callback, how_many_times = 0):
        """ how_many_times == 0 means endless """
        self.m_per_turn[callback] = how_many_times

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

    def deck_matching (self, matcher):
        matching = [deck for mod, deck in self.m_decks.iteritems ()
                    if matcher (deck)]
        assert len (matching) == 1, "%d matching, 1 expected" % len (matching)
        return matching[0]

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

    def run (self):
        print "-- setting up the game --"
        for mod in self.m_modules:
            print "call construct in %s" % mod.name ()
            mod.construct ()
        if len (self.m_all_investigators) == 0:
            raise RuntimeError ("No Investigator's to play with!")

        for mod in self.m_modules:
            mod.post_construct ()

        self.m_ui.setup_players (self)
        if len (self.m_investigators) == 0:
            raise RuntimeError ("No Investigator's selected!")

        print "player 1 is %s" % self.m_investigators[0].name ()

        for mod in self.m_modules:
            mod.before_turn_0 ()

        for investigator in self.m_investigators:
            investigator.prepare_pass_1 (self)

        for investigator in self.m_investigators:
            investigator.prepare_pass_2 (self)

        for mod in self.m_modules:
            mod.turn_0 ()

        print "-- entering the game loop --"
        try:
            while True:
                self.m_turn += 1
                print
                print
                print
                print "++++++++++++++++++++++++++++++++++++++++++++++++++++"
                print "+                                                  +"
                print "+ TURN %-9d                                   +" % self.m_turn
                print "+                                                  +"
                print "++++++++++++++++++++++++++++++++++++++++++++++++++++"
                print
                # Do per-turn callbacks
                for callback, how_many_times in self.m_per_turn.items ():
                    callback (self)
                    if how_many_times == 1:
                        del self.m_per_turn[callback]
                    elif how_many_times != 0:
                        self.m_per_turn[callback] -= 1

                # This phase is not in the original game, but I figure
                # it might be handy if something needs to be done
                # before the first module fires its upkeep.
                for investigator in self.m_investigators:
                    self.perform_selected_action \
                        (investigator, investigator.turn_start (self))

                print "-- upkeep --"
                for mod in self.m_modules:
                    if mod.upkeep_1 () != None:
                        raise AssertionError \
                            ("upkeep_1 is not supposed to return anything")

                for investigator in self.m_investigators:
                    if investigator.upkeep_1 (self) != None:
                        raise AssertionError \
                            ("upkeep_1 is not supposed to return anything")

                self.game_phase_with_actions ("upkeep_2")
                self.game_phase_with_actions ("upkeep_3")

                # Movement is complex, we can't simply dispatch to
                # game_phase_with_actions.
                print "-- movement --"

                self.m_dealt_with = set ()
                actions = sum ((mod.movement ()
                                for mod in self.m_modules), [])
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
                        self.deal_with_monsters (investigator)
                    else:
                        print "skipping second dealing with monsters"

                self.game_phase_with_actions ("encounters_1")
                self.game_phase_with_actions ("encounters_2")
                self.game_phase_with_actions ("mythos")

        except EndGame:
            pass

    def game_phase_with_actions (self, phase_name):
        print "-- %s --" % phase_name

        mod_actions = sum ((getattr (mod, phase_name) ()
                            for mod in self.m_modules), [])

        for investigator in self.m_investigators:
            try:
                while True:
                    actions = (mod_actions
                               + getattr (investigator, phase_name) (self))
                    if len (actions) == 0:
                        break
                    actions.append \
                        (arkham.GameplayAction_DoNothing ())
                    self.perform_selected_action \
                        (investigator, actions)

            except EndPhase:
                pass

    def perform_selected_action (self, investigator, actions):
        if actions:
            assert len (actions) > 0
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
        actions.extend (sum ((mod.pre_combat (combat, investigator, monster)
                              for mod in self.m_modules), []))
        self.perform_selected_action (investigator, actions)

    def combat_turn (self, combat, investigator, monster):
        print "-- combat_turn --"
        actions = []
        actions.extend (investigator.combat_turn (combat, monster))
        actions.extend (monster.combat_turn (combat, investigator))
        actions.extend (sum ((mod.combat_turn (combat, investigator, monster)
                              for mod in self.m_modules), []))
        self.perform_selected_action (investigator, actions)

    def investigator_dead (self, investigator):
        if investigator.should_be_devoured (self):
            self.devour (investigator)
        else:
            print "-- investigator_dead --"
            actions = []
            actions.extend (investigator.investigator_dead (self))
            actions.extend (sum ((mod.investigator_dead (investigator)
                                  for mod in self.m_modules), []))
            self.perform_selected_action (investigator, actions)

    def fight (self, investigator, monster):
        combat = arkham.Combat (self)
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
                self.fight_hook (combat, investigator, monster)
                assert False

        except arkham.EndCombat, e:
            succ = e.success ()
            if succ == None:
                pass
            elif succ:
                self.combat_won_hook (combat, investigator, monster)
            else:
                self.combat_lost_hook (combat, investigator, monster)

        combat.end ()

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

            # recently dropped
            d_monsters = monsters.difference (n_monsters)

            # recently introduced
            i_monsters = monsters.union (n_monsters) - monsters

            monsters.update (i_monsters)

            for monster in i_monsters:
                action = arkham.GameplayAction_DealWithMonster (monster)
                monster_actions[monster] = action
                actions.add (action)

            for monster in d_monsters:
                action = monster_actions[monster]
                if action in actions:
                    actions.remove (action)

            actions = list (actions) + investigator.deal_with (self)
            action = self.perform_selected_action (investigator, actions)
            if action == None:
                break
            actions.remove (action)

        self.m_dealt_with.add ((investigator, location))

    # Retur False if investigator can't leave the location.
    def leave_location (self, investigator):
        location = investigator.location ()
        print "%s attempts to leave %s" % (investigator.name (),
                                           location.name ())
        self.deal_with_monsters (investigator)
        ret = investigator.alive () and investigator.movement_points () > 0
        if not ret:
            print "%s can't leave %s" % (investigator.name (),
                                         location.name ())
        return ret

    def enter_location (self, investigator):
        print "%s entered %s" % (investigator.name (),
                                 investigator.location ().name ())
        self.m_dealt_with = set ()

    def environment (self):
        # XXX Haunter Of The Dark currently asks for that, but that
        # binds environment cards too tightly into the system.  Need
        # to come up with better solution.
        return None

    def devour (self, investigator):
        # XXX not implemented
        print "NYI: %s should be devoured" % investigator.name ()
