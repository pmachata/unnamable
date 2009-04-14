import fun
from investigator import Investigator, HealthAspect
from game import Game, Item
import conf

Subject = object # e.g. a monster, or a card that deals the damage
Amount = int

damage_trace = conf.trace # whether we want to trace hooks

deal_damage_hook = fun.Function \
    (Game, Investigator, Subject, HealthAspect, Amount,
     name="deal_damage_hook", trace=damage_trace)

@deal_damage_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, aspect, amount):
    # xxx more hooks that give bonuses or whatnot
    investigator.health (aspect).reduce (amount)
