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
        actions = actions + [arkham.GameplayAction_Quit ()]

        print "======================================================="
        print "%s @ %s: sanity=%s, stamina=%s, movement=%s"\
            % (investigator.name (),
               investigator.location ().name (),
               investigator.sanity (),
               investigator.stamina (),
               investigator.movement_points ())
        print "trophies:", ", ".join (trophy.name ()
                                      for trophy in investigator.trophies ())
        while True:
            print "-------------------------------------------------------"
            id_act = list (enumerate (actions))
            for i, action in id_act:
                loc = action.bound_location ()
                extra = ""
                if loc:
                    extra = " (%s)" % loc.attributes.fmt_flags ()
                    mon = game.monsters_at (loc)
                    if mon:
                        extra = extra + " [%s]" % (", ".join (monster.name () for monster in mon))
                print "%2s: %s%s" % (i, action.name (), extra)

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
