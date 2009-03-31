import fun

class EndGame (Exception):
    pass
class EndPhase (Exception):
    pass

# Whether we want hook traces.
trace = True

class Attributes:
    def __init__ (self):
        self.m_attributes = {}

    def set (self, name, value):
        if self.has (name):
            raise RuntimeError ("Attribute name collision")
        self.m_attributes[name] = value

    def has (self, name):
        return name in self.m_attributes

    def flag (self, name):
        if not self.has (name):
            return False
        else:
            ret = self.m_attributes[name]
            if ret != True and ret != False:
                raise RuntimeError ("Flag attribute not a boolean")
            return ret

    def get (self, name):
        if not self.has (name):
            return None
        else:
            return self.m_attributes[name]

    def fmt_flags (self):
        ret = []
        for attr, val in self.m_attributes.iteritems ():
            if val != True and val != False:
                ret.append ("%s=%s" % (attr, val))
            else:
                ret.append ("%s%s" % ("" if val else "not ",
                                      attr))
        return ";".join (ret)

def match_attribute (**kwargs):
    key, = kwargs.keys ()
    value, = kwargs.values ()
    def match (arg):
        if not arg.has (key):
            return False
        else:
            return arg.get (key) == value
    return match

def match_flag (flag):
    def match (arg):
        return arg.attributes ().flag (flag)
    return match

def get_flag (flag):
    def match (arg):
        return arg.attributes ().get (flag)
    return match

def cond_bind_attrib (attrib):
    import fun
    return fun.if_else (match_flag (attrib), get_flag (attrib))

class ObjectWithAttributes:
    def __init__ (self):
        self.m_attributes = Attributes ()

    def apply_attributes (self, dict):
        for k, v in dict.iteritems ():
            self.m_attributes.set (k, v)

    def attributes (self):
        return self.m_attributes

class Neighborhood (ObjectWithAttributes):
    def __init__ (self):
        ObjectWithAttributes.__init__ (self)

class Connection (ObjectWithAttributes):
    def __init__ (self, dest):
        ObjectWithAttributes.__init__ (self)
        self.m_dest = dest

    def dest (self):
        return self.m_dest

class Location (ObjectWithAttributes):
    def __init__ (self, name, neighborhood = None):
        ObjectWithAttributes.__init__ (self)
        self.m_name = name
        self.m_neighborhood = neighborhood
        self.m_connections = set ()
        self.m_clue_tokens = 0

    def add_connection (self, conn):
        assert conn not in self.m_connections
        self.m_connections.add (conn)

    def name (self):
        return self.m_name

    def add_clue_tokens (self, n):
        assert n >= 0
        self.m_clue_tokens += n

    def connections (self):
        return list (self.m_connections)

class ObjectWithLocation:
    def __init__ (self, initial_location):
        self.m_location = initial_location

    def location (self):
        return self.m_location

    def move_to (self, location):
        print "ObjectWithLocation.move_to %s->%s" % (self.name (), location.name () if location else "None")
        self.m_location = location


class GameplayAction:
    def __init__ (self, name):
        self.m_name = name

    def name (self):
        return self.m_name

    def perform (self, game, investigator):
        pass

    def bound_location (self):
        return None

    def bound_monster (self):
        return None

class LocationBoundGameplayAction (GameplayAction):
    def __init__ (self, location, name):
        GameplayAction.__init__ (self, name)
        self.m_location = location

    def bound_location (self):
        return self.m_location

class MonsterBoundGameplayAction (GameplayAction):
    def __init__ (self, monster, name):
        GameplayAction.__init__ (self, name)
        self.m_monster = monster

    def bound_monster (self):
        return self.m_monster

class GameplayAction_Move (LocationBoundGameplayAction):
    def __init__ (self, location):
        LocationBoundGameplayAction.__init__ (self, location, "move")

    def perform (self, game, investigator):
        game.move_investigator (investigator, self.m_location)
        if investigator.movement_points () > 0:
            # He might have lost all movement points during the fight
            # after he tried to leave the current location.
            investigator.spend_movement_point ()

