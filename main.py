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

    def select_action (self, game, investigator, actions):
        renames = {}
        known_names = {}

        renames = {}
        known_names = {}

        def dump_head (obj, level = 0):
            prefix = "  " * level
            name = obj.name ()
            first = True

            if name in known_names:
                if obj in renames:
                    name = renames[obj]
                    first = False
                else:
                    known_names[name] += 1
                    nth = known_names[name]
                    def fmtnumber (n):
                        # hopefully we won't need more!
                        return {2:"II",  3:"III", 4:"IV",
                                5:"V",   6:"VI",  7:"VII",
                                8:"VIII",9:"IX", 10:"X"}[n]
                    name = "%s %s" % (name, fmtnumber (nth))
                    renames[obj] = name
            else:
                renames[obj] = name
                known_names[name] = 1

            print "%s+ %s%s" % (prefix, name,
                                ((" (%s)" % obj.attributes ().fmt_flags ())
                                 if first else ""))

            return first

        def dump_monster_info (monster, level):
            if dump_head (monster, level):
                prefix = "  " * level
                print "%s  evade:  %s" \
                    % (prefix,
                       monster.proto ().evade_check ().description (game, investigator))
                print "%s  horror: %s/%s" \
                    % (prefix,
                       monster.proto ().horror_check ().description (game, investigator),
                       monster.proto ().horror_damage ().description (game, investigator, monster))
                print "%s  combat: %s/%s" \
                    % (prefix,
                       monster.proto ().combat_check ().description (game, investigator),
                       monster.proto ().combat_damage ().description (game, investigator, monster))
                print "%s  location: %s" % (prefix, monster.location ().name ())

        def dump_location_info (location, level):
            if dump_head (location, level):
                prefix = "  " * level
                for monster in game.monsters_at (location):
                    dump_monster_info (monster, level + 1)

        actions = actions + [arkham.GameplayAction_Quit ()]

        print "======================================================="
        print "%s: sanity=%s, stamina=%s, movement=%s"\
            % (investigator.name (),
               investigator.sanity (),
               investigator.stamina (),
               investigator.movement_points ())
        dump_location_info (investigator.location (), 1)
        print "trophies:", ", ".join (trophy.name ()
                                      for trophy in investigator.trophies ())
        while True:
            print "-------------------------------------------------------"
            id_act = list (enumerate (actions))

            already_shown = set ()
            for i, action in id_act:
                print "%2s: %s" % (i, action.name ())

                location = action.bound_location ()
                if location:
                    if location not in already_shown:
                        dump_location_info (location, 3)
                    else:
                        dump_head (location, 3)

                monster = action.bound_monster ()
                if monster:
                    if monster not in already_shown:
                        dump_monster_info (monster, 3)
                    else:
                        dump_head (monster, 3)
                    already_shown.add (monster)

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
idx.add_module (mod_ah.ModuleProto ())

import mod_ancient
idx.add_module (mod_ancient.ModuleProto ())

import mod_monster
idx.add_module (mod_monster.ModuleProto ())

import mod_common
idx.add_module (mod_common.ModuleProto ())

import mod_skills
idx.add_module (mod_skills.ModuleProto ())

import mod_terror
idx.add_module (mod_terror.ModuleProto ())

# let's play arkham horror!
idx.request ("ah")

game = arkham.Game (idx.requested_modules (), TUI ())
game.setup_game ()
