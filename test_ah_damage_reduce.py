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

    def expected_increment (self, x):
        return x

    def actions (self):
        yield fun.matchclass (arkham.GameplayAction_Multiple)

class ModuleProto1 (ModuleProto):
    def turn_0 (self, game):
        inv = ModuleProto.do_turn_0 \
            (self, game,
             self.m_common_deck.draw \
                 (lambda arg: arg.name () == "Food"))
        arkham.HarmStamina (_damage).cause (game, inv, arkham.Subject ())

class ModuleProto2 (ModuleProto):
    def turn_0 (self, game):
        inv = ModuleProto.do_turn_0 \
            (self, game,
             self.m_common_deck.draw \
                 (lambda arg: arg.name () == "Whiskey"))
        arkham.HarmSanity (_damage).cause (game, inv, arkham.Subject ())

class ModuleProto3 (ModuleProto):
    def turn_0 (self, game):
        inv = ModuleProto.do_turn_0 \
            (self, game,
             self.m_unique_deck.draw \
                 (lambda arg: arg.name () == "Enchanted Jewelry"))
        arkham.HarmStamina (_damage).cause (game, inv, arkham.Subject ())

    def heal_action_times (self):
        return 3

class ModuleProto4 (ModuleProto):
    def turn_0 (self, game):
        inv = ModuleProto.do_turn_0 \
            (self, game,
             self.m_unique_deck.draw \
                 (lambda arg: arg.name () == "Obsidian Statue"))
        arkham.HarmStamina (_damage).cause (game, inv, arkham.Subject ())

    def expected_increment (self, x):
        return _damage

class ModuleProto5 (ModuleProto):
    def turn_0 (self, game):
        inv = ModuleProto.do_turn_0 \
            (self, game,
             self.m_spell_deck.draw \
                 (lambda arg: arg.name () == "Flesh Ward"))
        arkham.HarmStamina (_damage).cause (game, inv, arkham.Subject ())

    def expected_increment (self, x):
        return _damage

    def actions (self):
        yield fun.matchclass (arkham.GameplayAction_Multiple)
        yield fun.matchclass (arkham.GameplayAction_IncurDamage)
        yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
        yield 5 # succeed lore check
        yield fun.matchclass (arkham.GameplayAction_Stay) # the damage got reduced out

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
        y = self.module.expected_increment (x)
        for i in range (x):
            for action in self.module.actions ():
                yield action
        h = self.inv.health (self.aspect).cur ()
        if y != _damage:
            yield fun.matchclass (arkham.GameplayAction_IncurDamage)
        assert self.inv.health (self.aspect).cur () == h - _damage + y
        raise tester.EndTest (True)

tester.run_test (test_ah.Game (Test (ModuleProto1, arkham.health_stamina)))
tester.run_test (test_ah.Game (Test (ModuleProto2, arkham.health_sanity)))
tester.run_test (test_ah.Game (Test (ModuleProto3, arkham.health_stamina)))
tester.run_test (test_ah.Game (Test (ModuleProto4, arkham.health_stamina)))
tester.run_test (test_ah.Game (Test (ModuleProto5, arkham.health_stamina)))