class GameplayAction_Stay (LocationBoundGameplayAction):
    def __init__ (self, location):
        LocationBoundGameplayAction.__init__ (self, location, "stay put")

    def perform (self, game, investigator):
        investigator.lose_movement_points ()
        raise EndPhase ()

class GameplayAction_Quit (GameplayAction):
    def __init__ (self):
        GameplayAction.__init__ (self, "quit the game")

    def perform (self, game, investigator):
        game.drop_investigator (investigator)

class GameplayAction_Evade (MonsterBoundGameplayAction):
    def __init__ (self, combat, monster):
        MonsterBoundGameplayAction.__init__ (self, monster, "evade")
        self.m_combat = combat

class GameplayAction_Evade_PreCombat (GameplayAction_Evade):
    def __init__ (self, *args):
        GameplayAction_Evade.__init__ (self, *args)

    def perform (self, game, investigator):
        import fight
        monster = self.m_monster
        fight.evade_check_hook (self.m_combat, investigator, monster)
        investigator.lose_movement_points ()
        raise fight.ContinueCombat () # Proceed with the combat.

class GameplayAction_Evade_Combat (GameplayAction_Evade):
    def __init__ (self, *args):
        GameplayAction_Evade.__init__ (self, *args)

    def perform (self, game, investigator):
        import fight
        monster = self.m_monster
        fight.evade_check_hook (self.m_combat, investigator, monster)

class GameplayAction_Fight (MonsterBoundGameplayAction):
    def __init__ (self, monster):
        MonsterBoundGameplayAction.__init__ (self, monster, "fight")

    def perform (self, game, investigator):
        import fight
        raise fight.ContinueCombat ()

class GameplayAction_DealWithMonster (MonsterBoundGameplayAction):
    def __init__ (self, monster):
        MonsterBoundGameplayAction.__init__ (self, monster, "deal with")

    def perform (self, game, investigator):
        print "dealing with %s" % self.m_monster.name ()
        game.fight (investigator, self.m_monster)
        print "combat finished"


class GameplayObject:
    # Game play phases.
    def turn_start (self, game):
        return []
    def upkeep (self, game):
        return []
    def movement (self, game):
        return []
    def encounters (self, game):
        return []
    def mythos (self, game):
        return []

