import tester
import mod_ah
import test_ah
import fun
import arkham

_damage = 4

class ModuleProto (test_ah.ModuleProto):
    def do_turn_0 (self, game, item):
        assert item

        inv, = game.investigators ()
        inv.take_item (game, item)
        assert inv.wield_item (game, item)

        return inv

    def heal_action_times (self):
        return 1

class ModuleProto1 (ModuleProto):
    def turn_0 (self, game):
        inv = ModuleProto.do_turn_0 \
            (self, game,
             self.m_common_deck.draw \
                 (lambda arg: arg.name () == "Food"))
        arkham.HarmStamina (_damage).deal (game, inv, arkham.Subject ())

class ModuleProto2 (ModuleProto):
    def turn_0 (self, game):
        inv = ModuleProto.do_turn_0 \
            (self, game,
             self.m_common_deck.draw \
                 (lambda arg: arg.name () == "Whiskey"))
        arkham.HarmSanity (_damage).deal (game, inv, arkham.Subject ())

class ModuleProto3 (ModuleProto):
    def turn_0 (self, game):
        inv = ModuleProto.do_turn_0 \
            (self, game,
             self.m_unique_deck.draw \
                 (lambda arg: arg.name () == "Enchanted Jewelry"))
        arkham.HarmStamina (_damage).deal (game, inv, arkham.Subject ())

    def heal_action_times (self):
        return 3

class Test (tester.Controller):
    def __init__ (self, proto, aspect):
        tester.Controller.__init__ (self)
        self.aspect = aspect
        self.module = proto ()

    def setup_players (self, game):
        self.inv, = self.use_investigators (game, ["\"Ashcan\" Pete"])

    def add_modules (self, idx):
        idx.add_module (self.module)

    def actions (self):
        x = self.module.heal_action_times ()
        for i in range (x):
            yield fun.matchclass (arkham.GameplayAction_Multiple)
        h = self.inv.health (self.aspect).cur ()
        yield fun.matchclass (arkham.GameplayAction_IncurDamage)
        assert self.inv.health (self.aspect).cur () == h - _damage + x
        raise tester.EndTest (True)

tester.run_test (test_ah.Game (Test (ModuleProto1, arkham.health_stamina)))
tester.run_test (test_ah.Game (Test (ModuleProto2, arkham.health_sanity)))
tester.run_test (test_ah.Game (Test (ModuleProto3, arkham.health_stamina)))
