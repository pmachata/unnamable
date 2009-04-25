import arkham

class Amount:
    def __init__ (self, parent, amount):
        self.m_parent = parent
        self.m_amount = amount

    def reduce (self, amount):
        assert amount > 0
        self.m_amount -= amount
        if self.m_amount < 0:
            self.m_amount == 0
        if self.m_amount == 0:
            self.m_parent.reduced_out (self)

    def amount (self):
        return self.m_amount

class ImpactHealth:
    def __init__ (self, aspects):
        self.m_aspects = dict ((aspect, Amount (self, amount))
                               for aspect, amount in aspects.iteritems ()
                               if amount > 0)

    def amount (self, aspect):
        return self.m_aspects[aspect]

    def aspects (self):
        return self.m_aspects.keys ()

    def reduced_out (self, amount):
        key, = [key
                for key, value in self.m_aspects.iteritems ()
                if value == amount]
        del self.m_aspects[key]

class Damage (ImpactHealth):
    def inflict (self, investigator):
        for aspect, amount in self.m_aspects.iteritems ():
            investigator.health (aspect).reduce (amount.amount ())

    def description (self):
        return ", ".join ("%s %+d" % (aspect.name (), -amount.amount ())
                          for aspect, amount in self.m_aspects.iteritems ())

class Heal (ImpactHealth):
    def heal (self, investigator):
        for aspect, amount in self.m_aspects.iteritems ():
            investigator.health (aspect).add (amount.amount ())

    def description (self):
        return ", ".join ("%s %+d" % (aspect.name (), amount.amount ())
                          for aspect, amount in self.m_aspects.iteritems ())

class Harm:
    def cause (self, game, investigator, monster):
        raise NotImplementedError ()

    def description (self, game, investigator, monster):
        raise NotImplementedError ()

class HarmNone (Harm):
    def cause (self, game, investigator, monster):
        pass

    def description (self, game, investigator, monster):
        return "-"

class HarmDamage (Harm):
    def __init__ (self, damage):
        self.m_damage = damage

    def description (self, game, investigator, monster):
        return self.m_damage.description ()

    def cause (self, game, investigator, monster):
        arkham.damage_hook (game, investigator, monster, self.m_damage)

class HarmHealth (HarmDamage):
    def __init__ (self, aspect, amount):
        HarmDamage.__init__ (self, Damage ({aspect: amount}))

class HarmSanity (HarmHealth):
    def __init__ (self, amount):
        HarmHealth.__init__ (self, arkham.health_sanity, amount)

class HarmStamina (HarmHealth):
    def __init__ (self, amount):
        HarmHealth.__init__ (self, arkham.health_stamina, amount)

class HarmDevour (Harm):
    def cause (self, game, investigator, monster):
        investigator.devour (game, monster)

    def description (self, game, investigator, monster):
        return "devour"

class ConditionalHarm (Harm):
    def __init__ (self, predicate, harm_pass, harm_fail = Harm ()):
        self.m_pred = predicate
        self.m_pass = harm_pass
        self.m_fail = harm_fail

    def cause (self, game, investigator, monster):
        if self.m_pred (game, investigator, monster):
            return self.m_pass.cause (game, investigator, monster)
        else:
            return self.m_fail.cause (game, investigator, monster)

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
