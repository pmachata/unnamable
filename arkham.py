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
        return arg.attributes.flag (flag)
    return match

def get_flag (flag):
    def match (arg):
        return arg.attributes.get (flag)
    return match

def cond_bind_attrib (attrib):
    import fun
    return fun.if_else (match_flag (attrib), get_flag (attrib))

class ObjectWithAttributes:
    def __init__ (self):
        self.attributes = Attributes ()

    def apply_attributes (self, dict):
        for k, v in dict.iteritems ():
            self.attributes.set (k, v)

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

class Investigator:
    def __init__ (self, name, sanity, stamina,
                  initial_money, initial_clues, statset, home):
        self.m_name = name
        self.m_max_sanity = sanity
        self.m_sanity = sanity
        self.m_max_stamina = stamina
        self.m_stamina = stamina
        self.m_money = initial_money
        self.m_clues = initial_clues
        self.m_statset = statset
        self.m_location = home
        self.m_movement_points = 0

        # XXX get rid of this
        self.m_skills = dict (evade = statset.m_sneak,
                              horror = statset.m_will,
                              combat = statset.m_fight,
                              lore = statset.m_lore,
                              luck = statset.m_luck,
                              will = statset.m_will)

    def name (self):
        return self.m_name

    def clues (self):
        return self.m_clues

    def gain_clues (self, clues):
        assert clues > 0
        self.m_clues += clues

    def location (self):
        return self.m_location

    def reduce_sanity (self, amount):
        print "reduce sanity by %s" % amount,
        self.m_sanity -= amount
        if self.m_sanity < 0:
            self.m_sanity = 0
        print "to", self.m_sanity

    def reduce_stamina (self, amount):
        print "reduce stamina by %s" % amount,
        self.m_stamina -= amount
        if self.m_stamina < 0:
            self.m_stamina = 0
        print "to", self.m_stamina

    def lose_movement_points (self):
        self.m_movement_points = 0

    def movement_points (self):
        return self.m_movement_points

    def alive (self):
        return self.m_sanity > 0 and self.m_stamina > 0

    # Override in subclass
    def before_turn_0 (self, game):
        # Pick up fixed & random posessions, whatever else...
        pass

    def roll_dice (self):
        import random
        # XXX curses, blesses
        return random.randint (1, 6) >= 5

    def perform_check (self, game, skill_name, modifier, difficulty):
        die = self.m_skills[skill_name] + modifier
        successes = sum (self.roll_dice () for _ in xrange (die))
        # XXX spend clue tokens to gain advantage
        ret = successes >= difficulty
        print "check %s, %s/%s successes on %s die"\
            % ("passed" if ret else "failed",
               successes, difficulty, die)
        return ret

    def devour (self, game, monster):
        game.devour (self)

class Damage:
    def deal (self, game, investigator, monster):
        pass

class DamageSanity (Damage):
    def __init__ (self, amount):
        self.m_amount = amount
    def deal (self, game, investigator, monster):
        investigator.reduce_sanity (self.m_amount)

class DamageStamina (Damage):
    def __init__ (self, amount):
        self.m_amount = amount
    def deal (self, game, investigator, monster):
        investigator.reduce_stamina (self.m_amount)

class DamageDevour (Damage):
    def deal (self, game, investigator, monster):
        investigator.devour (game, monster)

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

damage_devour = DamageDevour ()

class Check:
    def __init__ (self, ret):
        self.m_ret = ret
    def check (self, game, investigator):
        return self.m_ret

class SkillCheck (Check):
    def __init__ (self, skill_name, modifier, difficulty = 1):
        self.m_skill_name = skill_name
        self.m_modifier = modifier
        self.m_difficulty = difficulty

    def check (self, game, investigator):
        print "%s check:" % self.m_skill_name,
        return investigator.perform_check (game, self.m_skill_name,
                                           self.m_modifier, self.m_difficulty)

class ConditionalCheck (Check):
    def __init__ (self, predicate, check_pass, check_fail = Check (False)):
        self.m_pred = predicate
        self.m_pass = check_pass
        self.m_fail = check_fail

    def check (self, game, investigator):
        if self.m_pred (game, investigator):
            return self.m_pass.check (game, investigator)
        else:
            return self.m_fail.check (game, investigator)

pass_check = Check (True)
fail_check = Check (False)
def evade_check (awareness):
    return SkillCheck ("evade", awareness, 1)
def horror_check (rating):
    return SkillCheck ("horror", rating, 1)
def combat_check (rating, toughness):
    return SkillCheck ("combat", rating, toughness)

