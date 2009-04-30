import fun
from investigator import Investigator
from game import Game, Item, with_proto
from obj import Subject, match_attribute, match_flag
import conf
import arkham

class EndCheck (Exception):
    def __init__ (self, success):
        self.m_success = success
    def success (self):
        return self.m_success

class CheckBase:
    def __init__ (self, name, correctible):
        self.m_name = name
        self.m_correctible = correctible

    def name (self):
        return self.m_name

    def correctible (self):
        return self.m_correctible

skills_trace = conf.trace # whether we want to trace hooks

skill_value_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase, list,
     name="skill_value_hook", trace=skills_trace)

skill_value_bonus_hook = fun.Function \
    (Game, Investigator, Subject, Item, CheckBase, list,
     name="skill_value_bonus_hook", trace=skills_trace)

skill_value_mod_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase, list, int,
     name="skill_value_mod_hook", trace=skills_trace)

basic_skill_value_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase, list,
     name="basic_skill_value_hook", trace=skills_trace)

basic_skill_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase,
     name="basic_skill_hook", trace=skills_trace)

@skill_value_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base, primary_list):
    value = basic_skill_value_hook (game, investigator, subject, check_base, primary_list)
    for item in investigator.wields_items ():
        # xxx make it the same algorithm used in check hooks.  In fact
        # refactor that algorithm, clear up the nomenclature (what's
        # basic value, what's per-item bonus, what's modifier, etc.)
        # and just call it from here.
        value += skill_value_bonus_hook (game, investigator, subject, item, check_base, primary_list)
    return skill_value_mod_hook (game, investigator, subject, check_base, primary_list, value)

@basic_skill_value_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base, primary_list):
    raise NotImplementedError ()

@skill_value_bonus_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, check_base, primary_list):
    return 0

@skill_value_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base, primary_list, bonus):
    return bonus


class CheckBase_Skill (CheckBase):
    def __init__ (self, skill):
        CheckBase.__init__ (self, skill.name (), True)
        self.m_skill = skill

    def __repr__ (self):
        return "<CheckBase_Skill \"%s\">" % self.m_skill

@basic_skill_value_hook.match \
    (fun.any, fun.any, fun.any, fun.matchclass (CheckBase_Skill), fun.any)
def do (game, investigator, subject, check_base, primary_list):
    return investigator.skill (check_base.m_skill)

checkbase_fight = CheckBase_Skill (arkham.skill_fight)
checkbase_lore = CheckBase_Skill (arkham.skill_lore)
checkbase_luck = CheckBase_Skill (arkham.skill_luck)
checkbase_sneak = CheckBase_Skill (arkham.skill_sneak)
checkbase_speed = CheckBase_Skill (arkham.skill_speed)
checkbase_will = CheckBase_Skill (arkham.skill_will)

class CheckBase_Fixed (CheckBase):
    def __init__ (self, value):
        CheckBase.__init__ (self, str (value), False)
        self.m_value = value

    def __repr__ (self):
        return "<CheckBase_Fixed %s>" % self.m_value

@basic_skill_value_hook.match \
    (fun.any, fun.any, fun.any, fun.matchclass (CheckBase_Fixed), fun.any)
def do (game, investigator, subject, check_base, primary_list):
    return check_base.m_value

class CheckBase_Derived (CheckBase):
    def __init__ (self, name):
        CheckBase.__init__ (self, name, True)

    def __repr__ (self):
        return "<CheckBase_Derived \"%s\">" % self.name ()

@basic_skill_value_hook.match \
    (fun.any, fun.any, fun.any, fun.matchclass (CheckBase_Derived), fun.any)
def do (game, investigator, subject, check_base, primary_list):
    basic = basic_skill_hook (game, investigator, subject, check_base)
    return skill_value_hook (game, investigator, subject,
                             basic, [basic] + primary_list)

checkbase_evade = CheckBase_Derived ("evade")
checkbase_horror = CheckBase_Derived ("horror")
checkbase_combat = CheckBase_Derived ("combat")
checkbase_spell = CheckBase_Derived ("spell")

@basic_skill_hook.match (fun.any, fun.any, fun.any,
                         fun.val == checkbase_evade)
def do (game, investigator, subject, check_base):
    return arkham.checkbase_sneak

@basic_skill_hook.match (fun.any, fun.any, fun.any,
                         fun.val == checkbase_horror)
def do (game, investigator, subject, check_base):
    return arkham.checkbase_will

@basic_skill_hook.match (fun.any, fun.any, fun.any,
                         fun.val == checkbase_combat)
def do (game, investigator, subject, check_base):
    return arkham.checkbase_fight

@basic_skill_hook.match (fun.any, fun.any, fun.any,
                         fun.val == checkbase_spell)
def do (game, investigator, subject, check_base):
    return arkham.checkbase_lore

