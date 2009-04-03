class Damage:
    def deal (self, game, investigator, monster):
        raise NotImplementedError ()

    def description (self, game, investigator, monster):
        raise NotImplementedError ()

class DamageNone (Damage):
    def deal (self, game, investigator, monster):
        pass

    def description (self, game, investigator, monster):
        return "-"

class DamageSanity (Damage):
    def __init__ (self, amount):
        self.m_amount = amount

    def deal (self, game, investigator, monster):
        investigator.reduce_sanity (self.m_amount)

    def description (self, game, investigator, monster):
        return "sanity %+d" % -self.m_amount

class DamageStamina (Damage):
    def __init__ (self, amount):
        self.m_amount = amount

    def deal (self, game, investigator, monster):
        investigator.reduce_stamina (self.m_amount)

    def description (self, game, investigator, monster):
        return "stamina %+d" % -self.m_amount

class DamageDevour (Damage):
    def deal (self, game, investigator, monster):
        investigator.devour (game, monster)

    def description (self, game, investigator, monster):
        return "devour"

class ConditionalDamage (Damage):
    def __init__ (self, predicate, damage_pass, damage_fail = Damage ()):
        self.m_pred = predicate
        self.m_pass = damage_pass
        self.m_fail = damage_fail

    def deal (self, game, investigator, monster):
        if self.m_pred (game, investigator, monster):
            return self.m_pass.deal (game, investigator, monster)
        else:
            return self.m_fail.deal (game, investigator, monster)

    def description (self, game, investigator, monster):
        if self.m_pred (game, investigator, monster):
            return self.m_pass.description (game, investigator, monster)
        else:
            return self.m_fail.description (game, investigator, monster)

class SpecialDamage (Damage):
    def description (self, game, investigator, monster):
        return "*"


damage_none = DamageNone ()
damage_devour = DamageDevour ()
