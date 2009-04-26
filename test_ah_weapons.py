import tester
import mod_ah
import test_ah
import fun
import arkham
import mod_common
import mod_unique
import mod_spell
from test_ah_items import *

def test_weapon (name, actions, deck = mod_common.CommonDeck, **attrib):
    class ModuleProto1 (ModuleProto):
        def setup_investigator (self, game, inv):
            item = game.deck (deck).draw (lambda arg: arg.name () == name)
            inv.take_item (game, item)
            assert inv.wield_item (game, item)

            class SomeMonster (arkham.SimpleMonster):
                def __init__ (self):
                    arkham.SimpleMonster.__init__ \
                        (self, "SomeMonster",
                         0, (0, 1), attrib.get ("toughness", 1), (0, 1))
            game.add_monster (arkham.Monster (SomeMonster ()),
                              inv.location ())

        @classmethod
        def actions (self, test):
            return actions (test, name)

    return ModuleProto1

def fight_and_horror_check (*roll):
    yield fun.matchclass (arkham.GameplayAction_Stay)
    yield fun.matchclass (arkham.GameplayAction_DealWithMonster)
    yield fun.matchclass (arkham.GameplayAction_Fight)
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    for i in roll: yield i

def cast_spell (*roll):
    yield fun.matchclass (arkham.GameplayAction_Multiple) # cast spell
    yield fun.matchclass (arkham.GameplayAction_IncurDamage) # spell damage
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook) # lore check
    for i in roll: yield i

def test1 (test, name):
    for y in fight_and_horror_check (5, 5): yield y
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
    for y in fight_and_horror_check (5, 5): yield y
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
    for y in fight_and_horror_check (5, 5): yield y
    yield fun.matchclass (arkham.GameplayAction_Fight)
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    for i in xrange (5): yield 1 # fail combat hook
    yield fun.matchclass (arkham.GameplayAction_FailRoll)
    stamina = test.inv.health (arkham.health_stamina).cur ()
    yield fun.matchclass (arkham.GameplayAction_Multiple) # cancel stamina, discard
    assert stamina == test.inv.health (arkham.health_stamina).cur ()
    yield fun.matchclass (arkham.GameplayAction_Fight)
    raise tester.EndTest (True)

def test5 (test, name):
    for y in fight_and_horror_check (5, 5): yield y
    for y in cast_spell (5): yield y
    yield fun.matchclass (arkham.GameplayAction_Fight)
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook) # combat check
    for i in xrange (14): yield 1 # fail combat hook
    yield fun.matchclass (arkham.GameplayAction_FailRoll)
    yield fun.matchclass (arkham.GameplayAction_EndCauseHarmLoop)
    yield fun.matchclass (arkham.GameplayAction_IncurDamage) # monster hit
    yield fun.matchclass (arkham.GameplayAction_Fight)
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook) # combat check
    for i in xrange (14): yield 5 # check we still have the bonus
    yield fun.matchclass (arkham.GameplayAction_Stay)
    assert len (test.inv.m_temporary_items) == 0 # check the spell didn't get stuck
    raise tester.EndTest (True)

def test6 (combat_successes):
    def test (test, name):
        for y in fight_and_horror_check (5, 5): yield y
        for y in cast_spell (*[5 if i < combat_successes else 1
                               for i in range (7)]):
            yield y
        yield fun.matchclass (arkham.GameplayAction_Stay)
        assert len (test.inv.m_temporary_items) == 0 # check the spell didn't get stuck
        assert len (test.inv.m_active_items) == 0 # check the spell was discarded
        assert len (test.inv.m_items) == 0 # check the spell was discarded
        raise tester.EndTest (True)
    return test

if __name__ == "__main__":
    tester.run_test (test_ah.Game (Test (test_weapon ("Dynamite", test1))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Powder of Ibn-Ghazi", test2, mod_unique.UniqueDeck))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Silver Key", test3, mod_unique.UniqueDeck))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Warding Statue", test4, mod_unique.UniqueDeck))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Dread Curse of Azathoth", test5, mod_spell.SpellDeck))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Bind Monster", test6 (1), mod_spell.SpellDeck, toughness=1))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Bind Monster", test6 (2), mod_spell.SpellDeck, toughness=2))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Bind Monster", test6 (3), mod_spell.SpellDeck, toughness=3))))