class Investigator (ObjectWithLocation, GameplayObject):
    def __init__ (self, name, sanity, stamina,
                  initial_money, initial_clues, skills, home):
        ObjectWithLocation.__init__ (self, home)
        self.m_name = name
        self.m_max_sanity = sanity
        self.m_sanity = sanity
        self.m_max_stamina = stamina
        self.m_stamina = stamina
        self.m_money = initial_money
        self.m_clues = initial_clues
        self.m_skills = skills
        self.m_movement_points = 0
        self.m_delayed = False
        self.m_trophies = []

    def name (self):
        return self.m_name

    def clues (self):
        return self.m_clues

    def gain_clues (self, clues):
        assert clues > 0
        self.m_clues += clues

    def sanity (self):
        return self.m_sanity

    def stamina (self):
        return self.m_stamina

    def reduce_sanity (self, amount):
        assert amount >= 0
        print "reduce sanity by %s" % amount,
        self.m_sanity -= amount
        if self.m_sanity < 0:
            self.m_sanity = 0
        print "to", self.m_sanity

    def add_sanity (self, amount):
        assert amount >= 0
        print "add %s to sanity" % amount,
        self.m_sanity += amount
        if self.m_sanity > self.m_max_sanity:
            self.m_sanity = self.m_max_sanity
        print "to", self.m_sanity

    def reduce_stamina (self, amount):
        assert amount >= 0
        print "reduce stamina by %s" % amount,
        self.m_stamina -= amount
        if self.m_stamina < 0:
            self.m_stamina = 0
        print "to", self.m_stamina

    def add_stamina (self, amount):
        assert amount >= 0
        print "add %s to stamina" % amount,
        self.m_stamina += amount
        if self.m_stamina > self.m_max_stamina:
            self.m_stamina = self.m_max_stamina
        print "to", self.m_stamina

    def spend_movement_point (self):
        assert self.m_movement_points > 0
        self.m_movement_points -= 1

    def lose_movement_points (self):
        self.m_movement_points = 0

    def movement_points (self):
        return self.m_movement_points

    def alive (self):
        return self.m_sanity > 0 and self.m_stamina > 0

    def delay (self):
        self.m_delayed = True

    def delayed (self):
        return self.m_delayed

    def perform_check (self, game, skill_name, modifier, difficulty):
        die = self.m_skills.check (skill_name) + modifier
        successes = sum (roll_dice_hook (game, self, skill_name)
                         for _ in xrange (die))
        # XXX spend clue tokens to gain advantage
        ret = successes >= difficulty
        print "check %s, %s/%s successes on %s die"\
            % ("passed" if ret else "failed",
               successes, difficulty, die)
        return ret

    def devour (self, game, monster):
        game.devour (self)

    def trophies (self):
        return list (self.m_trophies)

    def claim_trophy (self, monster):
        print "claiming trophy %s" % monster.name ()
        self.m_trophies.append (monster)

    # Game construction phases.  Phases are called in sequence.  Given
    # phase is called only after the previous phase was finished for
    # all investigators.
    def prepare_pass_1 (self, game):
        pass
    def prepare_pass_2 (self, game):
        pass

    # Game play phases.
    def upkeep (self, game):
        mp = self.m_skills.check ("speed")
        # XXX apply equipment and allies
        self.m_movement_points = mp
        return []

    def movement (self, game):
        if self.m_movement_points > 0:
            dest_actions = [GameplayAction_Move (location)
                            for location
                            in [conn.dest ()
                                for conn in self.location ().connections ()
                                if not conn.attributes ().flag ("no_investigator")]]
        else:
            dest_actions = []

        return [GameplayAction_Stay (self.m_location)] + dest_actions

    # Combat phases.
    def pre_combat (self, combat, monster):
        return [GameplayAction_Evade_PreCombat (combat, monster),
                GameplayAction_Fight (monster)]

    def combat_turn (self, combat, monster):
        return [GameplayAction_Evade_Combat (combat, monster),
                GameplayAction_Fight (monster)]

    # Unconscious/Insane actions.
    def investigator_unconscious (self, game):
        return []

    def investigator_insane (self, game):
        return []

class Damage:
    def deal (self, game, investigator, monster):
        raise NotImplementedError ()

    def description (self, game, investigator, monster):
        raise NotImplementedError ()

class DamageNone (Damage):
    def deal (self, game, investigator, monster):
        pass

    def description (self, game, investigator, monster):
        return "-"

class DamageSanity (Damage):
    def __init__ (self, amount):
        self.m_amount = amount

    def deal (self, game, investigator, monster):
        investigator.reduce_sanity (self.m_amount)

    def description (self, game, investigator, monster):
        return "sanity %+d" % -self.m_amount

class DamageStamina (Damage):
    def __init__ (self, amount):
        self.m_amount = amount

    def deal (self, game, investigator, monster):
        investigator.reduce_stamina (self.m_amount)

    def description (self, game, investigator, monster):
        return "stamina %+d" % -self.m_amount

class DamageDevour (Damage):
    def deal (self, game, investigator, monster):
        investigator.devour (game, monster)

    def description (self, game, investigator, monster):
        return "devour"

class ConditionalDamage (Damage):
    def __init__ (self, predicate, damage_pass, damage_fail = Damage ()):
        self.m_pred = predicate
        self.m_pass = damage_pass
        self.m_fail = damage_fail

    def deal (self, game, investigator, monster):
        if self.m_pred (game, investigator, monster):
            return self.m_pass.deal (game, investigator, monster)
        else:
            return self.m_fail.deal (game, investigator, monster)

    def description (self, game, investigator, monster):
        if self.m_pred (game, investigator, monster):
            return self.m_pass.description (game, investigator, monster)
        else:
            return self.m_fail.description (game, investigator, monster)

