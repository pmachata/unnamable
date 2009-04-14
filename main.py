#!/usr/bin/env python
# -*- coding: utf-8 -*-

import arkham
import modules

class TUI (arkham.UI):
    def setup_players (self, game):
        for investigator in game.all_investigators ():
            game.use_investigator (investigator)
            break

    def select_action (self, game, investigator, actions):
        if len (actions) == 1:
            action = actions[0]
            print "(choosing the only available action, %s)" % action.name ()
            return action

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

        def dump_item_info (item, level):
            dump_head (item, level)

        actions = actions + [arkham.GameplayAction_Quit ()]

        print "======================================================="
        print "%s: sanity=%s, stamina=%s, movement=%s, clues=%s"\
            % (investigator.name (),
               investigator.sanity (),
               investigator.stamina (),
               investigator.movement_points (),
               investigator.clues ())
        dump_location_info (investigator.location (), 1)
        print "trophies:", ", ".join (trophy.name ()
                                      for trophy in investigator.trophies ())
        if investigator.wields_items ():
            print "wields items:"
            for item in investigator.wields_items ():
                dump_item_info (item, 1)

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

                item = action.bound_item ()
                if item:
                    if item not in already_shown:
                        dump_item_info (item, 3)
                    else:
                        dump_head (item, 3)
                    already_shown.add (item)

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
modules.discover_modules (idx)
idx.request ("ah")

game = arkham.Game (idx.requested_modules (), TUI ())
game.run ()