class Roll:
    def __init__ (self, game, investigator, subject, check_base, modifier):
        self.m_roll = []
        self.m_orig_die = die_count_hook (game, investigator, subject,
                                          check_base, modifier)

    def reroll (self, game, investigator, subject, check_base):
        self.m_roll = []
        for _ in xrange (self.m_orig_die):
            self.add_roll (game, investigator, subject, check_base)

    def add_roll (self, game, investigator, subject, check_base):
        self.m_roll.append (one_dice_roll_hook (game, investigator,
                                                subject, check_base))

    def roll (self):
        return list (self.m_roll)

check_trace = conf.trace # whether we want to trace hooks

Difficulty = int
Modifier = int
Die = int # number of die to roll
Dice = int # result on a given dice
Successes = int

class Family:
    def __init__ (self, name):
        self.m_name = name

    def name (self):
        return self.m_name

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

class ResistanceLevel:
    def __init__ (self, name, modifier):
        self.m_name = name
        self.m_modifier = modifier

    def name (self):
        return self.m_name

    def modify (self, bonus):
        return Bonus (self.m_modifier (bonus.value ()), bonus.family ())

reslev_none = ResistanceLevel ("none", lambda val: val)
reslev_resistance = ResistanceLevel ("resistance", lambda val: val / 2)
reslev_immunity = ResistanceLevel ("immunity", lambda val: 0)

die_count_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase, Modifier,
     name="die_count_hook", trace=check_trace)
normal_die_count_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase, Modifier,
     name="normal_die_count_hook", trace=check_trace)

perform_check_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase, Modifier, Difficulty,
     name="perform_check_hook", trace=check_trace)

normal_perform_check_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase, Modifier, Difficulty,
     name="normal_perform_check_hook", trace=check_trace)

perform_check_actions_hook = fun.Function \
    (Game, Investigator, Subject, Item, CheckBase, Modifier, Difficulty,
     name="perform_check_actions_hook", trace=check_trace)

base_die_mod_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase, Modifier,
     name="base_die_mod_hook", trace=check_trace)

base_modifier_mod_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase, Modifier,
     name="base_modifier_mod_hook", trace=check_trace)

difficulty_mod_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase, Difficulty,
     name="difficulty_mod_hook", trace=check_trace)

bonus_hook = fun.Function \
    (Game, Investigator, Subject, Item, CheckBase,
     name="bonus_hook", trace=check_trace, returns=Bonus)

bonus_mod_hook = fun.Function \
    (Game, Investigator, Subject, Item, CheckBase, Bonus,
     name="bonus_mod_hook", trace=check_trace, returns=Bonus)

total_bonus_mod_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase, Modifier,
     name="total_bonus_mod_hook", trace=check_trace)

total_modifier_mod_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase, Modifier,
     name="total_modifier_mod_hook", trace=check_trace)

total_die_mod_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase, Die,
     name="total_die_mod_hook", trace=check_trace)
normal_total_die_mod_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase, Die,
     name="normal_total_die_mod_hook", trace=check_trace)

one_dice_roll_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase,
     name="one_dice_roll_hook", trace=check_trace)
normal_one_dice_roll_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase,
     name="normal_one_dice_roll_hook", trace=check_trace)

dice_roll_successes_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase, Dice,
     name="dice_roll_successes_hook", trace=check_trace)
normal_dice_roll_successes_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase, Dice,
     name="normal_dice_roll_successes_hook", trace=check_trace)

dice_roll_successes_bonus_hook = fun.Function \
    (Game, Investigator, Subject, Item, CheckBase, Dice,
     name="dice_roll_successes_bonus_hook", trace=check_trace)

dice_roll_successes_bonus_mod_hook = fun.Function \
    (Game, Investigator, Subject, Item, CheckBase, Successes,
     name="dice_roll_successes_bonus_mod_hook", trace=check_trace)

dice_roll_successes_mod_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase, Successes,
     name="dice_roll_successes_mod_hook", trace=check_trace)

total_dice_roll_successes_mod_hook = fun.Function \
    (Game, Investigator, Subject, CheckBase, Successes,
     name="total_dice_roll_successes_mod_hook", trace=check_trace)

item_after_use_hook = fun.Function \
    (Game, Investigator, Subject, Item, CheckBase,
     name="item_after_use_hook", trace=check_trace,
     returns=arkham.GameplayAction)

check_correction_actions_hook = fun.Function \
    (Game, Investigator, Subject, Item, CheckBase, Roll,
     name="check_correction_actions_hook", trace=check_trace)

spend_clue_token_actions_hook = fun.Function \
    (Game, Investigator, Subject, Item, CheckBase,
     name="spend_clue_token_actions_hook", trace=check_trace)

@die_count_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base, modifier):
    return normal_die_count_hook (game, investigator, subject, check_base, modifier)

