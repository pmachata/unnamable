import arkham

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

class DamageHealth (Damage):
    def __init__ (self, aspect, amount):
        self.m_aspect = aspect
        self.m_amount = amount

    def description (self, game, investigator, monster):
        return "%s %+d" % (self.m_aspect.name (), -self.m_amount)

    def deal (self, game, investigator, monster):
        arkham.deal_damage_hook (game, investigator, monster,
                                 self.m_aspect, self.m_amount)

class DamageSanity (DamageHealth):
    def __init__ (self, amount):
        DamageHealth.__init__ (self, arkham.health_sanity, amount)

class DamageStamina (DamageHealth):
    def __init__ (self, amount):
        DamageHealth.__init__ (self, arkham.health_stamina, amount)

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
