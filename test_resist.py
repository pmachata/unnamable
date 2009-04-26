import tester
import arkham
import maps
import fun

def gen_test (item_fam, *roll, **resist):
    class Test1 (tester.Controller):
        def construct (self, game, module):
            maps.in_neighborhood (maps.neighborhood (game))
            module.add_locations ("A")
            module.add_investigator (game, "1", "A", {
                    arkham.skill_fight: 1,
                    arkham.skill_sneak: 1,
                    arkham.skill_will: 1})

            module.add_monster (game, "A",
                arkham.SimpleMonster (
                    "M1",
                    0, (0, 0), 1, (0, 1),
                    **resist
                )
            )

        def setup_players (self, game):
            self.inv, = self.use_investigators (game, ["Inv1"])

            class MyItem (arkham.InvestigatorItem):
                def __init__ (self):
                    arkham.InvestigatorItem.__init__ (self, "item", 0, 1)

            @arkham.bonus_hook.match (fun.any, fun.any, fun.any,
                                      arkham.with_proto (fun.matchclass (MyItem)),
                                      fun.val == arkham.checkbase_combat)
            def do (game, investigator, subject, item, check_base):
                return arkham.Bonus (2, item_fam)

            assert self.inv.wield_item (game, arkham.Item (MyItem ()))

        def actions (self):
            yield fun.matchclass (arkham.GameplayAction_Stay)
            yield fun.matchclass (arkham.GameplayAction_DealWithMonster)
            yield fun.matchclass (arkham.GameplayAction_Fight)
            yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
            yield 5 # pass horror check
            yield fun.matchclass (arkham.GameplayAction_Fight)
            yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
            for die in roll: yield die
            yield fun.matchclass (arkham.GameplayAction_Stay)
            raise tester.EndTest (True)

    class Game1 (tester.TestGame):
        def __init__ (self):
            tester.TestGame.__init__ (self, Test1 ())

    return Game1 ()

tester.run_test (gen_test (arkham.family_physical, 5, 5, 5))
tester.run_test (gen_test (arkham.family_physical, 5, 5, physical="resistance"))
tester.run_test (gen_test (arkham.family_physical, 5, physical="immunity"))

tester.run_test (gen_test (arkham.family_magical, 5, 5, 5))
tester.run_test (gen_test (arkham.family_magical, 5, 5, 5, physical="resistance"))
tester.run_test (gen_test (arkham.family_magical, 5, 5, 5, physical="immunity"))

tester.run_test (gen_test (arkham.family_physical, 5, 5, 5))
tester.run_test (gen_test (arkham.family_physical, 5, 5, 5, magical="resistance"))
tester.run_test (gen_test (arkham.family_physical, 5, 5, 5, magical="immunity"))

tester.run_test (gen_test (arkham.family_magical, 5, 5, 5))
tester.run_test (gen_test (arkham.family_magical, 5, 5, magical="resistance"))
tester.run_test (gen_test (arkham.family_magical, 5, magical="immunity"))
