import fun
from investigator import Investigator
from game import Game, Item
import conf
import arkham

check_trace = conf.trace # whether we want to trace hooks

SkillName = str
Difficulty = int
Modifier = int
Die = int
Roll = int
Subject = object # e.g. a monster, or a card that cause the check to be made
Successes = int

die_count_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Modifier,
     name="die_count_hook", trace=check_trace)
normal_die_count_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Modifier,
     name="normal_die_count_hook", trace=check_trace)

perform_check_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Modifier, Difficulty,
     name="perform_check_hook", trace=check_trace)
normal_perform_check_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Modifier, Difficulty,
     name="normal_perform_check_hook", trace=check_trace)

base_die_mod_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Modifier,
     name="base_die_mod_hook", trace=check_trace)
normal_base_die_mod_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Modifier,
     name="normal_base_die_mod_hook", trace=check_trace)

base_modifier_mod_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Modifier,
     name="base_modifier_mod_hook", trace=check_trace)
normal_base_modifier_mod_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Modifier,
     name="normal_base_modifier_mod_hook", trace=check_trace)

difficulty_mod_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Difficulty,
     name="difficulty_mod_hook", trace=check_trace)
normal_difficulty_mod_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Difficulty,
     name="normal_difficulty_mod_hook", trace=check_trace)

bonus_hook = fun.Function \
    (Game, Investigator, Subject, Item, SkillName,
     name="bonus_hook", trace=check_trace)
normal_bonus_hook = fun.Function \
    (Game, Investigator, Subject, Item, SkillName,
     name="normal_bonus_hook", trace=check_trace)

bonus_mod_hook = fun.Function \
    (Game, Investigator, Subject, Item, SkillName, Modifier,
     name="bonus_mod_hook", trace=check_trace)
normal_bonus_mod_hook = fun.Function \
    (Game, Investigator, Subject, Item, SkillName, Modifier,
     name="normal_bonus_mod_hook", trace=check_trace)

total_bonus_mod_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Modifier,
     name="total_bonus_mod_hook", trace=check_trace)
normal_total_bonus_mod_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Modifier,
     name="normal_total_bonus_mod_hook", trace=check_trace)

total_modifier_mod_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Modifier,
     name="total_modifier_mod_hook", trace=check_trace)
normal_total_modifier_mod_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Modifier,
     name="normal_total_modifier_mod_hook", trace=check_trace)

total_die_mod_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Die,
     name="total_die_mod_hook", trace=check_trace)
normal_total_die_mod_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Die,
     name="normal_total_die_mod_hook", trace=check_trace)

one_dice_roll_hook = fun.Function \
    (Game, Investigator, Subject, SkillName,
     name="one_dice_roll_hook", trace=check_trace)
normal_one_dice_roll_hook = fun.Function \
    (Game, Investigator, Subject, SkillName,
     name="normal_one_dice_roll_hook", trace=check_trace)

dice_roll_successes_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Roll,
     name="dice_roll_successes_hook", trace=check_trace)
normal_dice_roll_successes_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Roll,
     name="normal_dice_roll_successes_hook", trace=check_trace)

dice_roll_successes_bonus_hook = fun.Function \
    (Game, Investigator, Subject, Item, SkillName, Roll,
     name="dice_roll_successes_bonus_hook", trace=check_trace)
normal_dice_roll_successes_bonus_hook = fun.Function \
    (Game, Investigator, Subject, Item, SkillName, Roll,
     name="normal_dice_roll_successes_bonus_hook", trace=check_trace)

dice_roll_successes_bonus_mod_hook = fun.Function \
    (Game, Investigator, Subject, Item, SkillName, Successes,
     name="dice_roll_successes_bonus_mod_hook", trace=check_trace)
normal_dice_roll_successes_bonus_mod_hook = fun.Function \
    (Game, Investigator, Subject, Item, SkillName, Successes,
     name="normal_dice_roll_successes_bonus_mod_hook", trace=check_trace)

dice_roll_successes_mod_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Successes,
     name="dice_roll_successes_mod_hook", trace=check_trace)
normal_dice_roll_successes_mod_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Successes,
     name="normal_dice_roll_successes_mod_hook", trace=check_trace)

total_dice_roll_successes_mod_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Successes,
     name="total_dice_roll_successes_mod_hook", trace=check_trace)
normal_total_dice_roll_successes_mod_hook = fun.Function \
    (Game, Investigator, Subject, SkillName, Successes,
     name="normal_total_dice_roll_successes_mod_hook", trace=check_trace)

class Roll:
    def __init__ (self, modifier):
        self.m_roll = []
        self.m_modifier = modifier

    def reroll (self, game, investigator, subject, skill_name):
        self.m_roll = []
        for _ in xrange (die_count_hook (game, investigator, subject,
                                         skill_name, self.m_modifier)):
            self.add_roll (game, investigator, subject, skill_name)

    def add_roll (self, game, investigator, subject, skill_name):
        self.m_roll.append (one_dice_roll_hook (game, investigator,
                                                subject, skill_name))

    def roll (self):
        return list (self.m_roll)

    def update_roll (self, roll):
        self.m_roll = list (roll)

check_correction_actions_hook = fun.Function \
    (Game, Investigator, Subject, Item, SkillName, Roll,
     name="check_correction_actions_hook", trace=check_trace)
normal_check_correction_actions_hook = fun.Function \
    (Game, Investigator, Subject, Item, SkillName, Roll,
     name="normal_check_correction_actions_hook", trace=check_trace)

