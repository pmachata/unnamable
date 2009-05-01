import arkham

class Check:
    def check (self, game, investigator):
        raise NotImplementedError ()

    def description (self, game, investigator, subject):
        raise NotImplementedError ()

class ConstCheck (Check):
    def __init__ (self, ret):
        self.m_ret = ret

    def check (self, game, investigator, subject):
        return self.m_ret

    def description (self, game, investigator):
        if self.m_ret:
            return "pass"
        else:
            return "fail"

class SkillCheck (Check):
    def __init__ (self, check_base, base_modifier, difficulty = 1):
        self.m_check_base = check_base
        self.m_base_modifier = base_modifier
        self.m_difficulty = difficulty
        assert difficulty >= 1

    def check (self, game, investigator, subject):
        print "%s check:" % self.m_check_base.name ()
        return game.perform_check_hook \
            (game, investigator, subject,
             self.m_check_base, self.m_base_modifier, self.m_difficulty)

    def difficulty (self):
        return self.m_difficulty

    def description (self, game, investigator):
        return "%s(%+d)%s" % (self.m_check_base.name (),
                              self.m_base_modifier,
                               ("[%d]" % self.m_difficulty
                                if self.m_difficulty > 1 else ""))

class ConditionalCheck (Check):
    def __init__ (self, predicate, check_pass, check_fail = ConstCheck (False)):
        self.m_pred = predicate
        self.m_pass = check_pass
        self.m_fail = check_fail

    def check (self, game, investigator, subject):
        if self.m_pred (game, investigator):
            return self.m_pass.check (game, investigator, subject)
        else:
            return self.m_fail.check (game, investigator, subject)

    def description (self, game, investigator):
        if self.m_pred (game, investigator):
            return self.m_pass.description (game, investigator)
        else:
            return self.m_fail.description (game, investigator)

class SpecialCheck (Check):
    def description (self, game, investigator):
        return "*"

pass_check = ConstCheck (True)
fail_check = ConstCheck (False)
def evade_check (awareness):
    return SkillCheck (arkham.checkbase_evade, awareness, 1)
def horror_check (rating):
    return SkillCheck (arkham.checkbase_horror, rating, 1)
def combat_check (rating, toughness):
    return SkillCheck (arkham.checkbase_combat, rating, toughness)
def spell_check (rating):
    return SkillCheck (arkham.checkbase_spell, rating, 1)
