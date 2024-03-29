import fun

from obj import *
from loc import *
from investigator import *
from monster import *
from actions import *
from skills import *
from checks import *
from damage import *
from track import *
from item import *
from instances import *
from deck import *
from game import *

from fight_hooks import *
from check_hooks import *
from damage_hooks import *

class ModuleIndex:
    def __init__ (self):
        self.m_module_idx = {}
        self.m_modules = {}
        self.m_modules_ordered = []

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
        self.m_modules_ordered.append (module)
        return module

    def has_module (self, signature):
        module = self.m_module_idx[signature]
        if module == None:
            return False
        else:
            return self.m_modules[module]

    def requested_modules (self):
        return list (self.m_modules_ordered)

class ModuleProto (NamedObject):
    def __init__ (self, signature, name):
        NamedObject.__init__ (self, name)
        self.m_signature = signature

    def signature (self):
        return self.m_signature

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
    def upkeep_1 (self, game):
        pass
    def upkeep_2 (self, game):
        return []
    def upkeep_3 (self, game):
        return []

    def movement (self, game):
        return []

    def encounters_1 (self, game):
        return []
    def encounters_2 (self, game):
        return []

    def mythos (self, game):
        return []

    # Combat phases.
    def pre_combat (self, combat, investigator, monster):
        return []

    def combat_turn (self, combat, investigator, monster):
        return []

    # Unconscious/Insane actions.
    def investigator_dead (self, game, investigator):
        return []

class UI:
    def setup_players (self, game):
        raise NotImplementedError ()

    def select_action (self, game, investigator, actions):
        raise NotImplementedError ()
