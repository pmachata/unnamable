import arkham

class Amount:
    def __init__ (self, amount):
        self.m_amount = amount

    def reduce (self, amount):
        assert amount > 0
        self.m_amount -= amount
        if self.m_amount < 0:
            self.m_amount == 0

    def amount (self):
        return self.m_amount

class Damage:
    def __init__ (self, aspects):
        self.m_aspects = aspects


    def amount (self, aspect):
        return self.m_aspects[aspect]

    def aspects (self):
        return self.m_aspects.keys ()

    def inflict (self, investigator):
        for aspect, amount in self.m_aspects.iteritems ():
            investigator.health (aspect).reduce (amount.amount ())

class Harm:
    def deal (self, game, investigator, monster):
        raise NotImplementedError ()

    def description (self, game, investigator, monster):
        raise NotImplementedError ()

class HarmNone (Harm):
    def deal (self, game, investigator, monster):
        pass

    def description (self, game, investigator, monster):
        return "-"

class HarmHealth (Harm):
    def __init__ (self, aspect, amount):
        self.m_aspect = aspect
        self.m_amount = amount

    def description (self, game, investigator, monster):
        return "%s %+d" % (self.m_aspect.name (), -self.m_amount)

    def deal (self, game, investigator, monster):
        arkham.damage_hook (game, investigator, monster,
                            Damage ({self.m_aspect: Amount (self.m_amount)}))

class HarmSanity (HarmHealth):
    def __init__ (self, amount):
        HarmHealth.__init__ (self, arkham.health_sanity, amount)

class HarmStamina (HarmHealth):
    def __init__ (self, amount):
        HarmHealth.__init__ (self, arkham.health_stamina, amount)

class HarmDevour (Harm):
    def deal (self, game, investigator, monster):
        investigator.devour (game, monster)

    def description (self, game, investigator, monster):
        return "devour"

class ConditionalHarm (Harm):
    def __init__ (self, predicate, harm_pass, harm_fail = Harm ()):
        self.m_pred = predicate
        self.m_pass = harm_pass
        self.m_fail = harm_fail

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

class SpecialHarm (Harm):
    def description (self, game, investigator, monster):
        return "*"

harm_none = HarmNone ()
harm_devour = HarmDevour ()
