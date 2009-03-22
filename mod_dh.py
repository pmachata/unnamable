import arkham
import fight
import fun

class Module (arkham.Module):
    def __init__ (self):
        arkham.Module.__init__ (self, "dh", "Dunwich Horror")

    def consistent (self, mod_index):
        return mod_index.request ("ah") != None

    def construct (self, game):

        @combat_check_pass_hook.match (fun.any, fun.any,
                                       arkham.match_attribute (child_of_abhoth = 1))
        def do (game, investigator, monster):
            print "If you pass a Combat check against Child Of Abhoth, you must discard 1 Spell or Weapon, if able."
            # XXX investigator.discard_yadda_yadda

        @horror_check_hook.match (fun.any, fun.any,
                                  arkham.match_attribute (child_of_abhoth = 2))
        def do (game, investigator, monster):
            print "Before you make a Horror check against Child Of Abhoth, you must discard 1 Clue token or automatically fail."
            if True: # XXX clue discarded
                normal_horror_check_hook (game, investigator, monster)
            else:
                horror_check_fail_hook (game, investigator, monster)

        @combat_check_hook.match (fun.any, fun.any,
                                  arkham.match_attribute (child_of_abhoth = 3))
        def do (game, investigator, monster):
            print "Before you make a Combat check against Child Of Abhoth, you must discard 1 Clue token or automatically fail."
            # every time, or just the first time around??
            if True: # XXX clue discarded...
                normal_combat_check_hook (game, investigator, monster)
            else:
                combat_check_fail_hook (game, investigator, monster)

        BasicMonster = arkham.BasicMonster
        for monster in [
            BasicMonster ("Child of Abhoth",
                          arkham.evade_check (+1),
                          arkham.horror_check (-2), arkham.DamageSanity (2),
                          arkham.fight_check (-2, 3), arkham.DamageStamina (2),
                          child_of_abhoth = 1),
            BasicMonster ("Child of Abhoth",
                          arkham.evade_check (+1),
                          arkham.horror_check (-2), arkham.DamageSanity (4),
                          arkham.fight_check (-1, 3), arkham.DamageStamina (2),
                          child_of_abhoth = 2),
            BasicMonster ("Child of Abhoth",
                          arkham.evade_check (+1),
                          arkham.horror_check (-1), arkham.DamageSanity (2),
                          arkham.fight_check (-2, 3), arkham.DamageStamina (4),
                          child_of_abhoth = 3)
            ]:
            game.register_monster (monster)

