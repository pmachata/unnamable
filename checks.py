class Check:
    def check (self, game, investigator):
        raise NotImplementedError ()

    def description (self, game, investigator):
        raise NotImplementedError ()

class ConstCheck (Check):
    def __init__ (self, ret):
        self.m_ret = ret

    def check (self, game, investigator):
        return self.m_ret

    def description (self, game, investigator):
        if self.m_ret:
            return "pass"
        else:
            return "fail"

class SkillCheck (Check):
    def __init__ (self, skill_name, modifier, difficulty = 1):
        self.m_skill_name = skill_name
        self.m_modifier = modifier
        self.m_difficulty = difficulty
        assert difficulty >= 1

    def check (self, game, investigator):
        print "%s check:" % self.m_skill_name,
        return investigator.perform_check (game, self.m_skill_name,
                                           self.m_modifier, self.m_difficulty)

    def description (self, game, investigator):
        return "%s(%+d)%s" % (self.m_skill_name, self.m_modifier,
                               ("[%d]" % self.m_difficulty
                                if self.m_difficulty > 1 else ""))

class ConditionalCheck (Check):
    def __init__ (self, predicate, check_pass, check_fail = ConstCheck (False)):
        self.m_pred = predicate
        self.m_pass = check_pass
        self.m_fail = check_fail

    def check (self, game, investigator):
        if self.m_pred (game, investigator):
            return self.m_pass.check (game, investigator)
        else:
            return self.m_fail.check (game, investigator)

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
    return SkillCheck ("evade", awareness, 1)
def horror_check (rating):
    return SkillCheck ("horror", rating, 1)
def combat_check (rating, toughness):
    return SkillCheck ("combat", rating, toughness)
