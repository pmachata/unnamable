import fun
import conf
import arkham
import obj

class EndCheck (Exception):
    def __init__ (self, success):
        self.m_success = success
    def success (self):
        return self.m_success

class CheckBase (obj.NamedObject):
    def __init__ (self, name, correctible):
        obj.NamedObject.__init__ (self, name)
        self.m_correctible = correctible

    def correctible (self):
        return self.m_correctible

class CheckBase_Skill (CheckBase):
    def __init__ (self, skill):
        CheckBase.__init__ (self, skill.name (), True)
        self.m_skill = skill

    def __repr__ (self):
        return "<CheckBase_Skill \"%s\">" % self.m_skill

class CheckBase_Fixed (CheckBase):
    def __init__ (self, value):
        CheckBase.__init__ (self, str (value), False)
        self.m_value = value

    def __repr__ (self):
        return "<CheckBase_Fixed %s>" % self.m_value

class CheckBase_Derived (CheckBase):
    def __init__ (self, name):
        CheckBase.__init__ (self, name, True)

    def __repr__ (self):
        return "<CheckBase_Derived \"%s\">" % self.name ()

checkbase_fight = CheckBase_Skill (arkham.skill_fight)
checkbase_lore = CheckBase_Skill (arkham.skill_lore)
checkbase_luck = CheckBase_Skill (arkham.skill_luck)
checkbase_sneak = CheckBase_Skill (arkham.skill_sneak)
checkbase_speed = CheckBase_Skill (arkham.skill_speed)
checkbase_will = CheckBase_Skill (arkham.skill_will)

checkbase_evade = CheckBase_Derived ("evade")
checkbase_horror = CheckBase_Derived ("horror")
checkbase_combat = CheckBase_Derived ("combat")
checkbase_spell = CheckBase_Derived ("spell")

class Roll:
    def __init__ (self, game, investigator, subject, check_base, modifier):
        self.m_roll = []
        self.m_orig_die = game.die_count_hook (game, investigator, subject,
                                               check_base, modifier)

    def reroll (self, game, investigator, subject, check_base):
        self.m_roll = []
        for _ in xrange (self.m_orig_die):
            self.add_roll (game, investigator, subject, check_base)

    def add_roll (self, game, investigator, subject, check_base):
        self.m_roll.append (game.one_dice_roll_hook (game, investigator,
                                                     subject, check_base))

    def roll (self):
        return list (self.m_roll)

class Family (obj.NamedObject):
    pass

family_indifferent = Family ("indifferent")
family_physical = Family ("physical")
family_magical = Family ("magical")

class Bonus:
    def __init__ (self, value, family):
        self.m_value = value
        self.m_family = family

    def value (self):
        return self.m_value

    def family (self):
        return self.m_family

    def set_family (self, family):
        self.m_family = family

    @classmethod
    def match_family (cls, family):
        def match (bonus):
            return bonus.family () == family
        return match

class ResistanceLevel (obj.NamedObject):
    def __init__ (self, name, modifier):
        obj.NamedObject.__init__ (self, name)
        self.m_modifier = modifier

    def modify (self, bonus):
        return Bonus (self.m_modifier (bonus.value ()), bonus.family ())

reslev_none = ResistanceLevel ("none", lambda val: val)
reslev_resistance = ResistanceLevel ("resistance", lambda val: val / 2)
reslev_immunity = ResistanceLevel ("immunity", lambda val: 0)

