import tester
import arkham
import maps
import fun
import mod_ah

class Investigator1 (tester.TestInvestigator):
    def __init__ (self, name, loc, **skills):
        tester.TestInvestigator.__init__ (self, name, loc, **skills)

class ModuleProto (mod_ah.ModuleProto):
    def mythos (self, game):
        # We don't want to do regular AH mythos phase.
        return []

    def construct (self, game):
        mod_ah.ModuleProto.construct (self, game)

    def turn_0 (self, game):
        # We don't want to do regular AH turn_0 phase.
        mon = self.m_monster_cup.draw (lambda arg: arg.name () == "Gug")
        invs = game.investigators ()
        assert len (invs) == 1
        game.add_monster (mon, invs[0].location ())
        return []

class Test1 (tester.Controller):
    def setup_players (self, game):
        self.inv, = self.use_investigators (game, ["\"Ashcan\" Pete"])

    def add_modules (self, idx):
        idx.add_module (ModuleProto ())

    def actions (self):
        yield fun.matchclass (arkham.GameplayAction_Stay)
        yield fun.matchclass (arkham.GameplayAction_DealWithMonster)
        yield fun.matchclass (arkham.GameplayAction_Fight)
        for roll in 5,: yield roll # pass horror check
        for i in 1,2:
            yield fun.matchclass (arkham.GameplayAction_Fight)
            for roll in 1,1,1: yield roll
            yield fun.matchclass (arkham.GameplayAction_FailRoll)
        yield fun.matchclass (mod_ah.GameplayAction_Incapacitated)
        assert self.inv.location ().attributes ().flag ("hospital")
        raise tester.EndTest (True)

class Game1 (tester.TestGame):
    def __init__ (self):
        tester.TestGame.__init__ (self, Test1 (), ["ah"])

class Test2 (Test1):
    def actions (self):
        self.inv.health (arkham.health_sanity).reduce (3)
        yield fun.matchclass (arkham.GameplayAction_Stay)
        yield fun.matchclass (arkham.GameplayAction_DealWithMonster)
        yield fun.matchclass (arkham.GameplayAction_Fight)
        for roll in 1,: yield roll # fail horror check
        yield fun.matchclass (arkham.GameplayAction_FailRoll)
        yield fun.matchclass (mod_ah.GameplayAction_Incapacitated)
        assert self.inv.location ().attributes ().flag ("asylum")
        raise tester.EndTest (True)

class Game2 (tester.TestGame):
    def __init__ (self):
        tester.TestGame.__init__ (self, Test2 (), ["ah"])

tester.run_test (Game1 ())
#tester.run_test (Game2 ())
