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

idx = arkham.ModuleIndex ()

# some sort of module discovery would be here instead
import mod_ah
idx.add_module (mod_ah.Module ())

import mod_ancient
idx.add_module (mod_ancient.Module ())

import mod_monster
idx.add_module (mod_monster.Module ())

import stats
idx.add_module (stats.Module ())

import mod_terror
idx.add_module (mod_terror.Module ())

# let's play arkham horror!
idx.request ("ah")

game = arkham.Game (idx.requested_modules (), TUI ())
game.setup_game ()
