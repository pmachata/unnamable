import tester
import mod_ah
import test_ah
import fun
import arkham
import mod_common
import mod_unique
from test_ah_items import *

def test_weapon (name, actions, deck = mod_common.CommonDeck):
    class ModuleProto1 (ModuleProto):
        def setup_investigator (self, game, inv):
            item = game.deck (deck).draw (lambda arg: arg.name () == name)
            inv.take_item (game, item)
            assert inv.wield_item (game, item)

            class SomeMonster (arkham.SimpleMonster):
                def __init__ (self):
                    arkham.SimpleMonster.__init__ \
                        (self, "SomeMonster",
                         0, (0, 1), 1, (0, 1))
            game.add_monster (arkham.Monster (SomeMonster ()),
                              inv.location ())

        @classmethod
        def actions (self, test):
            return actions (test, name)

    return ModuleProto1

def test1 (test, name):
    yield fun.matchclass (arkham.GameplayAction_Stay)
    yield fun.matchclass (arkham.GameplayAction_DealWithMonster)
    yield fun.matchclass (arkham.GameplayAction_Fight)
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    yield 5; yield 5 # pass horror check
    yield fun.matchclass (arkham.GameplayAction_Fight)
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    for i in xrange (13): yield 1 # fail combat hook
    yield fun.matchclass (arkham.GameplayAction_FailRoll)
    yield fun.matchclass (arkham.GameplayAction_EndCauseHarmLoop)
    yield fun.matchclass (arkham.GameplayAction_IncurDamage)
    yield fun.matchclass (arkham.GameplayAction_Fight)
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    for i in xrange (5): yield 5 # pass combat hook, this time with fewer die
    yield fun.matchclass (arkham.GameplayAction_Stay)
    raise tester.EndTest (True)

def test2 (test, name):
    yield fun.matchclass (arkham.GameplayAction_Stay)
    yield fun.matchclass (arkham.GameplayAction_DealWithMonster)
    yield fun.matchclass (arkham.GameplayAction_Fight)
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    yield 5; yield 5 # pass horror check
    yield fun.matchclass (arkham.GameplayAction_Fight)
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    for i in xrange (14): yield 1 # fail combat hook
    yield fun.matchclass (arkham.GameplayAction_IncurDamage) # after-use damage
    yield fun.matchclass (arkham.GameplayAction_FailRoll)
    yield fun.matchclass (arkham.GameplayAction_EndCauseHarmLoop)
    yield fun.matchclass (arkham.GameplayAction_IncurDamage) # monster hit
    yield fun.matchclass (arkham.GameplayAction_Fight)
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    for i in xrange (5): yield 5 # pass combat hook, this time with fewer die
    yield fun.matchclass (arkham.GameplayAction_Stay)
    raise tester.EndTest (True)

def test3 (test, name):
    yield fun.matchclass (arkham.GameplayAction_Stay)
    yield fun.matchclass (arkham.GameplayAction_DealWithMonster)
    yield fun.matchclass (arkham.GameplayAction_Evade)
    yield fun.matchclass (arkham.GameplayAction_Multiple)
    yield fun.matchclass (arkham.GameplayAction_Stay)
    raise tester.EndTest (True)

def test4 (test, name):
    yield fun.matchclass (arkham.GameplayAction_Stay)
    yield fun.matchclass (arkham.GameplayAction_DealWithMonster)
    yield fun.matchclass (arkham.GameplayAction_Fight)
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    yield 5; yield 5 # pass horror check
    yield fun.matchclass (arkham.GameplayAction_Fight)
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    for i in xrange (5): yield 1 # fail combat hook
    yield fun.matchclass (arkham.GameplayAction_FailRoll)
    stamina = test.inv.health (arkham.health_stamina).cur ()
    yield fun.matchclass (arkham.GameplayAction_Multiple) # cancel stamina, discard
    assert stamina == test.inv.health (arkham.health_stamina).cur ()
    yield fun.matchclass (arkham.GameplayAction_Fight)
    raise tester.EndTest (True)

if __name__ == "__main__":
    tester.run_test (test_ah.Game (Test (test_weapon ("Dynamite", test1))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Powder of Ibn-Ghazi", test2, mod_unique.UniqueDeck))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Silver Key", test3, mod_unique.UniqueDeck))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Warding Statue", test4, mod_unique.UniqueDeck))))
