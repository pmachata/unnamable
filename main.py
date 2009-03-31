#!/usr/bin/env python
# -*- coding: utf-8 -*-

import arkham

class TUI (arkham.UI):
    def setup_players (self, game):
        for investigator in game.all_investigators ():
            game.use_investigator (investigator)
            break

    def setup_investigator (self, game, investigator):
        # decide initial values
        print "XXX setup investigator %s" % investigator.name ()

    def wants_to_fight (self, game, investigator, monster):
        return raw_input ("%s: Do you want to fight %s? [Y/n] "
                          % (investigator.name (), monster.name ()))\
            in ["Y", "y", ""]

    def select_action (self, game, investigator, actions):
        def dump_monster_info (monster, level):
            prefix = "  " * level
            print "%s+ %s (%s)" % (prefix, monster.name (),
                                   monster.attributes.fmt_flags ())
            print "%s  evade:  %s" \
                % (prefix,
                   monster.evade_check ().description (game, investigator))
            print "%s  horror: %s/%s" \
                % (prefix,
                   monster.horror_check ().description (game, investigator),
                   monster.horror_damage ().description (game, investigator, monster))
            print "%s  combat: %s/%s" \
                % (prefix,
                   monster.combat_check ().description (game, investigator),
                   monster.combat_damage ().description (game, investigator, monster))

        def dump_location_info (location, level):
            prefix = "  " * level
            print "%s%s (%s)" % (prefix, location.name (),
                                 location.attributes.fmt_flags ())
            for monster in game.monsters_at (location):
                dump_monster_info (monster, level + 1)

        actions = actions + [arkham.GameplayAction_Quit ()]

        print "======================================================="
        print "%s: sanity=%s, stamina=%s, movement=%s"\
            % (investigator.name (),
               investigator.sanity (),
               investigator.stamina (),
               investigator.movement_points ())
        dump_location_info (investigator.location (), 2)
        print "trophies:", ", ".join (trophy.name ()
                                      for trophy in investigator.trophies ())
        while True:
            print "-------------------------------------------------------"
            id_act = list (enumerate (actions))
            for i, action in id_act:
                print "%2s: %s" % (i, action.name ())
                loc = action.bound_location ()
                if loc:
                    dump_location_info (loc, 3)

            id_act = dict (id_act)
            try:
                sel = int (raw_input ())
            except ValueError:
                continue

            if sel in id_act:
                print "=>", id_act[sel].name ()
                print "-------------------------------------------------------"
                return id_act[sel]

idx = arkham.ModuleIndex ()

# some sort of module discovery would be here instead
import mod_ah
idx.add_module (mod_ah.Module ())

import mod_ancient
idx.add_module (mod_ancient.Module ())

import mod_monster
idx.add_module (mod_monster.Module ())

import mod_skills
idx.add_module (mod_skills.Module ())

import mod_terror
idx.add_module (mod_terror.Module ())

# let's play arkham horror!
idx.request ("ah")

game = arkham.Game (idx.requested_modules (), TUI ())
game.setup_game ()
