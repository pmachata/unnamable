import tester
import mod_ah
import test_ah
import fun
import arkham
import mod_common
import mod_unique
import mod_spell

class ModuleProto (test_ah.ModuleProto):
    def turn_0 (self, game):
        inv, = game.investigators ()
        self.setup_investigator (game, inv)
        return inv

class Test (tester.Controller):
    def __init__ (self, proto):
        self.proto = proto
        tester.Controller.__init__ (self)

    def setup_players (self, game):
        self.inv, = self.use_investigators (game, ["\"Ashcan\" Pete"])

    def add_modules (self, idx):
        idx.add_module (self.proto ())

    def actions (self):
        return self.proto.actions (self)

def action_bound_item_named (name):
    def match (arg):
        item = arg.bound_item ()
        if not item:
            return False
        else:
            return item.name () == name
    return match

def action_bound_monster_named (name):
    def match (arg):
        item = arg.bound_monster ()
        if not item:
            return False
        else:
            return item.name () == name
    return match

def cast_spell (damage, *roll):
    yield fun.matchclass (arkham.GameplayAction_Multiple) # cast spell
    if damage:
        yield fun.matchclass (arkham.GameplayAction_IncurDamage) # spell damage
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook) # lore check
    for i in roll: yield i

def test_item (name, actions, deck = mod_common.CommonDeck):
    class ModuleProto1 (ModuleProto):
        def setup_investigator (self, game, inv):
            item = game.deck (deck).draw (lambda arg: arg.name () == name)
            inv.take_item (game, item)
            assert inv.wield_item (game, item)

        @classmethod
        def actions (self, test):
            return actions (test, name)

    return ModuleProto1

def discard_gain_new (items1, items2):
    # discarded + gain new
    assert len (items1) == len (items2)
    assert len (items1 - items2) == 1
    assert len (items2 - items1) == 1

def test1 (test, name):
    yield fun.and_ (action_bound_item_named (name),
                    fun.matchclass (arkham.GameplayAction_Multiple))
    clues = test.inv.clues ()
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    for dice in 5,5: yield dice
    assert test.inv.clues () == clues + 3
    raise tester.EndTest (True)

def test2 (test, name):
    yield fun.and_ (action_bound_item_named (name),
                    fun.matchclass (arkham.GameplayAction_Multiple))
    items1 = set (item.proto () for item in test.inv.m_items)
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    for dice in 5,5: yield dice
    items2 = set (item.proto () for item in test.inv.m_items)
    discard_gain_new (items1, items2)
    raise tester.EndTest (True)

def test3 (test, name):
    # turn 1
    yield fun.and_ (action_bound_item_named (name),
                    fun.matchclass (arkham.GameplayAction_Multiple))
    sanity = test.inv.health (arkham.health_sanity).cur ()
    stamina = test.inv.health (arkham.health_stamina).cur ()
    yield fun.matchclass (arkham.GameplayAction_IncurDamage)
    assert test.inv.health (arkham.health_sanity).cur () == sanity - 1
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    yield 1 # failure
    sanity = test.inv.health (arkham.health_sanity).cur ()
    yield fun.matchclass (arkham.GameplayAction_IncurDamage)
    assert test.inv.health (arkham.health_stamina).cur () == stamina - 2
    test.inv.health (arkham.health_sanity).add (4)
    yield fun.matchclass (arkham.GameplayAction_Stay)

    # turn 2
    yield fun.and_ (action_bound_item_named (name),
                    fun.matchclass (arkham.GameplayAction_Multiple))
    sanity = test.inv.health (arkham.health_sanity).cur ()
    yield fun.matchclass (arkham.GameplayAction_IncurDamage)
    assert test.inv.health (arkham.health_sanity).cur () == sanity - 1
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    yield 5 # success
    clues = test.inv.clues ()
    yield fun.matchclass (arkham.GameplayAction_GainClues)
    assert test.inv.clues () == clues + 3
    raise tester.EndTest (True)

def test4 (test, name):
    items1 = set (item.proto () for item in test.inv.m_items)
    yield fun.and_ (action_bound_item_named (name),
                    fun.matchclass (arkham.GameplayAction_Multiple))
    clues = test.inv.clues ()
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    yield 1 # failure
    assert test.inv.clues () == clues + 2
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    yield 5 # pass
    items2 = set (item.proto () for item in test.inv.m_items)
    discard_gain_new (items1, items2)
    raise tester.EndTest (True)

def test5 (test, name):
    items1 = set (item.proto () for item in test.inv.m_items)
    yield fun.and_ (action_bound_item_named (name),
                    fun.matchclass (arkham.GameplayAction_Multiple))
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    yield 5
    items2 = set (item.proto () for item in test.inv.m_items)
    discard_gain_new (items1, items2)
    raise tester.EndTest (True)

