import fun
from investigator import Investigator
from game import Game
from item import Item
import conf

check_trace = conf.trace # whether we want to trace hooks

SkillName = str
Difficulty = int
Modifier = int
Die = int
Roll = int
Subject = object # e.g. a monster, or a card that cause the check to be made
Successes = int

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

@perform_check_hook.match (fun.any, fun.any, fun.any, fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name, modifier, difficulty):
    import random

    die = base_die_mod_hook (game, investigator, subject, skill_name,
                             investigator.skill (skill_name))
    modifier = base_modifier_mod_hook (game, investigator, subject, skill_name, modifier)
    difficulty = difficulty_mod_hook (game, investigator, subject, skill_name, difficulty)

    bonus = 0
    for item in investigator.wields_items (): # includes skill cards, spells, weapons, etc.
        i_bonus = bonus_hook (game, investigator, subject, item, skill_name)
        bonus += bonus_mod_hook (game, investigator, subject, item, skill_name, i_bonus)

    modifier += total_bonus_mod_hook (game, investigator, subject, skill_name, bonus)
    modifier = total_modifier_mod_hook (game, investigator, subject, skill_name, modifier)
    die = total_die_mod_hook (game, investigator, subject, skill_name, die + modifier)

    successes = 0
    for i in xrange (die):
        # Six-sided dice is so entrenched in the system, that we
        # can hopefully assume that no expansion will replace
        # that.
        roll = random.randint (1, 6) # xxx or something
        r_successes = dice_roll_successes_hook (game, investigator, subject, skill_name, roll)

        for item in investigator.wields_items ():
            b_successes = dice_roll_successes_bonus_hook (game, investigator, subject, item, skill_name, roll)
            r_successes += dice_roll_successes_bonus_mod_hook (game, investigator, subject, item, skill_name, b_successes)

        successes += dice_roll_successes_mod_hook (game, investigator, subject, skill_name, r_successes)

    successes = total_dice_roll_successes_mod_hook (game, investigator, subject, skill_name, successes)

    if successes < difficulty:
        # XXX spend clue tokens to gain advantage
        pass

    ret = successes >= difficulty
    print "check %s, %s/%s successes on %s die"\
        % ("passed" if ret else "failed",
           successes, difficulty, die)

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
