import fun
from investigator import Investigator, HealthAspect
from game import Game, Item
from damage import Damage, Amount
from obj import Subject
import arkham

import conf

damage_trace = conf.trace # whether we want to trace hooks

damage_hook = fun.Function \
    (Game, Investigator, Subject, Damage,
     name="damage_hook", trace=damage_trace)

damage_correction_actions_hook = fun.Function \
    (Game, Investigator, Subject, Item, Damage,
     name="damage_correction_actions_hook", trace=damage_trace)

@damage_hook.match (fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, damage):
    try:
        while True:
            if len (damage.aspects ()) == 0:
                # i.e. the damage was probably reduced out, or was
                # zero to begin with
                break

            actions = sum ((damage_correction_actions_hook (game, investigator, subject, item, damage)
                            for item in investigator.wields_items ()), []) \
                            + investigator.damage_correction_actions (game, subject, damage)
            actions.append (arkham.GameplayAction_IncurDamage ())
            if not game.perform_selected_action (investigator, actions):
                break

    except arkham.EndPhase:
        pass

    damage.inflict (investigator)

@damage_correction_actions_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, damage):
    return []
