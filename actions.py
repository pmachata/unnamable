import fun
from loc import *
from monster import *

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

class GameplayAction_Move (LocationBoundGameplayAction):
    def __init__ (self, location):
        LocationBoundGameplayAction.__init__ (self, location, "move")

    def perform (self, game, investigator):
        game.move_investigator (investigator, self.m_location)
        if investigator.movement_points () > 0:
            # He might have lost all movement points during the fight
            # after he tried to leave the current location.
            investigator.spend_movement_point ()

class GameplayAction_Stay (LocationBoundGameplayAction):
    def __init__ (self, location):
        LocationBoundGameplayAction.__init__ (self, location, "stay put")

    def perform (self, game, investigator):
        investigator.lose_movement_points ()
        raise EndPhase ()

class GameplayAction_Quit (GameplayAction):
    def __init__ (self):
        GameplayAction.__init__ (self, "quit the game")

    def perform (self, game, investigator):
        game.drop_investigator (investigator)

class GameplayAction_Evade (MonsterBoundGameplayAction):
    def __init__ (self, combat, monster):
        MonsterBoundGameplayAction.__init__ (self, monster, "evade")
        self.m_combat = combat

class GameplayAction_Evade_PreCombat (GameplayAction_Evade):
    def __init__ (self, *args):
        GameplayAction_Evade.__init__ (self, *args)

    def perform (self, game, investigator):
        import fight
        monster = self.m_monster
        fight.evade_check_hook (self.m_combat, investigator, monster)
        investigator.lose_movement_points ()
        raise fight.ContinueCombat () # Proceed with the combat.

class GameplayAction_Evade_Combat (GameplayAction_Evade):
    def __init__ (self, *args):
        GameplayAction_Evade.__init__ (self, *args)

    def perform (self, game, investigator):
        import fight
        monster = self.m_monster
        fight.evade_check_hook (self.m_combat, investigator, monster)

class GameplayAction_Fight (MonsterBoundGameplayAction):
    def __init__ (self, monster):
        MonsterBoundGameplayAction.__init__ (self, monster, "fight")

    def perform (self, game, investigator):
        import fight
        raise fight.ContinueCombat ()

class GameplayAction_DealWithMonster (MonsterBoundGameplayAction):
    def __init__ (self, monster):
        MonsterBoundGameplayAction.__init__ (self, monster, "deal with")

    def perform (self, game, investigator):
        print "dealing with %s" % self.m_monster.name ()
        game.fight (investigator, self.m_monster)
        print "combat finished"


from game import *
from investigator import *

roll_dice_hook = fun.Function (Game, Investigator, object)
dice_roll_successful_hook = fun.Function (Game, Investigator, object, int)

@roll_dice_hook.match (fun.any, fun.any, fun.any)
def do (game, investigator, skill):
    import random
    return dice_roll_successful_hook (game, investigator, skill,
                                      random.randint (1, 6))

@dice_roll_successful_hook.match (fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, skill, roll):
    return roll >= 5