def test6 (test, name):
    items1 = set (item.proto () for item in test.inv.m_items)
    yield fun.and_ (action_bound_item_named (name),
                    fun.matchclass (arkham.GameplayAction_Multiple))
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    yield 5
    yield fun.matchclass (arkham.GameplayAction_IncurDamage)
    items2 = set (item.proto () for item in test.inv.m_items)
    discard_gain_new (items1, items2)
    raise tester.EndTest (True)

def test7 (test, name):
    h = []
    for aspect in arkham.health_sanity, arkham.health_stamina:
        health = test.inv.health (aspect)
        health.reduce (1)
        h.append (health.cur ())

    yield fun.matchclass (arkham.GameplayAction_Stay)
    yield lambda arg: arg.name ().find ("sanity") >= 0
    assert test.inv.health (arkham.health_sanity).cur () == h[0] + 1

    yield fun.matchclass (arkham.GameplayAction_Stay)

    # Use matchclass now to make sure that we have only one available
    # match: to heal stamina.
    yield lambda arg: "stamina" in arg.name ()
    assert test.inv.health (arkham.health_stamina).cur () == h[1] + 1

    yield fun.matchclass (arkham.GameplayAction_Stay)
    raise tester.EndTest (True)

def test8 (test, name):
    items1 = set (item.proto () for item in test.inv.m_items)
    yield fun.and_ (action_bound_item_named (name),
                    fun.matchclass (arkham.GameplayAction_Multiple))
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    yield 5; yield 5
    yield fun.matchclass (arkham.GameplayAction_IncurDamage)
    items2 = set (item.proto () for item in test.inv.m_items)
    discard_gain_new (items1, items2)
    raise tester.EndTest (True)

def test9 (test, name):
    items1 = set (item.proto () for item in test.inv.m_items)
    yield fun.and_ (action_bound_item_named (name),
                    fun.matchclass (arkham.GameplayAction_Multiple))
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    yield 5
    yield fun.matchclass (arkham.GameplayAction_IncurDamage)
    items2 = set (item.proto () for item in test.inv.m_items)
    discard_gain_new (items1, items2)
    raise tester.EndTest (True)

def test10 (test, name):
    assert test.inv.movement_points () == 6
    yield fun.matchclass (arkham.GameplayAction_Stay)
    raise tester.EndTest (True)

def test11 (test, name):
    yield fun.and_ (action_bound_item_named (name),
                    fun.matchclass (arkham.GameplayAction_Multiple))
    clues = test.inv.clues ()
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    yield 5
    assert test.inv.clues () == clues + 4
    raise tester.EndTest (True)

def test12 (n):
    def t (test, name):
        h = test.inv.health (arkham.health_stamina)
        h.reduce (5)
        hv = h.cur ()
        yield fun.matchclass (arkham.GameplayAction_Stay) # wait for next round
        for y in cast_spell (True, *list (5 if i < n else 1 for i in range (4))): yield y
        yield lambda action: " %d " % n in action.name ()
        assert h.cur () == hv + n
        yield fun.matchclass (arkham.GameplayAction_Stay)
        raise tester.EndTest (True)
    return t

if __name__ == "__main__":
    tester.run_test (test_ah.Game (Test (test_item ("Old Journal", test1))))
    tester.run_test (test_ah.Game (Test (test_item ("Ancient Tome", test2))))
    tester.run_test (test_ah.Game (Test (test_item ("Alien Statue", test3, mod_unique.UniqueDeck))))
    tester.run_test (test_ah.Game (Test (test_item ("Ancient Tablet", test4, mod_unique.UniqueDeck))))
    tester.run_test (test_ah.Game (Test (test_item ("Cabala of Saboth", test5, mod_unique.UniqueDeck))))
    tester.run_test (test_ah.Game (Test (test_item ("Cultes des Goules", test6, mod_unique.UniqueDeck))))
    tester.run_test (test_ah.Game (Test (test_item ("Healing Stone", test7, mod_unique.UniqueDeck))))
    tester.run_test (test_ah.Game (Test (test_item ("Nameless Cults", test8, mod_unique.UniqueDeck))))
    tester.run_test (test_ah.Game (Test (test_item ("Necronomicon", test9, mod_unique.UniqueDeck))))
    tester.run_test (test_ah.Game (Test (test_item ("Ruby of R'lyeh", test10, mod_unique.UniqueDeck))))
    tester.run_test (test_ah.Game (Test (test_item ("The King in Yellow", test11, mod_unique.UniqueDeck))))
    tester.run_test (test_ah.Game (Test (test_item ("Heal", test12 (1), mod_spell.SpellDeck))))
    tester.run_test (test_ah.Game (Test (test_item ("Heal", test12 (2), mod_spell.SpellDeck))))
    tester.run_test (test_ah.Game (Test (test_item ("Heal", test12 (3), mod_spell.SpellDeck))))