damage_none = DamageNone ()
damage_devour = DamageDevour ()

class Check:
    def check (self, game, investigator):
        raise NotImplementedError ()

    def description (self, game, investigator):
        raise NotImplementedError ()

class ConstCheck (Check):
    def __init__ (self, ret):
        self.m_ret = ret

    def check (self, game, investigator):
        return self.m_ret

    def description (self, game, investigator):
        if self.m_ret:
            return "pass"
        else:
            return "fail"

class SkillCheck (Check):
    def __init__ (self, skill_name, modifier, difficulty = 1):
        self.m_skill_name = skill_name
        self.m_modifier = modifier
        self.m_difficulty = difficulty
        assert difficulty >= 1

    def check (self, game, investigator):
        print "%s check:" % self.m_skill_name,
        return investigator.perform_check (game, self.m_skill_name,
                                           self.m_modifier, self.m_difficulty)

    def description (self, game, investigator):
        return "%s(%+d)%s" % (self.m_skill_name, self.m_modifier,
                               ("[%d]" % self.m_difficulty
                                if self.m_difficulty > 1 else ""))

class ConditionalCheck (Check):
    def __init__ (self, predicate, check_pass, check_fail = ConstCheck (False)):
        self.m_pred = predicate
        self.m_pass = check_pass
        self.m_fail = check_fail

    def check (self, game, investigator):
        if self.m_pred (game, investigator):
            return self.m_pass.check (game, investigator)
        else:
            return self.m_fail.check (game, investigator)

    def description (self, game, investigator):
        if self.m_pred (game, investigator):
            return self.m_pass.description (game, investigator)
        else:
            return self.m_fail.description (game, investigator)

pass_check = ConstCheck (True)
fail_check = ConstCheck (False)
def evade_check (awareness):
    return SkillCheck ("evade", awareness, 1)
def horror_check (rating):
    return SkillCheck ("horror", rating, 1)
def combat_check (rating, toughness):
    return SkillCheck ("combat", rating, toughness)

class MonsterProto (ObjectWithAttributes):
    def __init__ (self, name, **attributes):
        ObjectWithAttributes.__init__ (self)
        self.m_name = name
        self.apply_attributes (attributes)

    def name (self):
        return self.m_name

    # Override in subclass
    def movement (self, game):
        raise NotImplementedError ()

    # Combat phases.
    def pre_combat (self, combat, investigator):
        return []

    def combat_turn (self, combat, investigator):
        return []

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

class BasicMonster (MonsterProto):
    def __init__ (self, name,
                  evade_check,
                  horror_check, horror_damage,
                  combat_check, combat_damage,
                  **attributes):
        MonsterProto.__init__ (self, name, **attributes)
        self.m_evade_check = evade_check
        self.m_horror_check = horror_check
        self.m_horror_damage = horror_damage
        self.m_combat_check = combat_check
        self.m_combat_damage = combat_damage

    def evade_check (self):
        return self.m_evade_check

    def horror_check (self):
        return self.m_horror_check

    def combat_check (self):
        return self.m_combat_check

    def horror_damage (self):
        return self.m_horror_damage

    def combat_damage (self):
        return self.m_combat_damage

class SimpleMonster (BasicMonster):
    def __init__ (self, name,
                  awareness,
                  (horror_rating, horror_damage),
                  toughness,
                  (combat_rating, combat_damage),
                  **attributes):
        BasicMonster.__init__ (self, name,
                               evade_check (awareness),
                               horror_check (horror_rating),
                               DamageSanity (horror_damage),
                               combat_check (combat_rating, toughness),
                               DamageStamina (combat_damage),
                               **attributes)

