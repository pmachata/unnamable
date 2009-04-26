import tester
import mod_ah
import test_ah
import fun
import arkham

class ModuleProto (test_ah.ModuleProto):
    def construct (self, game):
        test_ah.ModuleProto.construct (self, game)
        self.m_monster_cup.register (
            arkham.SimpleMonster ("Test-Mon1",
                                  -2, (-1, 2), 3, (-2, 4)),
            1)

    def turn_0 (self, game):
        mon = self.m_monster_cup.draw (lambda arg: arg.name () == "Test-Mon1")
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
        yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
        for roll in 5,: yield roll # pass horror check
        for i in 1,2:
            yield fun.matchclass (arkham.GameplayAction_Fight)
            yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
            for roll in 1,1,1: yield roll
            yield fun.matchclass (arkham.GameplayAction_FailRoll)
            yield fun.matchclass (arkham.GameplayAction_EndCauseHarmLoop)
            yield fun.matchclass (arkham.GameplayAction_IncurDamage)
        yield fun.matchclass (mod_ah.GameplayAction_Incapacitated)
        assert self.inv.location ().attributes ().flag ("hospital")
        raise tester.EndTest (True)

class Test2 (Test1):
    def actions (self):
        self.inv.health (arkham.health_sanity).reduce (3)
        yield fun.matchclass (arkham.GameplayAction_Stay)
        yield fun.matchclass (arkham.GameplayAction_DealWithMonster)
        yield fun.matchclass (arkham.GameplayAction_Fight)
        yield fun.matchclass (arkham.GameplayAction_NormalCheckHook)
        for roll in 1,: yield roll # fail horror check
        yield fun.matchclass (arkham.GameplayAction_FailRoll)
        yield fun.matchclass (arkham.GameplayAction_IncurDamage)
        yield fun.matchclass (mod_ah.GameplayAction_Incapacitated)
        assert self.inv.location ().attributes ().flag ("asylum")
        raise tester.EndTest (True)

tester.run_test (test_ah.Game (Test1 ()))
tester.run_test (test_ah.Game (Test2 ()))
