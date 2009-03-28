import fun
import arkham

class EndCombat (Exception):
    def __init__ (self, success):
        self.m_success = success
    def success (self):
        return self.m_success

# Combat hooks.  Monsters or investigators override these to achieve
# fine-grained customization of combat process.
trace = True or arkham.trace # whether we want to trace hooks
fight_args = (arkham.Combat, arkham.Investigator, arkham.Monster) # all the combat hooks have this prototype

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
    if monster.horror_check ().check (combat.game, investigator):
        horror_check_pass_hook (combat, investigator, monster)
    else:
        horror_check_fail_hook (combat, investigator, monster)

@horror_check_pass_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    pass

@horror_check_fail_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    deal_horror_damage_hook (combat, investigator, monster)

@deal_horror_damage_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    monster.horror_damage ().deal (combat.game, investigator, monster)

@combat_loop_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    while not combat.game.break_fight (investigator, monster):
        will = combat.game.will_fight (combat, investigator, monster)
        if will == 0:
            break
        elif will == 2:
            combat_check_hook (combat, investigator, monster)

@combat_check_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    normal_combat_check_hook (combat, investigator, monster)

@normal_combat_check_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    if monster.combat_check ().check (combat.game, investigator):
        combat_check_pass_hook (combat, investigator, monster)
    else:
        combat_check_fail_hook (combat, investigator, monster)

@combat_check_pass_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    raise EndCombat (True)

@combat_check_fail_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    deal_combat_damage_hook (combat, investigator, monster)

@deal_combat_damage_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    monster.combat_damage ().deal (combat.game, investigator, monster)

@combat_won_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    normal_combat_won_hook (combat, investigator, monster)

@normal_combat_won_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    investigator.claim_trophy (monster)
    combat.game.remove_monster (monster, monster.location ())

@combat_lost_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    normal_combat_lost_hook (combat, investigator, monster)

@normal_combat_lost_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    pass

# Overwhelming/Nightmarish modifiers.

@horror_check_pass_hook.match (fun.any, fun.any,
                               fun.bind (X = arkham.cond_bind_attrib ("nightmarish")))
def do (combat, investigator, monster, **kwargs):
    investigator.reduce_sanity (kwargs["X"])

@combat_check_pass_hook.match (fun.any, fun.any,
                               fun.bind (X = arkham.cond_bind_attrib ("overwhelming")))
def do (combat, investigator, monster, **kwargs):
    investigator.reduce_stamina (kwargs["X"])


# Endless monsters.
endless_combat_won_hook = fun.Function (name="endless_combat_won_hook", trace=trace, *fight_args)

@endless_combat_won_hook.match (fun.any, fun.any, fun.any)
def do (combat, investigator, monster):
    print "monster is endless, put trophy to cup"
    combat.game.remove_monster (monster, monster.location ())
    combat.game.put_monster_in_cup (monster)

@combat_won_hook.match (fun.any, fun.any, arkham.match_flag ("endless"))
def do (combat, investigator, monster):
    endless_combat_won_hook (combat, investigator, monster)
