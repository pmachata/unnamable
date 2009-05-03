import fun
import conf
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

class EndCauseHarm (Exception):
    pass

# Combat context.  Hooks can put there arbitrary info, and it will get
# preserved throughout the whole combat.  On-combat-end actions can be
# registered here, and they are called when the combat ends.
class Combat:
    def __init__ (self, game):
        self.game = game
        self.m_ended = False
        self.m_on_end = []

    def check_ends (self, investigator, monster):
        if investigator.location () != monster.location ():
            raise EndCombat (None)
        if not investigator.alive ():
            raise EndCombat (False)

    def on_end (self, cb):
        self.m_on_end.append (cb)

    def end (self):
        assert self.m_ended == False
        self.m_ended = True
        for cb in self.m_on_end:
            cb ()

class FightHooks:
    def __init__ (self):
        # Combat hooks.  Monsters or investigators override these to achieve
        # fine-grained customization of combat process.
        trace = conf.trace # whether we want to trace hooks
        # all the combat hooks have this prototype
        fight_args = (Combat, arkham.Investigator, arkham.Monster)

        self.fight_hook = fun.Function \
            (name="fight_hook", trace=trace, *fight_args)

        self.normal_fight_hook = fun.Function \
            (name="normal_fight_hook", trace=trace, *fight_args)

        self.horror_check_hook = fun.Function \
            (name="horror_check_hook", trace=trace, *fight_args)

        self.normal_horror_check_hook = fun.Function \
            (name="normal_horror_check_hook", trace=trace, *fight_args)

        self.horror_check_pass_hook = fun.Function \
            (name="horror_check_pass_hook", trace=trace, *fight_args)

        self.horror_check_fail_hook = fun.Function \
            (name="horror_check_fail_hook", trace=trace, *fight_args)

        self.cause_horror_harm_hook = fun.Function \
            (name="cause_horror_harm_hook", trace=trace, *fight_args)

        self.combat_loop_hook = fun.Function \
            (name="combat_loop_hook", trace=trace, *fight_args)

        self.combat_check_hook = fun.Function \
            (name="combat_check_hook", trace=trace, *fight_args)

        self.normal_combat_check_hook = fun.Function \
            (name="normal_combat_check_hook", trace=trace, *fight_args)

        self.combat_check_pass_hook = fun.Function \
            (name="combat_check_pass_hook", trace=trace, *fight_args)

        self.normal_combat_check_pass_hook = fun.Function \
            (name="normal_combat_check_pass_hook", trace=trace, *fight_args)

        self.combat_check_fail_hook = fun.Function \
            (name="combat_check_fail_hook", trace=trace, *fight_args)

        self.normal_combat_check_fail_hook = fun.Function \
            (name="normal_combat_check_fail_hook", trace=trace, *fight_args)

        self.cause_combat_harm_hook = fun.Function \
            (name="cause_combat_harm_hook", trace=trace, *fight_args)

        self.cause_combat_harm_actions_hook = fun.Function \
            (Combat, arkham.Investigator, arkham.Monster,
             arkham.Item, arkham.Harm,
             name="cause_combat_harm_actions_hook", trace=trace)

        # Evade check hooks.
        self.evade_check_hook = fun.Function \
            (name="evade_check_hook", trace=trace, *fight_args)

        self.normal_evade_check_hook = fun.Function \
            (name="normal_evade_check_hook", trace=trace, *fight_args)

        self.pass_evade_check_hook = fun.Function \
            (name="pass_evade_check_hook", trace=trace, *fight_args)

        self.normal_pass_evade_check_hook = fun.Function \
            (name="normal_pass_evade_check_hook", trace=trace, *fight_args)

        self.fail_evade_check_hook = fun.Function \
            (name="fail_evade_check_hook", trace=trace, *fight_args)

        self.normal_fail_evade_check_hook = fun.Function \
            (name="normal_fail_evade_check_hook", trace=trace, *fight_args)

        # Combat resolution hooks.  These get called _if_ there is a clear
        # resolution.  Should the investigator flee, neither of these get
        # called.
        self.combat_won_hook = fun.Function \
            (name="combat_won_hook", trace=trace, *fight_args)

        self.normal_combat_won_hook = fun.Function \
            (name="normal_combat_won_hook", trace=trace, *fight_args)

        self.combat_lost_hook = fun.Function \
            (name="combat_lost_hook", trace=trace, *fight_args)

        self.normal_combat_lost_hook = fun.Function \
            (name="normal_combat_lost_hook", trace=trace, *fight_args)

        # Default behavior.
        @self.fight_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            combat.game.normal_fight_hook (combat, investigator, monster)

        @self.normal_fight_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            combat.game.horror_check_hook (combat, investigator, monster)
            combat.game.combat_loop_hook (combat, investigator, monster)

        @self.horror_check_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            combat.game.normal_horror_check_hook (combat, investigator, monster)

        @self.normal_horror_check_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            if monster.proto ().horror_check ().check \
                    (combat.game, investigator, monster):
                combat.game.horror_check_pass_hook \
                    (combat, investigator, monster)
            else:
                combat.game.horror_check_fail_hook \
                    (combat, investigator, monster)
            combat.check_ends (investigator, monster)

        @self.horror_check_pass_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            pass

        @self.horror_check_fail_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            combat.game.cause_horror_harm_hook (combat, investigator, monster)

        @self.cause_horror_harm_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            monster.proto ().horror_harm ()\
                .cause (combat.game, investigator, monster)

        @self.combat_loop_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            while True:
                try:
                    try:
                        while True:
                            # Several actions can be performed before the
                            # combat continues.
                            combat.check_ends (investigator, monster)
                            combat.game.combat_turn \
                                (combat, investigator, monster)

                    except ContinueCombat:
                        combat.check_ends (investigator, monster)
                        combat.game.combat_check_hook \
                            (combat, investigator, monster)

                except SucceedCombat:
                    # We want to catch also SucceedCombat raised within
                    # combat_check_hook, hence this composed try block.
                    combat.game.combat_check_pass_hook \
                        (combat, investigator, monster)

        @self.combat_check_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            combat.game.normal_combat_check_hook \
                (combat, investigator, monster)

        @self.normal_combat_check_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            if monster.combat_check () \
                    .check (combat.game, investigator, monster):
                combat.game.combat_check_pass_hook \
                    (combat, investigator, monster)
            else:
                combat.game.combat_check_fail_hook \
                    (combat, investigator, monster)

        @self.combat_check_pass_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            return combat.game.normal_combat_check_pass_hook \
                (combat, investigator, monster)

        @self.normal_combat_check_pass_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            raise EndCombat (True)

        @self.combat_check_fail_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            return combat.game.normal_combat_check_fail_hook \
                (combat, investigator, monster)

        @self.normal_combat_check_fail_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            combat.game.cause_combat_harm_hook \
                (combat, investigator, monster)

        @self.cause_combat_harm_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            harm = monster.proto ().combat_harm ()

            try:
                while True:
                    if harm.nil (combat.game, investigator, monster):
                        # Either no harm to begin with, or reduced out.
                        break

                    actions \
                        = sum ((combat.game.cause_combat_harm_actions_hook \
                                    (combat, investigator, monster, item, harm)
                                for item in investigator.wields_items ()),
                               investigator.cause_combat_harm_actions \
                                   (combat, monster, harm))
                    actions.append (arkham.GameplayAction_EndCauseHarmLoop (
                            arkham.GameplayAction_CauseHarm \
                                (combat.game, investigator, monster, harm)))
                    if not combat.game.perform_selected_action \
                            (investigator, actions):
                        break

            except EndCauseHarm:
                pass

        @self.cause_combat_harm_actions_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (combat, investigator, monster, item, harm):
            return []

        @self.combat_won_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            combat.game.normal_combat_won_hook (combat, investigator, monster)

        @self.normal_combat_won_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            investigator.claim_trophy (monster)
            combat.game.remove_monster (monster)

        @self.combat_lost_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            combat.game.normal_combat_lost_hook (combat, investigator, monster)

        @self.normal_combat_lost_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            if not investigator.alive ():
                combat.game.investigator_dead (investigator)

        @self.evade_check_hook.match  \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            combat.game.normal_evade_check_hook (combat, investigator, monster)

        @self.normal_evade_check_hook.match  \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            if monster.proto ().evade_check ()\
                    .check (combat.game, investigator, monster):
                combat.game.pass_evade_check_hook \
                    (combat, investigator, monster)
            else:
                combat.game.fail_evade_check_hook \
                    (combat, investigator, monster)

        @self.pass_evade_check_hook.match  \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            combat.game.normal_pass_evade_check_hook \
                (combat, investigator, monster)

        @self.fail_evade_check_hook.match  \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            combat.game.normal_fail_evade_check_hook \
                (combat, investigator, monster)

        @self.normal_pass_evade_check_hook.match  \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            raise EndCombat (None)

        @self.normal_fail_evade_check_hook.match  \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            combat.game.cause_combat_harm_hook (combat, investigator, monster)
            # Don't raise ContinueCombat, that should only be done if we want
            # to continue with combat check hook.  This should be done
            # externally in a (transitive) caller of this hook.

        # Overwhelming/Nightmarish modifiers.

        @self.horror_check_pass_hook.match \
            (fun.any, fun.any,
             arkham.has_special_ability (arkham.monster_nightmarish))
        def do (combat, investigator, monster):
            value = monster.special_ability_param (arkham.monster_nightmarish)
            investigator.health (arkham.health_sanity).reduce (value)

        @self.combat_check_pass_hook.match \
            (fun.any, fun.any,
             arkham.has_special_ability (arkham.monster_overwhelming))
        def do (combat, investigator, monster):
            value = monster.special_ability_param (arkham.monster_overwhelming)
            investigator.health (arkham.health_stamina).reduce (value)
            return combat.game.normal_combat_check_pass_hook \
                (combat, investigator, monster)


        # Endless monsters.

        self.endless_combat_won_hook = fun.Function \
            (name="endless_combat_won_hook", trace=trace, *fight_args)

        @self.endless_combat_won_hook.match \
            (fun.any, fun.any, fun.any)
        def do (combat, investigator, monster):
            print "monster is endless, put trophy to cup"
            combat.game.remove_monster (monster)
            monster.discard ()

        @self.combat_won_hook.match \
            (fun.any, fun.any,
             fun.or_ (arkham.match_flag ("endless"),
                      arkham.has_special_ability (arkham.monster_endless)))
        def do (combat, investigator, monster):
            combat.game.endless_combat_won_hook (combat, investigator, monster)