class ModuleIndex:
    def __init__ (self):
        self.m_module_idx = {}
        self.m_modules = {}

    def add_module (self, module):
        self.m_module_idx[module.signature ()] = module
        self.m_modules[module] = False

    def request (self, signature):
        # XXX this will cause all sorts of endless loops.  Need some
        # sort of dependency resolver.  Or something else to inhibit
        # the endless recursion.
        if signature not in self.m_module_idx:
            # Don't know module called that.
            return None

        module = self.m_module_idx[signature]
        if self.m_modules[module]:
            # Already got it.
            return module

        self.m_modules[module] = True
        if not module.consistent (self):
            self.m_modules[module] = False
            return None

        print "included %s" % signature
        return module

    def has_module (self, signature):
        module = self.m_module_idx[signature]
        if module == None:
            return False
        else:
            return self.m_modules[module]

    def requested_modules (self):
        return [mod for mod, on in self.m_modules.iteritems () if on]

class Module:
    def __init__ (self, signature, name):
        self.m_signature = signature
        self.m_name = name

    def signature (self):
        return self.m_signature

    def name (self):
        return self.m_name

    # Check consistency constraints of the module.
    def consistent (self, mod_index):
        return False

    # Game construction phases.
    def construct (self, game):
        pass

    def post_construct (self, game):
        pass

    def before_turn_0 (self, game):
        # Note: investigators are initialized by now.
        pass

    def turn_0 (self, game):
        pass

    # Game play phases.
    def upkeep (self, game):
        return []

    def movement (self, game):
        return []

    def encounters (self, game):
        return []

    def mythos (self, game):
        return []

    # Combat phases.
    def pre_combat (self, combat, investigator, monster):
        return []

    def combat_turn (self, combat, investigator, monster):
        return []

    # Unconscious/Insane actions.
    def investigator_unconscious (self, game):
        return []

    def investigator_insane (self, game):
        return []

class ModuleInstance:

    def __init__ (self, game, type):
        self.m_game = game
        self.m_type = type

    def game (self):
        return self.m_game

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

class UI:
    def setup_players (self, game):
        raise NotImplementedError ()

    def setup_investigator (self, game, investigator):
        raise NotImplementedError ()

class TrackEvent:
    def event (self, game, owner, level):
        pass

class ConditionalEvent (TrackEvent):
    def __init__ (self, predicate, event_pass, event_fail = TrackEvent ()):
        self.m_pred = predicate
        self.m_pass = event_pass
        self.m_fail = event_fail
    def event (self, game, owner, level):
        if self.m_pred (game, owner, level):
            return self.m_pass.event (game, owner, level)
        else:
            return self.m_fail.event (game, owner, level)

class Track:
    def __init__ (self, owner):
        self.m_level = 0
        self.m_owner = owner
        self.m_events = []

    def add_event (self, event):
        self.m_events.append (event)

    def advance (self, game):
        self.m_level += 1
        for event in self.m_events:
            event.event (game, self.m_owner, self.m_level)

    def level (self):
        return self.m_level

