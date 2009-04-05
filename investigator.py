from loc import *

class Hand:
    def can_handle (self, game, investigator, object):
        return True

class Investigator (ObjectWithLocation, GameplayObject):
    def __init__ (self, name, sanity, stamina,
                  initial_money, initial_clues, skills, home):
        ObjectWithLocation.__init__ (self, home)
        self.m_name = name
        self.m_max_sanity = sanity
        self.m_sanity = sanity
        self.m_max_stamina = stamina
        self.m_stamina = stamina
        self.m_money = initial_money
        self.m_clues = initial_clues
        self.m_skills = skills
        self.m_movement_points = 0
        self.m_delayed = False
        self.m_trophies = []
        self.m_hands = []
        self.m_active_items = []

    def name (self):
        return self.m_name

    def clues (self):
        return self.m_clues

    def gain_clues (self, clues):
        assert clues > 0
        self.m_clues += clues

    def sanity (self):
        return self.m_sanity

    def stamina (self):
        return self.m_stamina

    def reduce_sanity (self, amount):
        assert amount >= 0
        print "reduce sanity by %s" % amount,
        self.m_sanity -= amount
        if self.m_sanity < 0:
            self.m_sanity = 0
        print "to", self.m_sanity

    def add_sanity (self, amount):
        assert amount >= 0
        print "add %s to sanity" % amount,
        self.m_sanity += amount
        if self.m_sanity > self.m_max_sanity:
            self.m_sanity = self.m_max_sanity
        print "to", self.m_sanity

    def reduce_stamina (self, amount):
        assert amount >= 0
        print "reduce stamina by %s" % amount,
        self.m_stamina -= amount
        if self.m_stamina < 0:
            self.m_stamina = 0
        print "to", self.m_stamina

    def add_stamina (self, amount):
        assert amount >= 0
        print "add %s to stamina" % amount,
        self.m_stamina += amount
        if self.m_stamina > self.m_max_stamina:
            self.m_stamina = self.m_max_stamina
        print "to", self.m_stamina

    def spend_movement_point (self):
        assert self.m_movement_points > 0
        self.m_movement_points -= 1

    def lose_movement_points (self):
        self.m_movement_points = 0

    def movement_points (self):
        return self.m_movement_points

    def alive (self):
        return self.m_sanity > 0 and self.m_stamina > 0

    def delay (self):
        self.m_delayed = True

    def delayed (self):
        return self.m_delayed

    def skill (self, skill_name):
        return self.m_skills.check (skill_name)

    def devour (self, game, monster):
        game.devour (self)

    def trophies (self):
        return list (self.m_trophies)

    def claim_trophy (self, monster):
        print "claiming trophy %s" % monster.name ()
        self.m_trophies.append (monster)

    def active_items (self):
        return []

    # Game construction phases.  Phases are called in sequence.  Given
    # phase is called only after the previous phase was finished for
    # all investigators.
    def prepare_pass_1 (self, game):
        pass
    def prepare_pass_2 (self, game):
        pass

    # Game play phases.
    def upkeep (self, game):
        mp = self.m_skills.check ("speed")
        # XXX apply equipment and allies
        self.m_movement_points = mp
        return []

    def movement (self, game):
        if self.m_movement_points > 0:
            dest_actions = [GameplayAction_Move (location)
                            for location
                            in [conn.dest ()
                                for conn in self.location ().connections ()
                                if not conn.attributes ().flag ("no_investigator")]]
        else:
            dest_actions = []

        return [GameplayAction_Stay (self.m_location)] + dest_actions

    # Combat phases.
    def pre_combat (self, combat, monster):
        return [GameplayAction_Evade_PreCombat (combat, monster),
                GameplayAction_Fight (monster)]

    def combat_turn (self, combat, monster):
        return [GameplayAction_Evade_Combat (combat, monster),
                GameplayAction_Fight (monster)]

    # Unconscious/Insane actions.
    def investigator_unconscious (self, game):
        return []

    def investigator_insane (self, game):
        return []

class CommonInvestigator (Investigator):
    def __init__ (self, *args, **kwargs):
        Investigator.__init__ (*args, **kwargs)
        self.m_hands = [Hand (), Hand ()]

from actions import *
