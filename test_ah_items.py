import tester
import mod_ah
import test_ah
import fun
import arkham
import mod_common
import mod_unique

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

def test1 (test, name):
    yield action_bound_item_named (name)
    clues = test.inv.clues ()
    for dice in 5,5: yield dice
    assert test.inv.clues () == clues + 3
    raise tester.EndTest (True)

def test2 (test, name):
    yield action_bound_item_named (name)
    items1 = set (item.proto () for item in test.inv.m_items)
    for dice in 5,5: yield dice
    items2 = set (item.proto () for item in test.inv.m_items)

    # discarded Ancient Tome, but gained another one from the deck
    assert len (items1) == len (items2)
    assert len (items1 - items2) == 1
    assert len (items2 - items1) == 1
    raise tester.EndTest (True)

def test3 (test, name):
    # turn 1
    yield action_bound_item_named (name)
    sanity = test.inv.health (arkham.health_sanity).cur ()
    yield fun.matchclass (arkham.GameplayAction_IncurDamage)
    assert test.inv.health (arkham.health_sanity).cur () == sanity - 1
    yield 1 # failure
    sanity = test.inv.health (arkham.health_sanity).cur ()
    yield fun.matchclass (arkham.GameplayAction_IncurDamage)
    assert test.inv.health (arkham.health_sanity).cur () == sanity - 2
    test.inv.health (arkham.health_sanity).add (4)
    yield fun.matchclass (arkham.GameplayAction_Stay)

    # turn 2
    yield action_bound_item_named (name)
    sanity = test.inv.health (arkham.health_sanity).cur ()
    yield fun.matchclass (arkham.GameplayAction_IncurDamage)
    assert test.inv.health (arkham.health_sanity).cur () == sanity - 1
    yield 5 # success
    clues = test.inv.clues ()
    yield fun.matchclass (arkham.GameplayAction_GainClues)
    assert test.inv.clues () == clues + 3
    raise tester.EndTest (True)

def test4 (test, name):
    items1 = set (item.proto () for item in test.inv.m_items)
    yield action_bound_item_named (name)
    clues = test.inv.clues ()
    yield 1 # failure
    assert test.inv.clues () == clues + 3
    yield 5 # pass
    items2 = set (item.proto () for item in test.inv.m_items)

    # discarded Ancient Tablet, but gained another item from the deck
    assert len (items1) == len (items2)
    assert len (items1 - items2) == 1
    assert len (items2 - items1) == 1
    raise tester.EndTest (True)

if __name__ == "__main__":
    tester.run_test (test_ah.Game (Test (test_item ("Old Journal", test1))))
    tester.run_test (test_ah.Game (Test (test_item ("Ancient Tome", test2))))
    tester.run_test (test_ah.Game (Test (test_item ("Alien Statue", test3, mod_unique.UniqueDeck))))
    tester.run_test (test_ah.Game (Test (test_item ("Ancient Tablet", test4, mod_unique.UniqueDeck))))
