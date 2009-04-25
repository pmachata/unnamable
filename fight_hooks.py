import fun
import conf
from investigator import Investigator
from game import Monster
from obj import cond_bind_attrib, match_flag
import arkham

class EndCombat (Exception):
    # Success is True if the investigator killed the monster, False if
    # the monster killed the investigator, or None, if the
    # investigator managed to flee.
    def __init__ (self, success):
        self.m_success = success
    def success (self):
        return self.m_success

class ContinueCombat (Exception):
    pass

class SucceedCombat (Exception):
    pass

# Combat context.  Hooks can put there arbitrary info, and it will get
# preserved throughout the whole combat.
class Combat:
    def __init__ (self, game):
        self.game = game

    def check_ends (self, investigator, monster):
        if investigator.location () != monster.location ():
            raise EndCombat (None)
        if not investigator.alive ():
            raise EndCombat (False)

# Combat hooks.  Monsters or investigators override these to achieve
# fine-grained customization of combat process.
trace = conf.trace # whether we want to trace hooks
fight_args = (Combat, Investigator, Monster) # all the combat hooks have this prototype

fight_hook = fun.Function (name="fight_hook", trace=trace, *fight_args)
normal_fight_hook = fun.Function (name="normal_fight_hook", trace=trace, *fight_args)
horror_check_hook = fun.Function (name="horror_check_hook", trace=trace, *fight_args)
normal_horror_check_hook = fun.Function (name="normal_horror_check_hook", trace=trace, *fight_args)
horror_check_pass_hook = fun.Function (name="horror_check_pass_hook", trace=trace, *fight_args)
horror_check_fail_hook = fun.Function (name="horror_check_fail_hook", trace=trace, *fight_args)
cause_horror_harm_hook = fun.Function (name="cause_horror_harm_hook", trace=trace, *fight_args)
combat_loop_hook = fun.Function (name="combat_loop_hook", trace=trace, *fight_args)
combat_check_hook = fun.Function (name="combat_check_hook", trace=trace, *fight_args)
normal_combat_check_hook = fun.Function (name="normal_combat_check_hook", trace=trace, *fight_args)
combat_check_pass_hook = fun.Function (name="combat_check_pass_hook", trace=trace, *fight_args)
normal_combat_check_pass_hook = fun.Function (name="normal_combat_check_pass_hook", trace=trace, *fight_args)
combat_check_fail_hook = fun.Function (name="combat_check_fail_hook", trace=trace, *fight_args)
normal_combat_check_fail_hook = fun.Function (name="normal_combat_check_fail_hook", trace=trace, *fight_args)
cause_combat_harm_hook = fun.Function (name="cause_combat_harm_hook", trace=trace, *fight_args)

# Evade check hooks.
evade_check_hook = fun.Function (name="evade_check_hook", trace=trace, *fight_args)
normal_evade_check_hook = fun.Function (name="normal_evade_check_hook", trace=trace, *fight_args)
pass_evade_check_hook = fun.Function (name="pass_evade_check_hook", trace=trace, *fight_args)
normal_pass_evade_check_hook = fun.Function (name="normal_pass_evade_check_hook", trace=trace, *fight_args)
fail_evade_check_hook = fun.Function (name="fail_evade_check_hook", trace=trace, *fight_args)
normal_fail_evade_check_hook = fun.Function (name="normal_fail_evade_check_hook", trace=trace, *fight_args)

# Combat resolution hooks.  These get called _if_ there is a clear
# resolution.  Should the investigator flee, neither of these get
# called.
combat_won_hook = fun.Function (name="combat_won_hook", trace=trace, *fight_args)
normal_combat_won_hook = fun.Function (name="normal_combat_won_hook", trace=trace, *fight_args)
combat_lost_hook = fun.Function (name="combat_lost_hook", trace=trace, *fight_args)
normal_combat_lost_hook = fun.Function (name="normal_combat_lost_hook", trace=trace, *fight_args)

# Default behavior.
@fight_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    normal_fight_hook (combat, investigator, monster)

@normal_fight_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    horror_check_hook (combat, investigator, monster)
    combat_loop_hook (combat, investigator, monster)

