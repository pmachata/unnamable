from loc import *
import arkham

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

        self.m_hands = set ()

        self.m_items = []
        self.m_active_items = {} # item->[hands]

    def name (self):
        return self.m_name

    def clues (self):
        return self.m_clues

    def gain_clues (self, clues):
        assert clues > 0
        self.m_clues += clues

    def spend_clue (self):
        assert self.m_clues > 0
        self.m_clues -= 1

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

    def gain_movement_points (self, amount):
        assert amount > 0
        self.m_movement_points += amount

    def lose_movement_points (self):
        self.m_movement_points = None # no movement at all possible
                                      # until next turn

    def spend_movement_points (self, amount):
        assert self.m_movement_points >= amount
        self.m_movement_points -= amount

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

    def add_hand (self, hand):
        assert hand not in self.m_hands
        self.m_hands.add (hand)

    def take_item (self, game, item):
        self.m_items.append (item)

    def discard_item (self, item):
        # xxx ugly linear lookup
        if item in self.m_active_items:
            self.release_item (item)
        assert item in self.m_items
        del self.m_items[self.m_items.index (item)]
        item.discard ()

    def find_wield (self, game, item, hands):
        wants_wield = [(item, item.hands ())
                       for item in  self.m_active_items.keys ()] \
                       + [(item, hands)]
        if sum (hands for item, hands in wants_wield) > len (self.m_hands):
            return False

        # Taken from Python Recipe 190465, from a comment by Simone Leo:
        # http://code.activestate.com/recipes/190465/#c6
        def xpermutations (L):
            if len (L) <= 1:
                yield L
            else:
                a = [L.pop (0)]
                for p in xpermutations (L):
                    for i in range (len (p) + 1):
                        yield p[:i] + a + p[i:]

        # We basically try to assign hands to items in all possible
        # ways.  This involves iterating all permutations of list of
        # hands.  That's factorial in time complexity.  Luckily we
        # typically deal with two-handed investigators, and the most
        # hands we can probably encounter is three or four.  So don't
        # bother inventing anything smart.
        found_wield = None
        for hands in xpermutations (list (self.m_hands)):
            can_handle_all = True
            wield = {}

            it = 0
            for item, h in wants_wield:
                hands_for_item = hands[it : it+h]
                it += h
                if False in (hand.can_handle (game, self, item)
                             for hand in hands_for_item):
                    can_handle_all = False
                    break
                wield[item] = hands_for_item

            if can_handle_all:
                found_wield = wield

        return found_wield

    def wield_item (self, game, item):
        found_wield = self.find_wield (game, item, item.hands ())
        if found_wield != None:
            self.m_active_items = found_wield
            return True
        else:
            return False

    def release_item (self, item):
        assert item in self.m_active_items
        del self.m_active_items[item]

    def wields_items (self):
        return list (self.m_active_items.keys ())

    def wields_item (self, item):
        return item in self.m_active_items

    # Game construction phases.  Phases are called in sequence.  Given
    # phase is called only after the previous phase was finished for
    # all investigators.
    def prepare_pass_1 (self, game):
        pass
    def prepare_pass_2 (self, game):
        pass

    # Game play phases.
    def upkeep (self, game):
        self.m_movement_points = self.initial_movement_points ()
        return sum ((item.upkeep (game, self)
                     for item in self.m_active_items), [])

    def movement (self, game):
        if self.m_movement_points > 0:
            dest_actions = [arkham.GameplayAction_Move (location)
                            for location
                            in [conn.dest ()
                                for conn in self.location ().connections ()
                                if not conn.attributes ().flag ("no_investigator")]]
        else:
            dest_actions = []

        return [arkham.GameplayAction_Stay (self.m_location)] + dest_actions \
            + sum ((item.movement (game, self)
                    for item in self.m_active_items), [])

    def initial_movement_points (self):
        " not including bonuses for items "
        return self.m_skills.check ("speed")

    # Combat phases.
    def item_actions (self):
        return [arkham.GameplayAction_WieldItem (item)
                for item in self.m_items
                if item not in self.m_active_items] \
             + [arkham.GameplayAction_ReleseItem (item)
                for item in self.m_items
                if item in self.m_active_items]

    def pre_combat (self, combat, monster):
        return ([arkham.GameplayAction_Evade_PreCombat (combat, monster),
                 arkham.GameplayAction_Fight (monster)]
                + self.item_actions ())

    def combat_turn (self, combat, monster):
        return ([arkham.GameplayAction_Evade_Combat (combat, monster),
                 arkham.GameplayAction_Fight (monster)]
                + self.item_actions ())

    # Unconscious/Insane actions.
    def investigator_unconscious (self, game):
        return []

    def investigator_insane (self, game):
        return []

    # Other actions
    def check_correction_actions (self, game, subject, skill_name, roll):
        ret = []
        if self.m_clues > 0:
            ret.append \
                (arkham.GameplayAction_Multiple \
                     ([arkham.GameplayAction_SpendClue (),
                       arkham.GameplayAction_AddRoll (subject, skill_name, roll)]))
        # xxx apparently, clue tokens should simply be items.  The
        # downside of that is that the investigator could choose from
        # N identical "spend this clue token" actions, that would need
        # to be handled in some way.
        return ret + sum (([arkham.GameplayAction_Multiple \
                                ([spend_clue_action,
                                  arkham.GameplayAction_AddRoll (subject, skill_name, roll)])
                            for spend_clue_action
                            in arkham.spend_clue_token_actions_hook \
                                (game, self, subject, item, skill_name)]
                           for item in self.m_active_items), [])

class CommonInvestigator (Investigator):
    def __init__ (self, *args, **kwargs):
        Investigator.__init__ (self, *args, **kwargs)
        self.add_hand (Hand ())
        self.add_hand (Hand ())
