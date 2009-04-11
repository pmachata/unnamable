import fun
from loc import *
import arkham

class GameplayAction:
    def __init__ (self, name):
        self.m_name = name

    def name (self):
        return self.m_name

    def perform (self, game, investigator):
        pass

    def bound_location (self):
        return None

    def bound_monster (self):
        return None

    def bound_item (self):
        return None

class LocationBoundGameplayAction (GameplayAction):
    def __init__ (self, location, name):
        GameplayAction.__init__ (self, name)
        self.m_location = location

    def bound_location (self):
        return self.m_location

class MonsterBoundGameplayAction (GameplayAction):
    def __init__ (self, monster, name):
        GameplayAction.__init__ (self, name)
        self.m_monster = monster

    def bound_monster (self):
        return self.m_monster

class ItemBoundGameplayAction (GameplayAction):
    def __init__ (self, item, name):
        GameplayAction.__init__ (self, name)
        self.m_item = item

    def bound_item (self):
        return self.m_item

class GameplayAction_Multiple (GameplayAction):
    def __init__ (self, actions):
        GameplayAction.__init__ (self, ", ".join (action.name ()
                                                  for action in actions))
        self.m_actions = actions

    def perform (self, game, investigator):
        ret = None
        for action in self.m_actions:
            ret = action.perform (game, investigator) or ret
        return ret

    def bound_location (self):
        ret = None
        for action in self.m_actions:
            ret = action.bound_location () or ret
        return ret

    def bound_monster (self):
        ret = None
        for action in self.m_actions:
            ret = action.bound_monster () or ret
        return ret

    def bound_item (self):
        ret = None
        for action in self.m_actions:
            ret = action.bound_item () or ret
        return ret

class GameplayAction_Conditional (GameplayAction):
    def __init__ (self, game, investigator, subject,
                  check, action_pass, action_fail = None):
        GameplayAction.__init__ (self,
                                 "if %s passes then %s%s" \
                                     % (check.description (game, investigator),
                                        action_pass.name (),
                                        ("else %s" % action_fail.name () \
                                             if action_fail != None else "")))
        assert action_pass
        self.m_check = check
        self.m_pass = action_pass
        self.m_fail = action_fail
        self.m_subject = subject

    def perform (self, game, investigator):
        if self.m_check.check (game, investigator, self.m_subject):
            return self.m_pass.perform (game, investigator)
        elif self.m_fail != None:
            return self.m_fail.perform (game, investigator)
        else:
            return None

    def bound_location (self):
        ret = self.m_pass.bound_location ()
        if ret == None and self.m_fail:
            ret = self.m_fail.bound_location ()
        return ret

    def bound_monster (self):
        ret = self.m_pass.bound_monster ()
        if ret == None and self.m_fail:
            ret = self.m_fail.bound_monster ()
        return ret

    def bound_item (self):
        ret = self.m_pass.bound_item ()
        if ret == None and self.m_fail:
            ret = self.m_fail.bound_item ()
        return ret

# Movement actions

class GameplayAction_Move (LocationBoundGameplayAction):
    def __init__ (self, location):
        LocationBoundGameplayAction.__init__ (self, location, "move")

    def perform (self, game, investigator):
        game.move_investigator (investigator, self.m_location)
        if investigator.movement_points () > 0:
            # He might have lost all movement points during the fight
            # after he tried to leave the current location.
            investigator.spend_movement_points (1)

class GameplayAction_Stay (LocationBoundGameplayAction):
    def __init__ (self, location):
        LocationBoundGameplayAction.__init__ (self, location, "stay put")

    def perform (self, game, investigator):
        investigator.lose_movement_points ()
        raise arkham.EndPhase ()

class GameplayAction_GainMovementPoints (GameplayAction):
    def __init__ (self, amount):
        assert amount > 0
        GameplayAction.__init__ (self,
                                 "gain %d movement point%s" \
                                     % (amount, "s" if amount > 1 else ""))
        self.m_amount = amount

    def perform (self, game, investigator):
        investigator.gain_movement_points (self.m_amount)

class GameplayAction_GainClues (GameplayAction):
    def __init__ (self, amount):
        assert amount > 0
        GameplayAction.__init__ (self,
                                 "gain %d clue%s" \
                                     % (amount, "s" if amount > 1 else ""))
        self.m_amount = amount

    def perform (self, game, investigator):
        investigator.gain_clues (self.m_amount)