@die_count_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, modifier):
    return normal_die_count_hook (game, investigator, subject, skill_name, modifier)

@normal_die_count_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, modifier):
    die = base_die_mod_hook (game, investigator, subject, skill_name,
                             investigator.skill (skill_name))
    modifier = base_modifier_mod_hook (game, investigator, subject, skill_name, modifier)

    bonus = 0
    for item in investigator.wields_items (): # includes skill cards, spells, weapons, etc.
        i_bonus = bonus_hook (game, investigator, subject, item, skill_name)
        bonus += bonus_mod_hook (game, investigator, subject, item, skill_name, i_bonus)

    modifier += total_bonus_mod_hook (game, investigator, subject, skill_name, bonus)
    modifier = total_modifier_mod_hook (game, investigator, subject, skill_name, modifier)
    die = total_die_mod_hook (game, investigator, subject, skill_name, die + modifier)

    return die


@perform_check_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, modifier, difficulty):

    roll = Roll (modifier)
    roll.reroll (game, investigator, subject, skill_name)

    difficulty = difficulty_mod_hook (game, investigator, subject, skill_name, difficulty)

    try:
        while True:
            successes = 0
            for dice in roll.roll ():
                r_successes = dice_roll_successes_hook (game, investigator, subject, skill_name, dice)

                for item in investigator.wields_items ():
                    b_successes = dice_roll_successes_bonus_hook (game, investigator, subject, item, skill_name, dice)
                    r_successes += dice_roll_successes_bonus_mod_hook (game, investigator, subject, item, skill_name, b_successes)

                successes += dice_roll_successes_mod_hook (game, investigator, subject, skill_name, r_successes)

            successes = total_dice_roll_successes_mod_hook (game, investigator, subject, skill_name, successes)

            ret = successes >= difficulty

            # xxx This needs to be passed over to UI as some sort of
            # event description object.
            print "check %s, %s/%s successes on %s die"\
                % ("passed" if ret else "failed",
                   successes, difficulty, len (roll.roll ()))

            if successes >= difficulty:
                # No need to modify the roll.
                break

            actions = sum ((check_correction_actions_hook (game, investigator, subject, item, skill_name, roll)
                            for item in investigator.wields_items ()), []) \
                            + investigator.check_correction_actions (game, subject, skill_name, roll)
            actions.append (arkham.GameplayAction_FailRoll ())
            if not game.perform_selected_action (investigator, actions):
                break

    except arkham.EndPhase:
        pass

    return ret

@base_die_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, modifier):
    return normal_base_die_mod_hook (game, investigator, subject, skill_name, modifier)

@normal_base_die_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, modifier):
    return modifier


@base_modifier_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, modifier):
    return normal_base_modifier_mod_hook (game, investigator, subject, skill_name, modifier)

@normal_base_modifier_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, modifier):
    return modifier


@difficulty_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, difficulty):
    return normal_difficulty_mod_hook (game, investigator, subject, skill_name, difficulty)

@normal_difficulty_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, difficulty):
    return difficulty


@bonus_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, skill_name):
    return normal_bonus_hook (game, investigator, subject, item, skill_name)

@normal_bonus_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, skill_name):
    return 0


@bonus_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, skill_name, modifier):
    return normal_bonus_mod_hook (game, investigator, subject, item, skill_name, modifier)

@normal_bonus_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, skill_name, modifier):
    return modifier


@total_bonus_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, modifier):
    return normal_total_bonus_mod_hook (game, investigator, subject, skill_name, modifier)

@normal_total_bonus_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, modifier):
    return modifier


@total_modifier_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, modifier):
    return normal_total_modifier_mod_hook (game, investigator, subject, skill_name, modifier)

@normal_total_modifier_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, modifier):
    return modifier


@total_die_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, die):
    return normal_total_die_mod_hook (game, investigator, subject, skill_name, die)

@normal_total_die_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, die):
    return die


@one_dice_roll_hook.match (fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name):
    return normal_one_dice_roll_hook (game, investigator, subject, skill_name)

@normal_one_dice_roll_hook.match (fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name):
    # Six-sided dice is so entrenched in the system, that we
    # can hopefully assume that no expansion will replace
    # that.
    import random
    return random.randint (1, 6)


@dice_roll_successes_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, roll):
    return normal_dice_roll_successes_hook (game, investigator, subject, skill_name, roll)

@normal_dice_roll_successes_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, roll):
    if roll >= 5:
        return 1
    else:
        return 0


@dice_roll_successes_bonus_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, skill_name, roll):
    return normal_dice_roll_successes_bonus_hook (game, investigator, subject, item, skill_name, roll)

@normal_dice_roll_successes_bonus_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, skill_name, roll):
    return 0


@dice_roll_successes_bonus_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, skill_name, roll):
    return normal_dice_roll_successes_bonus_mod_hook (game, investigator, subject, item, skill_name, roll)

@normal_dice_roll_successes_bonus_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, skill_name, roll):
    return roll


@dice_roll_successes_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, successes):
    return normal_dice_roll_successes_mod_hook (game, investigator, subject, skill_name, successes)

@normal_dice_roll_successes_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, successes):
    return successes


@total_dice_roll_successes_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, successes):
    return normal_total_dice_roll_successes_mod_hook (game, investigator, subject, skill_name, successes)

@normal_total_dice_roll_successes_mod_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, successes):
    return successes


@check_correction_actions_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, skill_name, roll):
    return normal_check_correction_actions_hook (game, investigator, subject, item, skill_name, roll)

@normal_check_correction_actions_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, item, skill_name, roll):
    return []