@normal_die_count_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base, modifier):
    skill_value = skill_value_hook (game, investigator, subject, check_base, [])
    die = base_die_mod_hook (game, investigator, subject, check_base, skill_value)
    modifier = base_modifier_mod_hook (game, investigator, subject, check_base, modifier)

    bonus = 0
    for item in investigator.wields_items (): # includes skill cards, spells, weapons, etc.
        i_bonus = bonus_hook \
            (game, investigator, subject, item, check_base)
        bonus += bonus_mod_hook \
            (game, investigator, subject, item, check_base, i_bonus).value ()

    modifier += total_bonus_mod_hook (game, investigator, subject, check_base, bonus)
    modifier = total_modifier_mod_hook (game, investigator, subject, check_base, modifier)
    die = total_die_mod_hook (game, investigator, subject, check_base, die + modifier)

    return die


@perform_check_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base, modifier, difficulty):
    try:
        while True:
            actions = sum ((perform_check_actions_hook \
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

@normal_perform_check_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base, modifier, difficulty):

    roll = Roll (game, investigator, subject, check_base, modifier)
    roll.reroll (game, investigator, subject, check_base)

    difficulty = difficulty_mod_hook \
        (game, investigator, subject, check_base, difficulty)

    try:
        while True:
            successes = 0
            for dice in roll.roll ():
                r_successes = dice_roll_successes_hook \
                    (game, investigator, subject, check_base, dice)

                # xxx Note: by having bonus_hook and bonus_mod_hook,
                # we make it possible for items to specialize the
                # first hook, and e.g. monsters specialize the second.
                # On the other hand, this doesn't allow item x item
                # influences.  Perhaps should be fixed.
                for item in investigator.wields_items ():
                    b_successes = dice_roll_successes_bonus_hook \
                        (game, investigator, subject, item, check_base, dice)
                    r_successes += dice_roll_successes_bonus_mod_hook \
                        (game, investigator, subject, item,
                         check_base, b_successes)

                successes += dice_roll_successes_mod_hook \
                    (game, investigator, subject, check_base, r_successes)

            successes = total_dice_roll_successes_mod_hook \
                (game, investigator, subject, check_base, successes)

            for item in investigator.wields_items ():
                item_after_use_hook (game, investigator, subject,
                                     item, check_base) \
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

            actions = sum ((check_correction_actions_hook (game, investigator, subject, item, check_base, roll)
                            for item in investigator.wields_items ()), []) \
                            + investigator.check_correction_actions (game, subject, check_base, roll)
            actions.append (arkham.GameplayAction_FailRoll ())
            if not game.perform_selected_action (investigator, actions):
                break

    except arkham.EndPhase:
        pass

    return ret

@perform_check_actions_hook.match \
    (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, check_base, modifier, difficulty):
    return []

@base_die_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base, modifier):
    return modifier

@base_modifier_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base, modifier):
    return modifier

@difficulty_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base, difficulty):
    return difficulty

@bonus_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, check_base):
    return Bonus (0, family_indifferent)

@bonus_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, check_base, bonus):
    return bonus

@total_bonus_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base, modifier):
    return modifier

@total_modifier_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base, modifier):
    return modifier


@total_die_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base, die):
    return normal_total_die_mod_hook (game, investigator, subject, check_base, die)

@normal_total_die_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base, die):
    return die


@one_dice_roll_hook.match (fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base):
    return normal_one_dice_roll_hook (game, investigator, subject, check_base)

@normal_one_dice_roll_hook.match (fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base):
    # Six-sided dice is so entrenched in the system, that we
    # can hopefully assume that no expansion will replace
    # that.
    import random
    return random.randint (1, 6)


@dice_roll_successes_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base, roll):
    return normal_dice_roll_successes_hook (game, investigator, subject, check_base, roll)

@normal_dice_roll_successes_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base, roll):
    if roll >= 5:
        return 1
    else:
        return 0


@dice_roll_successes_bonus_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, check_base, dice):
    return 0

@dice_roll_successes_bonus_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, check_base, roll):
    return roll

@dice_roll_successes_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base, successes):
    return successes

@total_dice_roll_successes_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, check_base, successes):
    return successes

@item_after_use_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, check_base):
    return arkham.GameplayAction ("")

@check_correction_actions_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, check_base, roll):
    return []

@spend_clue_token_actions_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, check_base):
    return []


# Resistances and immunities -- combat check only

@bonus_mod_hook.match (fun.any, fun.any,
                       lambda subject: len (subject.resistances ()) > 0,
                       fun.any,
                       fun.val == checkbase_combat,
                       fun.not_ (Bonus.match_family (family_indifferent)))
def do (game, investigator, subject, item, check_base, bonus):
    fam = bonus.family ()
    ress = subject.resistances ()
    if fam in ress:
        return ress[fam].modify (bonus)
    else:
        return bonus