class Monster (ObjectWithAttributes):
    def __init__ (self, name, **attributes):
        ObjectWithAttributes.__init__ (self)
        self.m_name = name
        self.m_location = None
        self.apply_attributes (attributes)

    def name (self):
        return self.m_name

    def location (self):
        return self.m_location

    def move_to (self, location):
        self.m_location = location

    # Override in subclass
    def xxx_combat_check (self, game, investigator):
        # Examples from the game:
        #
        # - Before you make a Combat check against Child Of Abhoth,
        #   you must discard 1 Clue token or automatically fail.
        #
        # - Before making a Combat check against Crawling One, roll a
        #   die. X is equal to the result of the die roll. [X is his
        #   combat rating]
        #
        # - If you pass a Combat check against Child Of Abhoth, you
        #   must discard 1 Spell or Weapon, if able.
        #
        # - If you fail a Combat check or Evade check against Child of
        #   the Goat, you are delayed.
        raise NotImplementedError ()

    def xxx_horror_check (self, game, investigator):
        # - Before you make a Horror check against Child Of Abhoth,
        #   you must discard 1 Clue token or automatically fail.
        return True

    def xxx_move (self, game):
        # - Instead of moving, roll a die. On a 4-6, all Investigators
        #   in Arkham lose 1 Sanity.
        raise NotImplementedError ()

class BasicMonster (Monster):
    def __init__ (self, name,
                  evade_check,
                  horror_check, horror_damage,
                  combat_check, combat_damage,
                  **attributes):
        Monster.__init__ (self, name, **attributes)
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

    # Override in subclass
    def consistent (self, mod_index):
        return False

    def construct (self, game):
        pass

    def post_construct (self, game):
        pass

    def before_turn_0 (self, game):
        pass

class ModuleInstance:

    def __init__ (self, game, type):
        self.m_game = game
        self.m_type = type

    def game (self):
        return self.m_game

    def construct (self):
        return self.m_type.construct (self.m_game)

    def post_construct (self):
        return self.m_type.post_construct (self.m_game)

    def before_turn_0 (self):
        return self.m_type.before_turn_0 (self.m_game)

class UI:
    def setup_players (self, game):
        raise NotImplementedError ()

    def setup_investigator (self, game, investigator):
        raise NotImplementedError ()

class Game:
    def __init__ (self, modules, ui):
        self.m_modis = [ModuleInstance (self, mod) for mod in modules]
        self.m_ui = ui

        self.m_neighborhoods = []
        self.m_locations = []
        self.m_all_investigators = set ()
        self.m_investigators = []

        self.m_monsters_extra = [] # ancient ones, heralds, etc.
        self.m_registered_monsters = {} # monster->count
        self.m_monster_cup = []
        self.m_loc_monsters = {} # location->monster

        if len (modules) == 0:
            raise RuntimeError ("No modules to play with!")
        assert ui != None

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

    def add_investigator (self, it):
        self.m_all_investigators.add (it)

    def use_investigator (self, it):
        assert it in self.m_all_investigators
        self.m_investigators.append (it)
        print "%s playing" % it.name ()

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

    def move_monster (self, monster, location):
        if location not in self.m_loc_monsters:
            self.m_loc_monsters[location] = []
        self.m_loc_monsters[location].append (monster)
        monster.move_to (location)

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
            investigator.before_turn_0 (self)
            self.m_ui.setup_investigator (self, investigator)

        brave = self.m_investigators[0]
        for monster in self.m_monster_cup:
            self.move_monster (monster, brave.location ())
            break
        if self.leave_location (brave, brave.location ()):
            print "you managed to leave the location"


    # 0: won't fight
    # 1: does't want to fight, but failed awareness check
    # 2: wants to fight
    def will_fight (self, investigator, monster):
        import fight
        if self.m_ui.wants_to_fight (self, investigator, monster):
            return 2
        elif monster.evade_check ().check (self, investigator):
            return 0
        else:
            investigator.lose_movement_points ()
            fight.deal_combat_damage_hook (self, investigator, monster)
            if investigator.alive ():
                return 1
            else:
                return 0

    # Whether the fight should be ended.
    def break_fight (self, investigator, monster):
        if investigator.location () != monster.location ():
            return True
        if not investigator.alive ():
            return True
        return False

    # Retur False if investigator can't leave the location.
    def leave_location (self, investigator, location):
        import fight
        print "%s attempts to leave a location" % investigator.name ()
        monsters = self.m_loc_monsters.get (location, [])
        if monsters != []:
            for monster in monsters:
                print "dealing with %s" % monster.name ()
                try:
                    if self.will_fight (investigator, monster) != 0:
                        investigator.lose_movement_points ()
                        fight.fight_hook (self, investigator, monster)
                except fight.EndCombat:
                    pass
                print "combat is over"
                if not investigator.alive ():
                    print "investigator died"
                    break
            print "all monsters were dealt with"
        return investigator.alive () and investigator.movement_points () > 0

    def environment (self):
        # XXX Haunter Of The Dark currently asks for that, but that
        # binds environment cards too tightly into the system.  Need
        # to come up with better solution.
        return None

    def terror_track (self):
        # XXX Same here with the Maniac
        return 0

    def devour (self, investigator):
        # XXX not implemented
        pass
