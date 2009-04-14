import tester
import arkham
import maps
import fun

class Test1 (tester.Controller):
    def construct (self, game, module):
        maps.in_neighborhood (maps.neighborhood (game))
        module.add_locations ("A")
        module.add_investigator (game, "1", "A", combat=1, evade=1)
        module.add_monster (game, "A",
            arkham.SimpleMonster (
                "M1",
                0, (-1, 3), 3, (-1, 3)
            )
        )

    def setup_players (self, game):
        self.use_investigators (game, ["Inv1"])

    def actions (self):
        yield fun.matchclass (arkham.GameplayAction_Stay)
        yield fun.matchclass (arkham.GameplayAction_DealWithMonster)
        yield fun.matchclass (arkham.GameplayAction_Evade)
        for roll in 5,: yield roll

class Game1 (tester.TestGame):
    def __init__ (self):
        tester.TestGame.__init__ (self, Test1 ())

@arkham.pass_evade_check_hook.match  (tester.match_combat (Game1), tester.match_investigator ("1"), fun.any)
def do (combat, investigator, monster):
    raise tester.EndTest (True)


class Test2 (Test1):
    def actions (self):
        yield fun.matchclass (arkham.GameplayAction_Stay)
        yield fun.matchclass (arkham.GameplayAction_DealWithMonster)
        yield fun.matchclass (arkham.GameplayAction_Evade)
        for roll in 4,: yield roll
        yield fun.matchclass (arkham.GameplayAction_FailRoll)

class Game2 (tester.TestGame):
    def __init__ (self):
        tester.TestGame.__init__ (self, Test2 ())

@arkham.fail_evade_check_hook.match  (tester.match_combat (Game2), tester.match_investigator ("1"), fun.any)
def do (combat, investigator, monster):
    raise tester.EndTest (True)

tester.run_test (Game1)
tester.run_test (Game2)
