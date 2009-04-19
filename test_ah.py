import tester
import arkham
import maps
import mod_ah

class ModuleProto (mod_ah.ModuleProto):
    def mythos (self, game):
        # We don't want to do regular AH mythos phase.
        return []

    def turn_0 (self, game):
        # We don't want to do regular AH turn_0 phase.
        return []

    def signature (self):
        return "test-" + mod_ah.ModuleProto.signature (self)

class Game (tester.TestGame):
    def __init__ (self, controller):
        tester.TestGame.__init__ (self, controller, ["test-ah"])
