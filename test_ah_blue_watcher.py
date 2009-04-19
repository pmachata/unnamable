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

if __name__ == "__main__":
    tester.run_test (test_ah.Game (Test (ModuleProto1)))
