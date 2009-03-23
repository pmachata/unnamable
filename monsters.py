# Odds and ends.  Will be in apropriate modules later.

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