class Game:
    def __init__ (self, modules, ui):
        self.m_modis = [ModuleInstance (self, mod) for mod in modules]
        self.m_ui = ui

        self.m_neighborhoods = []
        self.m_locations = []

        self.m_all_investigators = set () # All known investigators.
        self.m_investigators = [] # Active investigators.

        # Containers for inactive monsters
        self.m_registered_monsters = {} # monster->count
        self.m_monster_cup = []

        # Active monsters
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

    def register_monster (self, monster, count):
        if monster not in self.m_registered_monsters:
            self.m_registered_monsters[monster] = 0
        self.m_registered_monsters[monster] += count

    def registered_monsters (self):
        return sum (([monster] * count
                     for monster, count in self.m_registered_monsters.iteritems ()),
                    [])

    def put_monster_in_cup (self, monster):
        assert monster in self.m_registered_monsters
        count = self.m_registered_monsters[monster]
        count -= 1
        if count == 0:
            del self.m_registered_monsters[monster]
        else:
            self.m_registered_monsters[monster] = count
        self.m_monster_cup.append (monster)

    def return_monster_in_cup (self, monster):
        self.m_monster_cup.append (monster)

    def monster_cup (self):
        return list (self.m_monster_cup)

    def monster_from_cup (self, monster_proto, location):
        # XXX ugly linear lookup
        assert monster_proto in self.m_monster_cup
        del self.m_monster_cup[self.m_monster_cup.index (monster_proto)]

        if location not in self.m_loc_monsters:
            self.m_loc_monsters[location] = []
        print "%s appears at %s" % (monster_proto.name (), location.name ())
        monster = Monster (monster_proto)
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
        for modi in self.m_modis:
            modi.construct ()
        if len (self.m_all_investigators) == 0:
            raise RuntimeError ("No Investigator's to play with!")

        for modi in self.m_modis:
            modi.post_construct ()

        self.m_ui.setup_players (self)
        if len (self.m_investigators) == 0:
            raise RuntimeError ("No Investigator's selected!")

        print "player 1 is %s" % self.m_investigators[0].name ()

        for modi in self.m_modis:
            modi.before_turn_0 ()

        for investigator in self.m_investigators:
            investigator.prepare_pass_1 (self)

        for investigator in self.m_investigators:
            investigator.prepare_pass_2 (self)

        for investigator in self.m_investigators:
            self.m_ui.setup_investigator (self, investigator)

        for modi in self.m_modis:
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
                                for modi in self.m_modis), [])
                for investigator in self.m_investigators:
                    self.perform_selected_action \
                        (investigator, actions + investigator.upkeep (self))

                print "-- movement --"

                self.m_dealt_with = set ()
                actions = sum ((modi.movement ()
                                for modi in self.m_modis), [])
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
                                for modi in self.m_modis), [])
                for investigator in investigators:
                    self.perform_selected_action \
                        (investigator, actions + investigator.encounters (self))

                print "-- mythos --"
                actions = sum ((modi.mythos ()
                                for modi in self.m_modis), [])
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
                              for modi in self.m_modis), []))
        self.perform_selected_action (investigator, actions)

    def combat_turn (self, combat, investigator, monster):
        print "-- combat_turn --"
        actions = []
        actions.extend (investigator.combat_turn (combat, monster))
        actions.extend (monster.combat_turn (combat, investigator))
        actions.extend (sum ((modi.combat_turn (combat, investigator, monster)
                              for modi in self.m_modis), []))
        self.perform_selected_action (investigator, actions)

    def investigator_unconscious (self, investigator):
        print "-- investigator_unconscious --"
        actions = []
        actions.extend (investigator.investigator_unconscious (self))
        actions.extend (sum ((modi.investigator_unconscious ()
                              for modi in self.m_modis), []))
        self.perform_selected_action (investigator, actions)

    def investigator_insane (self, investigator):
        print "-- investigator_insane --"
        actions = []
        actions.extend (investigator.investigator_insane (self))
        actions.extend (sum ((modi.investigator_insane ()
                              for modi in self.m_modis), []))
        self.perform_selected_action (investigator, actions)

    def investigator_unconscious_insane (self, investigator):
        return self.devour (investigator)

    def fight (self, investigator, monster):
        import fight
        combat = fight.Combat (self)
        print "game.fight"
        try:
            try:
                while True:
                    # Several actions can be performed before the
                    # combat ensues.
                    combat.check_ends (investigator, monster)
                    self.pre_combat (combat, investigator, monster)

            except fight.ContinueCombat:
                investigator.lose_movement_points ()
                combat.check_ends (investigator, monster)
                fight.fight_hook (combat, investigator, monster)
                print "AFTER FIGHT HOOK"

        except fight.EndCombat, e:
            succ = e.success ()
            if succ == None:
                pass
            elif succ:
                fight.combat_won_hook (combat, investigator, monster)
            else:
                fight.combat_lost_hook (combat, investigator, monster)

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
        import fight
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

roll_dice_hook = fun.Function (Game, Investigator, object)
dice_roll_successful_hook = fun.Function (Game, Investigator, object, int)

@roll_dice_hook.match (fun.any, fun.any, fun.any)
def do (game, investigator, skill):
    import random
    return dice_roll_successful_hook (game, investigator, skill,
                                      random.randint (1, 6))

@dice_roll_successful_hook.match (fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, skill, roll):
    return roll >= 5
