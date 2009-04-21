import tester
import mod_ah
import test_ah
import fun
import arkham
import mod_common
import mod_unique
from test_ah_items import *

class ModuleProto1 (ModuleProto):
    item_name = "Blue Watcher of the Pyramid"
    item_deck = mod_unique.UniqueDeck

    def setup_investigator (self, game, inv):
        item = game.deck (self.__class__.item_deck)\
            .draw (lambda arg: arg.name () == self.__class__.item_name)
        inv.take_item (game, item)
        assert inv.wield_item (game, item)

        class MyMonster (arkham.MonsterProto):
            def __init__ (self):
                arkham.MonsterProto.__init__ (self, "MyMonster")
            def horror_check (self):
                return arkham.pass_check
            def combat_check (self):
                return arkham.SkillCheck (arkham.checkbase_combat, 0)
            def resistances (self):
                return {}
        game.add_monster (arkham.Monster (MyMonster ()), inv.location ())

    @classmethod
    def actions (cls, test):
        yield fun.matchclass (arkham.GameplayAction_Stay)
        yield fun.matchclass (arkham.GameplayAction_DealWithMonster)
        yield fun.matchclass (arkham.GameplayAction_Fight)
        trophies = len (test.inv.trophies ())
        yield fun.if_else (action_bound_item_named (cls.item_name),
                           fun.matchclass (arkham.GameplayAction_Multiple))
        yield fun.matchclass (arkham.GameplayAction_IncurDamage)
        assert len (test.inv.trophies ()) == trophies + 1
        raise tester.EndTest (True)

class ModuleProto2 (ModuleProto1):
    @classmethod
    def actions (cls, test):
        yield fun.matchclass (arkham.GameplayAction_Stay)
        yield fun.matchclass (arkham.GameplayAction_DealWithMonster)
        yield fun.matchclass (arkham.GameplayAction_Fight)
        yield fun.matchclass (arkham.GameplayAction_Fight)
        for die in 1, 1, 1, 1, 1: yield die
        trophies = len (test.inv.trophies ())
        yield action_bound_item_named (cls.item_name)
        yield fun.matchclass (arkham.GameplayAction_IncurDamage) # use costs -2 sanity
        assert len (test.inv.trophies ()) == trophies + 1
        raise tester.EndTest (True)

class ModuleProto3 (ModuleProto):
    item_name = "Flute of the Outer Gods"
    item_deck = mod_unique.UniqueDeck

    def setup_investigator (self, game, inv):
        item = game.deck (self.__class__.item_deck)\
            .draw (lambda arg: arg.name () == self.__class__.item_name)
        inv.take_item (game, item)
        assert inv.wield_item (game, item)

        class MyMonster (arkham.MonsterProto):
            def __init__ (self):
                arkham.MonsterProto.__init__ (self, "MyMonster")
            def horror_check (self):
                return arkham.pass_check

        for i in range (5):
            game.add_monster (arkham.Monster (MyMonster ()), inv.location ())

    @classmethod
    def actions (cls, test):
        yield fun.matchclass (arkham.GameplayAction_Stay)
        yield fun.take_first ()
        yield fun.matchclass (arkham.GameplayAction_Fight)
        yield fun.matchclass (arkham.GameplayAction_Multiple)
        yield fun.matchclass (arkham.GameplayAction_IncurDamage)
        assert len (test.inv.trophies ()) == 5
        raise tester.EndTest (True)

class TestEnchantedBlade (ModuleProto):
    item_name = "Enchanted Blade"

if __name__ == "__main__":
    tester.run_test (test_ah.Game (Test (ModuleProto1)))
    tester.run_test (test_ah.Game (Test (ModuleProto2)))
    tester.run_test (test_ah.Game (Test (ModuleProto3)))
