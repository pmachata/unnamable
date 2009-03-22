import fun
import arkham

class EndCombat (Exception):
    pass

# Fight hooks.  Monsters or investigators override these to achieve
# fine-grained customization or combat process.
trace = False # whether we want hook traces
fight_args = (arkham.Game, arkham.Investigator, arkham.Monster) # all the fight hooks have this prototype
fight_hook = fun.Function (name="fight_hook", trace=trace, *fight_args)
normal_fight_hook = fun.Function (name="normal_fight_hook", trace=trace, *fight_args)
horror_check_hook = fun.Function (name="horror_check_hook", trace=trace, *fight_args)
normal_horror_check_hook = fun.Function (name="normal_horror_check_hook", trace=trace, *fight_args)
horror_check_pass_hook = fun.Function (name="horror_check_pass_hook", trace=trace, *fight_args)
horror_check_fail_hook = fun.Function (name="horror_check_fail_hook", trace=trace, *fight_args)
deal_horror_damage_hook = fun.Function (name="deal_horror_damage_hook", trace=trace, *fight_args)
combat_loop_hook = fun.Function (name="combat_loop_hook", trace=trace, *fight_args)
combat_check_hook = fun.Function (name="combat_check_hook", trace=trace, *fight_args)
normal_combat_check_hook = fun.Function (name="normal_combat_check_hook", trace=trace, *fight_args)
combat_check_pass_hook = fun.Function (name="combat_check_pass_hook", trace=trace, *fight_args)
combat_check_fail_hook = fun.Function (name="combat_check_fail_hook", trace=trace, *fight_args)
deal_combat_damage_hook = fun.Function (name="deal_combat_damage_hook", trace=trace, *fight_args)

# Default behavior.
@fight_hook.match (fun.any, fun.any, fun.any)
def do (game, investigator, monster):
    normal_fight_hook (game, investigator, monster)

@normal_fight_hook.match (fun.any, fun.any, fun.any)
def do (game, investigator, monster):
    horror_check_hook (game, investigator, monster)
    combat_loop_hook (game, investigator, monster)

@horror_check_hook.match (fun.any, fun.any, fun.any)
def do (game, investigator, monster):
    normal_horror_check_hook (game, investigator, monster)

@normal_horror_check_hook.match (fun.any, fun.any, fun.any)
def do (game, investigator, monster):
    if monster.horror_check ().check (game, investigator):
        horror_check_pass_hook (game, investigator, monster)
    else:
        horror_check_fail_hook (game, investigator, monster)

@horror_check_pass_hook.match (fun.any, fun.any, fun.any)
def do (game, investigator, monster):
    pass

@horror_check_fail_hook.match (fun.any, fun.any, fun.any)
def do (game, investigator, monster):
    deal_horror_damage_hook (game, investigator, monster)

@deal_horror_damage_hook.match (fun.any, fun.any, fun.any)
def do (game, investigator, monster):
    monster.horror_damage ().deal (game, investigator, monster)

@combat_loop_hook.match (fun.any, fun.any, fun.any)
def do (game, investigator, monster):
    while not game.break_fight (investigator, monster):
        will = game.will_fight (investigator, monster)
        if will == 0:
            break
        elif will == 2:
            combat_check_hook (game, investigator, monster)

@combat_check_hook.match (fun.any, fun.any, fun.any)
def do (game, investigator, monster):
    normal_combat_check_hook (game, investigator, monster)

@normal_combat_check_hook.match (fun.any, fun.any, fun.any)
def do (game, investigator, monster):
    if monster.combat_check ().check (game, investigator):
        combat_check_pass_hook (game, investigator, monster)
    else:
        combat_check_fail_hook (game, investigator, monster)

@combat_check_pass_hook.match (fun.any, fun.any, fun.any)
def do (game, investigator, monster):
    raise EndCombat

@combat_check_fail_hook.match (fun.any, fun.any, fun.any)
def do (game, investigator, monster):
    deal_combat_damage_hook (game, investigator, monster)

@deal_combat_damage_hook.match (fun.any, fun.any, fun.any)
def do (game, investigator, monster):
    monster.combat_damage ().deal (game, investigator, monster)

# Overwhelming/Nightmarish modifiers.

@horror_check_pass_hook.match (fun.any, fun.any,
                               fun.bind (X = arkham.cond_bind_attrib ("nightmarish")))
def do (game, investigator, monster, **kwargs):
    investigator.reduce_sanity (kwargs["X"])

@combat_check_pass_hook.match (fun.any, fun.any,
                               fun.bind (X = arkham.cond_bind_attrib ("overwhelming")))
def do (game, investigator, monster, **kwargs):
    investigator.reduce_stamina (kwargs["X"])
