import tester
import mod_ah
import test_ah
import fun
import arkham
import mod_common
import mod_unique
import mod_spell
from test_ah_items import *

def test_weapons (actions, names, special_abilities = [], **attrib):
    class ModuleProto1 (ModuleProto):
        def setup_investigator (self, game, inv):
            for name, deck in names:
                item = game.deck (deck).draw (lambda arg: arg.name () == name)
                inv.take_item (game, item)
                assert inv.wield_item (game, item)

            class SomeMonster (arkham.SimpleMonster):
                def __init__ (self):
                    toughness = attrib.pop ("toughness", 1)
                    awareness = attrib.pop ("awareness", 1)
                    arkham.SimpleMonster.__init__ \
                        (self, "SomeMonster",
                         awareness, (0, 1), toughness, (0, 1),
                         special_abilities, **attrib)
            mon = arkham.Monster (SomeMonster ())
            game.add_monster (mon, inv.location ())

        @classmethod
        def actions (self, test):
            return actions (test)

    return ModuleProto1

class look_for_action:
    def __init__ (self, lookfor, match):
        self.seen = 0
        self.lookfor = lookfor
        self.match = match
    def __call__ (self, action):
        if self.lookfor (action):
            self.seen += 1
        return self.match (action)

def test_weapon (name, actions, deck = mod_common.CommonDeck,
                 special_abilities = [], **attrib):
    return test_weapons (actions, [(name, deck)], special_abilities, **attrib)

def fight_and_horror_check (*roll):
    yield fun.matchclass (arkham.GameplayAction_Stay)
    yield fun.matchclass (arkham.GameplayAction_DealWithMonster)
    yield fun.matchclass (arkham.GameplayAction_Fight)
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    for i in roll: yield i

def test1 (test):
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

def test2 (test):
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

def test3 (test):
    yield fun.matchclass (arkham.GameplayAction_Stay)
    yield fun.matchclass (arkham.GameplayAction_DealWithMonster)
    yield fun.matchclass (arkham.GameplayAction_Evade)
    yield fun.matchclass (arkham.GameplayAction_Multiple)
    yield fun.matchclass (arkham.GameplayAction_Stay)
    raise tester.EndTest (True)

def test4 (test):
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

def test5 (test):
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
    def test (test):
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

def test7 (test):
    for y in fight_and_horror_check (5, 5): yield y
    yield fun.matchclass (arkham.GameplayAction_Fight)
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook) # combat check
    for y in 1, 1, 1, 1, 1: yield y # fail first roll with five die
    yield fun.matchclass (arkham.GameplayAction_FailRoll)
    yield fun.matchclass (arkham.GameplayAction_EndCauseHarmLoop)
    yield fun.matchclass (arkham.GameplayAction_IncurDamage) # monster hit
    for y in cast_spell (5, 5, 5): yield y
    yield fun.matchclass (arkham.GameplayAction_ForCombat)
    yield fun.matchclass (arkham.GameplayAction_Fight)
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook) # combat check
    for y in 1, 1, 1, 1, 1, 5, 5: yield y # pass second roll with seven die
    yield fun.matchclass (arkham.GameplayAction_Stay)
    raise tester.EndTest (True)

def test8 (awareness):
    def t (test):
        yield fun.matchclass (arkham.GameplayAction_Stay)
        yield fun.matchclass (arkham.GameplayAction_DealWithMonster)
        yield fun.matchclass (arkham.GameplayAction_Evade)
        yield lambda action: (" lore(%+d) " % awareness) in action.name ()
        yield fun.matchclass (arkham.GameplayAction_NormalCheckHook) # lore check
        for i in range (3 + awareness):
            yield 5
        yield fun.matchclass (arkham.GameplayAction_Stay)
        raise tester.EndTest (True)
    return t

def test9 (n):
    def t(test):
        h = test.inv.health (arkham.health_sanity)
        hv = h.cur ()
        for y in fight_and_horror_check (5, 5): yield y
        assert h.cur () == hv - n
        yield fun.matchclass (arkham.GameplayAction_Fight)
        raise tester.EndTest (True)
    return t

def test10 (n):
    def t(test):
        h = test.inv.health (arkham.health_stamina)
        hv = h.cur ()
        for y in fight_and_horror_check (5, 5): yield y
        yield fun.matchclass (arkham.GameplayAction_Fight)
        yield fun.matchclass (arkham.GameplayAction_NormalCheckHook) # combat check
        for y in 1, 1, 1, 1, 1, 5, 5: yield y # pass combat check
        assert h.cur () == hv - n
        yield fun.matchclass (arkham.GameplayAction_Stay)
        raise tester.EndTest (True)
    return t

def test11 (n):
    """ Check that ambush monster presents an option to evade before
    the combat begins, but not in the middle of the combat. """
    yield fun.matchclass (arkham.GameplayAction_Stay)
    yield fun.matchclass (arkham.GameplayAction_DealWithMonster)
    e1 = look_for_action (fun.matchclass (arkham.GameplayAction_Evade),
                          fun.matchclass (arkham.GameplayAction_Fight))
    yield e1
    assert e1.seen == 1
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    for i in 5, 5: yield i

    e2 = look_for_action (fun.matchclass (arkham.GameplayAction_Evade),
                          fun.matchclass (arkham.GameplayAction_Fight))
    yield e2
    assert e2.seen == 0
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook) # combat check
    raise tester.EndTest (True)

if __name__ == "__main__":
    tester.run_test (test_ah.Game (Test (test_weapon ("Dynamite", test1))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Powder of Ibn-Ghazi", test2, mod_unique.UniqueDeck))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Silver Key", test3, mod_unique.UniqueDeck))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Warding Statue", test4, mod_unique.UniqueDeck))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Dread Curse of Azathoth", test5, mod_spell.SpellDeck))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Bind Monster", test6 (1), mod_spell.SpellDeck, toughness=1))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Bind Monster", test6 (2), mod_spell.SpellDeck, toughness=2))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Bind Monster", test6 (3), mod_spell.SpellDeck, toughness=3))))
    tester.run_test (test_ah.Game (Test (test_weapons (test7, [("Enchant Weapon", mod_spell.SpellDeck),
                                                               (".18 Derringer", mod_common.CommonDeck)],
                                                       {arkham.monster_physical: arkham.reslev_immunity}))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Mists of Releh", test8 (-1), mod_spell.SpellDeck, awareness=-1))))
    tester.run_test (test_ah.Game (Test (test_weapon ("Mists of Releh", test8 (+1), mod_spell.SpellDeck, awareness=+1))))
    tester.run_test (test_ah.Game (Test (test_weapon (".18 Derringer", test9 (1), mod_common.CommonDeck,
                                                      {arkham.monster_nightmarish: 1}))))
    tester.run_test (test_ah.Game (Test (test_weapon (".18 Derringer", test9 (2), mod_common.CommonDeck,
                                                      {arkham.monster_nightmarish: 2}))))
    tester.run_test (test_ah.Game (Test (test_weapon (".18 Derringer", test10 (1), mod_common.CommonDeck,
                                                      {arkham.monster_overwhelming: 1}))))
    tester.run_test (test_ah.Game (Test (test_weapon (".18 Derringer", test10 (2), mod_common.CommonDeck,
                                                      {arkham.monster_overwhelming: 2}))))
    tester.run_test (test_ah.Game (Test (test_weapon (".18 Derringer", test11, mod_common.CommonDeck,
                                                      {arkham.monster_ambush: None}))))
