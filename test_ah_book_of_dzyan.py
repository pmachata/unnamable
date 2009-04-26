import tester
import mod_ah
import test_ah
import fun
import arkham
import mod_common
import mod_unique
from test_ah_items import *

def test1 (test, name):
    yield fun.and_ (action_bound_item_named (name),
                    fun.matchclass (arkham.GameplayAction_Multiple))
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    for die in 5, 5: yield die
    yield fun.matchclass (arkham.GameplayAction_IncurDamage)
    yield fun.matchclass (arkham.GameplayAction_Stay)
    yield fun.and_ (action_bound_item_named (name),
                    fun.matchclass (arkham.GameplayAction_Multiple))
    yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
    for die in 5, 5: yield die
    yield fun.matchclass (arkham.GameplayAction_IncurDamage)
    yield fun.matchclass (arkham.GameplayAction_Stay)
    # check the item got dropped after two uses
    for item in test.inv.wields_items ():
        assert item.name () != name
    raise tester.EndTest (True)

if __name__ == "__main__":
    tester.run_test (test_ah.Game (Test (test_item ("Book of Dzyan", test1, mod_unique.UniqueDeck))))
