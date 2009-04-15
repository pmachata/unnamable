import tester
import mod_ah
import test_ah
import fun
import arkham

_damage = 3

class ModuleProto (test_ah.ModuleProto):
    def turn_0 (self, game):
        inv, = game.investigators ()

        item = self.m_common_deck.draw (lambda arg: arg.name () == "Food")
        inv.take_item (game, item)
        inv.wield_item (game, item)

        item = self.m_common_deck.draw (lambda arg: arg.name () == "Whiskey")
        inv.take_item (game, item)
        inv.wield_item (game, item)

        return inv

class ModuleProto1 (ModuleProto):
    def turn_0 (self, game):
        inv = ModuleProto.turn_0 (self, game)
        arkham.HarmStamina (_damage).deal (game, inv, None)

class ModuleProto2 (ModuleProto):
    def turn_0 (self, game):
        inv = ModuleProto.turn_0 (self, game)
        arkham.HarmSanity (_damage).deal (game, inv, None)

class Test (tester.Controller):
    def __init__ (self, proto, aspect):
        tester.Controller.__init__ (self)
        self.proto = proto
        self.aspect = aspect

    def setup_players (self, game):
        self.inv, = self.use_investigators (game, ["\"Ashcan\" Pete"])

    def add_modules (self, idx):
        idx.add_module (self.proto ())

    def actions (self):
        yield fun.matchclass (arkham.GameplayAction_Multiple)
        h = self.inv.health (self.aspect).cur ()
        yield fun.matchclass (arkham.GameplayAction_IncurDamage)
        assert self.inv.health (self.aspect).cur () == h - _damage + 1
        raise tester.EndTest (True)

tester.run_test (test_ah.Game (Test (ModuleProto1, arkham.health_stamina)))
tester.run_test (test_ah.Game (Test (ModuleProto2, arkham.health_sanity)))