class GameplayAction_SpendMovementPoints (GameplayAction):
    def __init__ (self, amount):
        assert amount > 0
        GameplayAction.__init__ (self,
                                 "spend %d movement point%s" \
                                     % (amount, "s" if amount > 1 else ""))
        self.m_amount = amount

    def perform (self, game, investigator):
        investigator.spend_movement_points (self.m_amount)

class GameplayAction_Quit (GameplayAction):
    def __init__ (self):
        GameplayAction.__init__ (self, "quit the game")

    def perform (self, game, investigator):
        game.drop_investigator (investigator)

# Combat actions

class GameplayAction_Evade (MonsterBoundGameplayAction):
    def __init__ (self, combat, monster):
        MonsterBoundGameplayAction.__init__ (self, monster, "evade")
        self.m_combat = combat

class GameplayAction_Evade_PreCombat (GameplayAction_Evade):
    def __init__ (self, *args):
        GameplayAction_Evade.__init__ (self, *args)

    def perform (self, game, investigator):
        monster = self.m_monster
        arkham.evade_check_hook (self.m_combat, investigator, monster)
        investigator.lose_movement_points ()
        raise arkham.ContinueCombat () # Proceed with the combat.

class GameplayAction_Evade_Combat (GameplayAction_Evade):
    def __init__ (self, *args):
        GameplayAction_Evade.__init__ (self, *args)

    def perform (self, game, investigator):
        monster = self.m_monster
        arkham.evade_check_hook (self.m_combat, investigator, monster)

class GameplayAction_Fight (MonsterBoundGameplayAction):
    def __init__ (self, monster):
        MonsterBoundGameplayAction.__init__ (self, monster, "fight")

    def perform (self, game, investigator):
        raise arkham.ContinueCombat ()

class GameplayAction_DealWithMonster (MonsterBoundGameplayAction):
    def __init__ (self, monster):
        MonsterBoundGameplayAction.__init__ (self, monster, "deal with")

    def perform (self, game, investigator):
        print "dealing with %s" % self.m_monster.name ()
        game.fight (investigator, self.m_monster)
        print "combat finished"

# Item manipulation actions

class GameplayAction_WieldItem (ItemBoundGameplayAction):
    def __init__ (self, item):
        ItemBoundGameplayAction.__init__ (self, item, "wield")

    def perform (self, game, investigator):
        investigator.wield_item (game, self.m_item)

class GameplayAction_ReleseItem (ItemBoundGameplayAction):
    def __init__ (self, item):
        ItemBoundGameplayAction.__init__ (self, item, "release")

    def perform (self, game, investigator):
        investigator.release_item (self.m_item)

class GameplayAction_Exhaust (ItemBoundGameplayAction):
    def __init__ (self, item):
        ItemBoundGameplayAction.__init__ (self, item, "exhaust")

    def perform (self, game, investigator):
        self.m_item.exhaust ()

class GameplayAction_Discard (ItemBoundGameplayAction):
    def __init__ (self, item):
        ItemBoundGameplayAction.__init__ (self, item, "discard")

    def perform (self, game, investigator):
        if investigator.wields_item (self.m_item):
            investigator.release_item (self.m_item)
        investigator.discard_item (self.m_item)

class GameplayAction_SpendClue (GameplayAction):
    def __init__ (self):
        GameplayAction.__init__ (self, "spend clue token")

    def perform (self, game, investigator):
        investigator.spend_clue ()

class GameplayAction_DrawItem (GameplayAction):
    def __init__ (self, deck):
        GameplayAction.__init__ (self, "draw from %s" % deck.name ())
        assert deck != None
        self.m_deck = deck

    def perform (self, game, investigator):
        investigator.take_item (game, self.m_deck.draw ())

# Roll correction actions

class GameplayAction_AddRoll (GameplayAction):
    def __init__ (self, subject, skill_name, roll):
        GameplayAction.__init__ (self, "roll additional die")
        self.m_subject = subject
        self.m_skill_name = skill_name
        self.m_roll = roll

    def perform (self, game, investigator):
        self.m_roll.add_roll (game, investigator,
                              self.m_subject, self.m_skill_name)

class GameplayAction_Reroll (GameplayAction):
    def __init__ (self, subject, skill_name, roll):
        GameplayAction.__init__ (self, "reroll")
        self.m_subject = subject
        self.m_skill_name = skill_name
        self.m_roll = roll

    def perform (self, game, investigator):
        self.m_roll.reroll (game, investigator,
                            self.m_subject, self.m_skill_name)

class GameplayAction_FailRoll (GameplayAction):
    def __init__ (self):
        GameplayAction.__init__ (self, "fail check")

    def perform (self, game, investigator):
        raise arkham.EndPhase ()