class CheckHooks:
    def __init__ (self, Game):
        skills_trace = conf.trace # whether we want to trace hooks

        self.skill_value_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase, list,
             name="skill_value_hook", trace=skills_trace)

        self.skill_value_bonus_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, arkham.Item,
             CheckBase, list,
             name="skill_value_bonus_hook", trace=skills_trace)

        self.skill_value_mod_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase, list, int,
             name="skill_value_mod_hook", trace=skills_trace)

        self.basic_skill_value_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase, list,
             name="basic_skill_value_hook", trace=skills_trace)

        self.basic_skill_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase,
             name="basic_skill_hook", trace=skills_trace)

        @self.skill_value_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base, primary_list):
            value = game.basic_skill_value_hook (game, investigator, subject,
                                                 check_base, primary_list)
            for item in investigator.wields_items ():
                # xxx make it the same algorithm used in check hooks.  In fact
                # refactor that algorithm, clear up the nomenclature (what's
                # basic value, what's per-item bonus, what's modifier, etc.)
                # and just call it from here.
                value += game.skill_value_bonus_hook \
                    (game, investigator, subject, item,
                     check_base, primary_list)
            return game.skill_value_mod_hook (game, investigator, subject,
                                              check_base, primary_list, value)

        @self.basic_skill_value_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base, primary_list):
            raise NotImplementedError ()

        @self.skill_value_bonus_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, item, check_base, primary_list):
            return 0

        @self.skill_value_mod_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base, primary_list, bonus):
            return bonus

        @self.basic_skill_value_hook.match \
            (fun.any, fun.any, fun.any,
             fun.matchclass (CheckBase_Skill), fun.any)
        def do (game, investigator, subject, check_base, primary_list):
            return investigator.skill (check_base.m_skill)

        @self.basic_skill_value_hook.match \
            (fun.any, fun.any, fun.any,
             fun.matchclass (CheckBase_Fixed), fun.any)
        def do (game, investigator, subject, check_base, primary_list):
            return check_base.m_value

        @self.basic_skill_value_hook.match \
            (fun.any, fun.any, fun.any,
             fun.matchclass (CheckBase_Derived), fun.any)
        def do (game, investigator, subject, check_base, primary_list):
            basic = game.basic_skill_hook \
                (game, investigator, subject, check_base)
            return game.skill_value_hook (game, investigator, subject,
                                          basic, [basic] + primary_list)

        @self.basic_skill_hook.match \
            (fun.any, fun.any, fun.any, fun.val == checkbase_evade)
        def do (game, investigator, subject, check_base):
            return arkham.checkbase_sneak

        @self.basic_skill_hook.match \
            (fun.any, fun.any, fun.any, fun.val == checkbase_horror)
        def do (game, investigator, subject, check_base):
            return arkham.checkbase_will

        @self.basic_skill_hook.match \
            (fun.any, fun.any, fun.any, fun.val == checkbase_combat)
        def do (game, investigator, subject, check_base):
            return arkham.checkbase_fight

        @self.basic_skill_hook.match \
            (fun.any, fun.any, fun.any, fun.val == checkbase_spell)
        def do (game, investigator, subject, check_base):
            return arkham.checkbase_lore

        check_trace = conf.trace # whether we want to trace hooks

        Difficulty = int
        Modifier = int
        Die = int # number of die to roll
        Dice = int # result on a given dice
        Successes = int

        self.die_count_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase, Modifier,
             name="die_count_hook", trace=check_trace)
        self.normal_die_count_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase, Modifier,
             name="normal_die_count_hook", trace=check_trace)

        self.perform_check_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject,
             CheckBase, Modifier, Difficulty,
             name="perform_check_hook", trace=check_trace)
        self.normal_perform_check_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject,
             CheckBase, Modifier, Difficulty,
             name="normal_perform_check_hook", trace=check_trace)

        self.perform_check_actions_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, arkham.Item,
             CheckBase, Modifier, Difficulty,
             name="perform_check_actions_hook", trace=check_trace)

        self.base_die_mod_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase, Modifier,
             name="base_die_mod_hook", trace=check_trace)

        self.base_modifier_mod_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase, Modifier,
             name="base_modifier_mod_hook", trace=check_trace)

        self.difficulty_mod_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase, Difficulty,
             name="difficulty_mod_hook", trace=check_trace)

        self.bonus_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, arkham.Item, CheckBase,
             name="bonus_hook", trace=check_trace, returns=Bonus)

        self.bonus_mod_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, arkham.Item,
             CheckBase, Bonus,
             name="bonus_mod_hook", trace=check_trace, returns=Bonus)

        self.total_bonus_mod_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase, Modifier,
             name="total_bonus_mod_hook", trace=check_trace)

        self.total_modifier_mod_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase, Modifier,
             name="total_modifier_mod_hook", trace=check_trace)

        self.total_die_mod_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase, Die,
             name="total_die_mod_hook", trace=check_trace)
        self.normal_total_die_mod_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase, Die,
             name="normal_total_die_mod_hook", trace=check_trace)

        self.one_dice_roll_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase,
             name="one_dice_roll_hook", trace=check_trace)
        self.normal_one_dice_roll_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase,
             name="normal_one_dice_roll_hook", trace=check_trace)

        self.dice_roll_successes_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase, Dice,
             name="dice_roll_successes_hook", trace=check_trace)
        self.normal_dice_roll_successes_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase, Dice,
             name="normal_dice_roll_successes_hook", trace=check_trace)

        self.dice_roll_successes_bonus_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, arkham.Item,
             CheckBase, Dice,
             name="dice_roll_successes_bonus_hook", trace=check_trace)

        self.dice_roll_successes_bonus_mod_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, arkham.Item,
             CheckBase, Successes,
             name="dice_roll_successes_bonus_mod_hook", trace=check_trace)

        self.dice_roll_successes_mod_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase, Successes,
             name="dice_roll_successes_mod_hook", trace=check_trace)

        self.total_dice_roll_successes_mod_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, CheckBase, Successes,
             name="total_dice_roll_successes_mod_hook", trace=check_trace)

        self.item_after_use_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, arkham.Item, CheckBase,
             name="item_after_use_hook", trace=check_trace,
             returns=arkham.GameplayAction)

        self.check_correction_actions_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, arkham.Item,
             CheckBase, Roll,
             name="check_correction_actions_hook", trace=check_trace)

        self.spend_clue_token_actions_hook = fun.Function \
            (Game, arkham.Investigator, arkham.Subject, arkham.Item, CheckBase,
             name="spend_clue_token_actions_hook", trace=check_trace)

        @self.die_count_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base, modifier):
            return game.normal_die_count_hook (game, investigator, subject,
                                               check_base, modifier)

        @self.normal_die_count_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base, modifier):
            skill_value = game.skill_value_hook \
                (game, investigator, subject, check_base, [])
            die = game.base_die_mod_hook \
                (game, investigator, subject, check_base, skill_value)
            modifier = game.base_modifier_mod_hook \
                (game, investigator, subject, check_base, modifier)

            bonus = 0
            for item in investigator.wields_items ():
                i_bonus = game.bonus_hook \
                    (game, investigator, subject, item, check_base)
                bonus += game.bonus_mod_hook \
                    (game, investigator, subject, item, check_base, i_bonus) \
                    .value ()

            modifier += game.total_bonus_mod_hook \
                (game, investigator, subject, check_base, bonus)
            modifier = game.total_modifier_mod_hook \
                (game, investigator, subject, check_base, modifier)
            die = game.total_die_mod_hook \
                (game, investigator, subject, check_base, die + modifier)

            return die


        @self.perform_check_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base, modifier, difficulty):
            try:
                while True:
                    actions = sum ((game.perform_check_actions_hook \
                                        (game, investigator, subject, item,
                                         check_base, modifier, difficulty)
                                    for item in investigator.wields_items ()),
                                   investigator.perform_check_actions \
                                       (game, subject, check_base))
                    actions.append (arkham.GameplayAction_NormalCheckHook \
                                        (game, investigator, subject,
                                         check_base, modifier, difficulty))
                    if not game.perform_selected_action (investigator, actions):
                        break

            except EndCheck, e:
                return e.success ()

        @self.normal_perform_check_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base, modifier, difficulty):

            roll = Roll (game, investigator, subject, check_base, modifier)
            roll.reroll (game, investigator, subject, check_base)

            difficulty = game.difficulty_mod_hook \
                (game, investigator, subject, check_base, difficulty)

            try:
                while True:
                    successes = 0
                    for dice in roll.roll ():
                        r_successes = game.dice_roll_successes_hook \
                            (game, investigator, subject, check_base, dice)

                        # xxx Note: by having bonus_hook and bonus_mod_hook,
                        # we make it possible for items to specialize the
                        # first hook, and e.g. monsters specialize the second.
                        # On the other hand, this doesn't allow item x item
                        # influences.  Perhaps should be fixed.
                        for item in investigator.wields_items ():
                            b_successes = game.dice_roll_successes_bonus_hook \
                                (game, investigator, subject, item,
                                 check_base, dice)
                            r_successes += \
                                game.dice_roll_successes_bonus_mod_hook \
                                (game, investigator, subject, item,
                                 check_base, b_successes)

                        successes += game.dice_roll_successes_mod_hook \
                            (game, investigator, subject,
                             check_base, r_successes)

                    successes = game.total_dice_roll_successes_mod_hook \
                        (game, investigator, subject, check_base, successes)

                    for item in investigator.wields_items ():
                        game.item_after_use_hook \
                            (game, investigator, subject, item, check_base) \
                            .perform (game, investigator)

                    ret = successes >= difficulty

                    # xxx This needs to be passed over to UI as some sort of
                    # event description object.
                    print "%s check %s, %s/%s successes with roll %s"\
                        % (check_base.name (),
                           "passed" if ret else "failed",
                           successes, difficulty,
                           # I'd love to use unicode die faces, but while
                           # cute, that's just not practical.
                           ",".join (str (dice) for dice in roll.roll ()))

                    if successes >= difficulty or not check_base.correctible ():
                        print "success"
                        # No need to modify the roll.
                        break

                    actions = sum ((game.check_correction_actions_hook \
                                        (game, investigator, subject, item,
                                         check_base, roll)
                                    for item in investigator.wields_items ()),
                                   investigator.check_correction_actions \
                                       (game, subject, check_base, roll))
                    actions.append (arkham.GameplayAction_FailRoll ())
                    if not game.perform_selected_action (investigator, actions):
                        break

            except arkham.EndPhase:
                pass

            return ret

        @self.perform_check_actions_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, item, check_base,
                modifier, difficulty):
            return []

        @self.base_die_mod_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base, modifier):
            return modifier

        @self.base_modifier_mod_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base, modifier):
            return modifier

        @self.difficulty_mod_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base, difficulty):
            return difficulty

        @self.bonus_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, item, check_base):
            return Bonus (0, family_indifferent)

        @self.bonus_mod_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, item, check_base, bonus):
            return bonus

        @self.total_bonus_mod_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base, modifier):
            return modifier

        @self.total_modifier_mod_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base, modifier):
            return modifier


        @self.total_die_mod_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base, die):
            return game.normal_total_die_mod_hook \
                (game, investigator, subject, check_base, die)

        @self.normal_total_die_mod_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base, die):
            return die


        @self.one_dice_roll_hook.match \
            (fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base):
            return game.normal_one_dice_roll_hook \
                (game, investigator, subject, check_base)

        @self.normal_one_dice_roll_hook.match \
            (fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base):
            # Six-sided dice is so entrenched in the system, that we
            # can hopefully assume that no expansion will replace
            # that.
            import random
            return random.randint (1, 6)


        @self.dice_roll_successes_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base, roll):
            return game.normal_dice_roll_successes_hook \
                (game, investigator, subject, check_base, roll)

        @self.normal_dice_roll_successes_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base, roll):
            if roll >= 5:
                return 1
            else:
                return 0


        @self.dice_roll_successes_bonus_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, item, check_base, dice):
            return 0

        @self.dice_roll_successes_bonus_mod_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, item, check_base, roll):
            return roll

        @self.dice_roll_successes_mod_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base, successes):
            return successes

        @self.total_dice_roll_successes_mod_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, check_base, successes):
            return successes

        @self.item_after_use_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, item, check_base):
            return arkham.GameplayAction ("")

        @self.check_correction_actions_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, item, check_base, roll):
            return []

        @self.spend_clue_token_actions_hook.match \
            (fun.any, fun.any, fun.any, fun.any, fun.any)
        def do (game, investigator, subject, item, check_base):
            return []


        # Resistances and immunities -- combat check only

        @self.bonus_mod_hook.match \
            (fun.any, fun.any,
             lambda subject: len (subject.resistances ()) > 0,
             fun.any, fun.val == checkbase_combat,
             fun.not_ (Bonus.match_family (family_indifferent)))
        def do (game, investigator, subject, item, check_base, bonus):
            fam = bonus.family ()
            ress = subject.resistances ()
            if fam in ress:
                return ress[fam].modify (bonus)
            else:
                return bonus