@horror_check_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    normal_horror_check_hook (combat, investigator, monster)

@normal_horror_check_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    if monster.proto ().horror_check ().check (combat.game, investigator, monster):
        horror_check_pass_hook (combat, investigator, monster)
    else:
        horror_check_fail_hook (combat, investigator, monster)
    combat.check_ends (investigator, monster)

@horror_check_pass_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    pass

@horror_check_fail_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    cause_horror_harm_hook (combat, investigator, monster)

@cause_horror_harm_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    monster.proto ().horror_harm ().cause (combat.game, investigator, monster)

@combat_loop_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    while True:
        try:
            try:
                while True:
                    # Several actions can be performed before the
                    # combat continues.
                    combat.check_ends (investigator, monster)
                    combat.game.combat_turn (combat, investigator, monster)

            except ContinueCombat:
                combat.check_ends (investigator, monster)
                combat_check_hook (combat, investigator, monster)

        except SucceedCombat:
            # We want to catch also SucceedCombat raised within
            # combat_check_hook, hence this composed try block.
            combat_check_pass_hook (combat, investigator, monster)

@combat_check_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    normal_combat_check_hook (combat, investigator, monster)

@normal_combat_check_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    if monster.proto ().combat_check ().check (combat.game, investigator, monster):
        combat_check_pass_hook (combat, investigator, monster)
    else:
        combat_check_fail_hook (combat, investigator, monster)

@combat_check_pass_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    return normal_combat_check_pass_hook (combat, investigator, monster)

@normal_combat_check_pass_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    raise EndCombat (True)

@combat_check_fail_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    return normal_combat_check_fail_hook (combat, investigator, monster)

@normal_combat_check_fail_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    cause_combat_harm_hook (combat, investigator, monster)

@cause_combat_harm_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    monster.proto ().combat_harm ().cause (combat.game, investigator, monster)

@combat_won_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    normal_combat_won_hook (combat, investigator, monster)

@normal_combat_won_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    investigator.claim_trophy (monster)
    combat.game.remove_monster (monster)

@combat_lost_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    normal_combat_lost_hook (combat, investigator, monster)

@normal_combat_lost_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    if not investigator.alive ():
        combat.game.investigator_dead (investigator)

@evade_check_hook.match  (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    normal_evade_check_hook (combat, investigator, monster)

@normal_evade_check_hook.match  (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    if monster.proto ().evade_check ().check (combat.game, investigator, monster):
        pass_evade_check_hook (combat, investigator, monster)
    else:
        fail_evade_check_hook (combat, investigator, monster)

@pass_evade_check_hook.match  (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    normal_pass_evade_check_hook (combat, investigator, monster)

@fail_evade_check_hook.match  (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    normal_fail_evade_check_hook (combat, investigator, monster)

@normal_pass_evade_check_hook.match  (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    raise EndCombat (None)

@normal_fail_evade_check_hook.match  (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    cause_combat_harm_hook (combat, investigator, monster)
    # Don't raise ContinueCombat, that should only be done if we want
    # to continue with combat check hook.  This should be done
    # externally in a (transitive) caller of this hook.

# Overwhelming/Nightmarish modifiers.

@horror_check_pass_hook.match (fun.any, fun.any,
                               fun.bind (X = cond_bind_attrib ("nightmarish")))
def do (combat, investigator, monster):
    investigator.health (arkham.health_sanity).reduce (X)
    return normal_horror_check_pass_hook (combat, investigator, monster)

@combat_check_pass_hook.match (fun.any, fun.any,
                               fun.bind (X = cond_bind_attrib ("overwhelming")))
def do (combat, investigator, monster):
    investigator.health (arkham.health_stamina).reduce (X)
    return normal_combat_check_pass_hook (combat, investigator, monster)


# Endless monsters.

endless_combat_won_hook = fun.Function (name="endless_combat_won_hook", trace=trace, *fight_args)

@endless_combat_won_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    print "monster is endless, put trophy to cup"
    combat.game.remove_monster (monster)
    monster.discard ()

@combat_won_hook.match (fun.any, fun.any, match_flag ("endless"))
def do (combat, investigator, monster):
    endless_combat_won_hook (combat, investigator, monster)
