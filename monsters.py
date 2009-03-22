import arkham

# Specializations.  Will be in modules.


@horror_check_fail_hook.match (fun.any, fun.any, fun.matchattr (name = "The Skinless One"))
def do (game, investigator, monster):
    investigator.devour (game)

@combat_check_fail_hook.match (fun.any, fun.any, fun.matchattr (name = "The Skinless One"))
def do (game, investigator, monster):
    investigator.devour (game)

@combat_check_hook.match (fun.any, fun.matchattr (name = "Jim Culver"), fun.any)
def do (game, investigator, monster):
    if investigator.wants_to_spend_1_clue_token (game):
        return combat_check_pass_hook (game, investigator, monster)
    else:
        return normal_combat_check_hook (game, investigator, monster)

"""
horror_check_pass_hook = fun.Function (Game, Investigator, Monster)
@horror_check_pass_hook.match (fun.any, fun.any, *[nightmarish X])
def do (game, investigator, monster):
    investigator.reduce_sanity (X)

combat_check_pass_hook = fun.Function (Game, Investigator, Monster)
@combat_check_pass_hook.match (fun.any, fun.any, *[overwhelming X])
def do (game, investigator, monster):
    investigator.reduce_stamina (X)
    return True
"""

game = Game ()
pjotr = Investigator ("Pjotr", 6, 4,  4, 5, 3)
obluda = Monster ("Obluda", SkillCheck ("evade", -3),
                  SkillCheck ("horror", -3), DamageSanity (1),
                  SkillCheck ("fight", +1), DamageStamina (1))
if game.leave_location (pjotr, Location ([obluda])):
    print "you managed to leave the location"
