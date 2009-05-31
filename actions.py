import arkham
import obj

class GameplayAction (obj.NamedObject):
    def perform (self, game, investigator):
        pass

    def bound_location (self):
        return None

    def bound_monster (self):
        return None

    def bound_item (self):
        return None

class LocationBoundGameplayAction (GameplayAction):
    def __init__ (self, location, name):
        GameplayAction.__init__ (self, name)
        self.m_location = location

    def bound_location (self):
        return self.m_location

class MonsterBoundGameplayAction (GameplayAction):
    def __init__ (self, monster, name):
        GameplayAction.__init__ (self, name)
        self.m_monster = monster

    def bound_monster (self):
        return self.m_monster

class ItemBoundGameplayAction (GameplayAction):
    def __init__ (self, item, name):
        GameplayAction.__init__ (self, name)
        self.m_item = item

    def bound_item (self):
        return self.m_item

# Generic actions.

class GameplayAction_Many (GameplayAction):
    """Base class for actions involving several sub-actions."""
    def __init__ (self, actions, name_ctor):
        actions = list (action for action in actions if action != None)
        GameplayAction.__init__ (self, name_ctor (actions))
        self.m_actions = actions

    def bound_location (self):
        ret = None
        for action in self.m_actions:
            ret = action.bound_location () or ret
        return ret

    def bound_monster (self):
        ret = None
        for action in self.m_actions:
            ret = action.bound_monster () or ret
        return ret

    def bound_item (self):
        ret = None
        for action in self.m_actions:
            ret = action.bound_item () or ret
        return ret

class GameplayAction_One (GameplayAction):
    def __init__ (self, action, name):
        assert action
        GameplayAction.__init__ (self, name)
        self.m_action = action

    def bound_location (self):
        return self.m_action.bound_location ()

    def bound_monster (self):
        return self.m_action.bound_monster ()

    def bound_item (self):
        return self.m_action.bound_item ()

class GameplayAction_Multiple (GameplayAction_Many):
    def __init__ (self, actions):
        GameplayAction_Many.__init__ \
            (self, actions,
             lambda actions: ", ".join (action.name () for action in actions))

    def perform (self, game, investigator):
        ret = None
        for action in self.m_actions:
            ret = action.perform (game, investigator) or ret
        return ret

class GameplayAction_Select (GameplayAction_Many):
    def __init__ (self, actions):
        GameplayAction_Many.__init__ \
            (self, actions,
             lambda actions: " or ".join (action.name () for action in actions))

    def perform (self, game, investigator):
        game.perform_selected_action (investigator, self.m_actions)

class GameplayAction_Repeat (GameplayAction_One):
    def __init__ (self, count, action):
        assert count > 1
        quantifier = "twice" if count == 2 else ("%d times" % count)
        GameplayAction_One.__init__ \
            (self, action, "%s do %s" % (quantifier, action.name ()))
        self.m_count = count

    def perform (self, game, investigator):
        for _ in xrange (self.m_count):
            self.m_action.perform (game, investigator)

class GameplayAction_Conditional (GameplayAction_Many):
    def __init__ (self, game, investigator, subject,
                  check, action_pass, action_fail = None):
        assert action_pass is not None
        GameplayAction_Many.__init__ \
                 (self, [action_pass, action_fail],
                  lambda actions: \
                      ("if %s passes then %s%s"
                       % (check.description (game, investigator),
                          actions[0].name (),
                          (", else %s" % actions[1].name () \
                               if len (actions) > 1 else ""))))

        self.m_check = check
        self.m_subject = subject

    def perform (self, game, investigator):
        if self.m_check.check (game, investigator, self.m_subject):
            return self.m_actions[0].perform (game, investigator)
        elif len (self.m_actions) > 1:
            return self.m_actions[1].perform (game, investigator)
        else:
            return None

class GameplayAction_WithNumberOfSuccesses (GameplayAction):
    # SkillCheck needs to be passed here, or something else that can
    # yield success as well as number of successes after the call to
    # `extended_check' method.
    def __init__ (self, game, investigator, subject,
                  skill_check, action_ctor_pass, action_ctor_fail = None):
        assert action_ctor_pass is not None
        n = "number of successes"
        GameplayAction.__init__ \
                 (self,
                  "if %s passes then %s%s" \
                      % (skill_check.description (game, investigator),
                         action_ctor_pass (n).name (),
                          (", else %s" % action_ctor_fail (n).name () \
                               if action_ctor_fail != None else "")))

        self.m_check = skill_check
        self.m_subject = subject
        self.m_pass = action_ctor_pass
        self.m_fail = action_ctor_fail

    def perform (self, game, investigator):
        success, successes \
            = self.m_check.extended_check (game, investigator, self.m_subject)
        if success:
            return self.m_pass (successes).perform (game, investigator)
        elif self.m_fail != None:
            return self.m_fail (successes).perform (game, investigator)
        else:
            return None

class GameplayAction_WithSelectedItem (GameplayAction):
    def __init__ (self, selector, description, action_ctor):
        class FakeItem (arkham.ItemProto):
            def __init__ (self):
                arkham.ItemProto.__init__ (self, "selected %s" % description)
        GameplayAction.__init__ \
            (self, action_ctor (arkham.Item (FakeItem ())).name ())
        self.m_selector = selector
        self.m_action_ctor = action_ctor

    def perform (self, game, investigator):
        actions = [self.m_action_ctor (item)
                   for item in investigator.wields_items ()
                   if self.m_selector (item)]
        assert len (actions) > 0
        game.perform_selected_action (investigator, actions)

class GameplayAction_WithSelectedInvestigator (GameplayAction):
    def __init__ (self, selector, description, action_ctor):
        class FakeInvestigator (arkham.ItemProto):
            def __init__ (self):
                arkham.ItemProto.__init__ (self, None)
        GameplayAction.__init__ \
            (self, "select %s and %s" \
                 % (description,
                    action_ctor (FakeInvestigator ()).name ()))
        self.m_selector = selector
        self.m_action_ctor = action_ctor

    def perform (self, game, investigator):
        actions = [self.m_action_ctor (investigator)
                   for investigator in game.investigators ()
                   if self.m_selector (investigator)]
        assert len (actions) > 0
        game.perform_selected_action (investigator, actions)

class GameplayAction_WithSelected (GameplayAction):
    def __init__ (self, candidate_ctor, description, action_ctor, fake):
        GameplayAction.__init__ \
            (self, "select %s and %s" \
                 % (description,
                    action_ctor (fake).name ()))
        self.m_candidate_ctor = candidate_ctor
        self.m_action_ctor = action_ctor

    def perform (self, game, investigator):
        actions = [self.m_action_ctor (candidate)
                   for candidate in self.m_candidate_ctor ()]
        assert len (actions) > 0
        game.perform_selected_action (investigator, actions)

# Movement actions

class GameplayAction_Move (LocationBoundGameplayAction):
    def __init__ (self, location):
        LocationBoundGameplayAction.__init__ (self, location, "move")

    def perform (self, game, investigator):
        game.move_investigator (investigator, self.m_location)
        if investigator.movement_points () > 0:
            # He might have lost all movement points during the fight
            # after he tried to leave the current location.
            investigator.spend_movement_points (1)

class GameplayAction_Stay (LocationBoundGameplayAction):
    def __init__ (self, location):
        LocationBoundGameplayAction.__init__ (self, location, "stay put")

    def perform (self, game, investigator):
        investigator.lose_movement_points ()
        raise arkham.EndPhase ()

class GameplayAction_DoNothing (GameplayAction):
    def __init__ (self):
        GameplayAction.__init__ (self, "do nothing")

    def perform (self, game, investigator):
        raise arkham.EndPhase ()

# Investigator actions

class GameplayAction_GainClues (GameplayAction):
    def __init__ (self, amount):
        assert amount > 0
        GameplayAction.__init__ (self,
                                 "gain %d clue%s" \
                                     % (amount, "s" if amount > 1 else ""))
        self.m_amount = amount

    def perform (self, game, investigator):
        investigator.gain_clues (self.m_amount)

class GameplayAction_GainMovementPoints (GameplayAction):
    def __init__ (self, amount):
        assert amount > 0
        GameplayAction.__init__ (self,
                                 "gain %d movement point%s" \
                                     % (amount, "s" if amount > 1 else ""))
        self.m_amount = amount

    def perform (self, game, investigator):
        investigator.gain_movement_points (self.m_amount)

class GameplayAction_SpendMovementPoints (GameplayAction):
    def __init__ (self, amount):
        assert amount > 0
        GameplayAction.__init__ (self,
                                 "spend %d movement point%s" \
                                     % (amount, "s" if amount > 1 else ""))
        self.m_amount = amount

    def perform (self, game, investigator):
        investigator.spend_movement_points (self.m_amount)

class GameplayAction_CauseHarm (GameplayAction):
    def __init__ (self, game, investigator, subject, harm):
        GameplayAction.__init__ \
            (self, harm.description (game, investigator, subject))
        self.m_subject = subject
        self.m_harm = harm

    def perform (self, game, investigator):
        self.m_harm.cause (game, investigator, self.m_subject)

class GameplayAction_Heal (GameplayAction):
    def __init__ (self, heal):
        GameplayAction.__init__ (self, heal.description ())
        self.m_heal = heal

    def perform (self, game, investigator):
        self.m_heal.heal (investigator)


# Checks

class GameplayAction_NormalCheckHook (GameplayAction):
    def __init__ (self, game, investigator, subject,
                  checkbase, modifier, difficulty):
        GameplayAction.__init__ (self, "perform %s check" % checkbase.name ())
        self.m_subject = subject
        self.m_checkbase = checkbase
        self.m_modifier = modifier
        self.m_difficulty = difficulty

    def perform (self, game, investigator):
        successes = game.normal_perform_check_hook \
            (game, investigator, self.m_subject,
             self.m_checkbase, self.m_modifier,
             self.m_difficulty)
        raise arkham.EndCheck (successes >= self.m_difficulty, successes)

class GameplayAction_PassCheck (GameplayAction):
    def __init__ (self):
        GameplayAction.__init__ (self, "pass check")

    def perform (self, game, investigator):
        raise arkham.EndCheck (True, 1)

# Combat actions

class GameplayAction_Evade (MonsterBoundGameplayAction):
    def __init__ (self, combat, monster):
        MonsterBoundGameplayAction.__init__ (self, monster, "evade")
        self.m_combat = combat

class GameplayAction_Evade_PreCombat (GameplayAction_Evade):
    def perform (self, game, investigator):
        game.evade_check_hook (self.m_combat, investigator, self.m_monster)
        investigator.lose_movement_points ()
        raise arkham.ContinueCombat () # Proceed with the combat.

class GameplayAction_Evade_Combat (GameplayAction_Evade):
    def perform (self, game, investigator):
        game.evade_check_hook (self.m_combat, investigator, self.m_monster)

class GameplayAction_Fight (MonsterBoundGameplayAction):
    def __init__ (self, monster):
        MonsterBoundGameplayAction.__init__ (self, monster, "fight")

    def perform (self, game, investigator):
        raise arkham.ContinueCombat ()

class GameplayAction_DealWithMonster (MonsterBoundGameplayAction):
    def __init__ (self, monster):
        MonsterBoundGameplayAction.__init__ (self, monster, "deal with")

    def perform (self, game, investigator):
        print "dealing with %s" % self.m_monster.name ()
        game.fight (investigator, self.m_monster)
        print "combat finished"

class GameplayAction_EndCauseHarmLoop (GameplayAction_One):
    def __init__ (self, action):
        GameplayAction_One.__init__ (self, action, action.name ())

    def perform (self, game, investigator):
        self.m_action.perform (game, investigator)
        raise arkham.EndCauseHarm ()

class GameplayAction_WhenCombatEnds (GameplayAction_One):
    def __init__ (self, combat, action):
        GameplayAction_One.__init__ \
            (self, action, "when combat ends, %s" % action.name ())
        self.m_combat = combat

    def perform (self, game, investigator):
        self.m_combat.on_end \
            (lambda: self.m_action.perform (game, investigator))

class GameplayAction_ForCombat (GameplayAction_One):
    def __init__ (self, combat, action, cleanup):
        GameplayAction_One.__init__ \
            (self, action, "%s until the end of the combat" % action.name ())
        self.m_combat = combat
        self.m_cleanup = cleanup

    def perform (self, game, investigator):
        self.m_action.perform (game, investigator)
        self.m_combat.on_end \
            (lambda: self.m_cleanup.perform (game, investigator))

class GameplayAction_ForTurn (GameplayAction_One):
    def __init__ (self, action, cleanup):
        GameplayAction_One.__init__ \
            (self, action, "%s until the end of the turn" % action.name ())
        self.m_cleanup = cleanup

    def perform (self, game, investigator):
        self.m_action.perform (game, investigator)
        game.register_per_turn \
            (lambda game: self.m_cleanup.perform (game, investigator), 1)


# Item manipulation actions

class GameplayAction_WieldItem (ItemBoundGameplayAction):
    def __init__ (self, item, temporary = False):
        ItemBoundGameplayAction.__init__ (self, item, "wield")
        self.m_temporary = temporary

    def perform (self, game, investigator):
        if self.m_temporary:
            investigator.take_temporary_item (investigator, self.m_item)
        investigator.wield_item (game, self.m_item)

class GameplayAction_ReleseItem (ItemBoundGameplayAction):
    def __init__ (self, item):
        ItemBoundGameplayAction.__init__ (self, item, "release")

    def perform (self, game, investigator):
        investigator.release_item (self.m_item)

class GameplayAction_Exhaust (ItemBoundGameplayAction):
    def __init__ (self, item):
        ItemBoundGameplayAction.__init__ (self, item, "exhaust")

    def perform (self, game, investigator):
        self.m_item.exhaust ()

class GameplayAction_Discard (ItemBoundGameplayAction):
    def __init__ (self, item):
        ItemBoundGameplayAction.__init__ (self, item, "discard")

    def perform (self, game, investigator):
        if investigator.wields_item (self.m_item):
            investigator.release_item (self.m_item)
        investigator.discard_item (self.m_item)

class GameplayAction_SpendClue (GameplayAction):
    def __init__ (self):
        GameplayAction.__init__ (self, "spend clue token")

    def perform (self, game, investigator):
        investigator.spend_clue ()

class GameplayAction_DrawItem (GameplayAction):
    def __init__ (self, deck):
        assert deck != None
        GameplayAction.__init__ (self, "draw from %s" % deck.name ())
        self.m_deck = deck

    def perform (self, game, investigator):
        investigator.take_item (game, self.m_deck.draw ())

class GameplayAction_MarkItem (GameplayAction):
    def _tokens (self, item):
        return item.__dict__.get ("tokens", 0)

    def __init__ (self, item, max, when_exhausted):
        assert when_exhausted
        assert max > 0
        assert item

        i = self._tokens (item) + 1
        if i == max:
            description = when_exhausted.name ()
        else:
            description = "put %d%s token on the card (when there are %d, %s)" \
                % (i,
                   {1:"st", 2:"nd", 3:"rd", 11:"th", 12:"th", 13:"th"} \
                       .get (i % 10, "th"),
                   max, when_exhausted.name ())

        GameplayAction.__init__ (self, description)
        self.m_when_exhausted = when_exhausted
        self.m_max = max
        self.m_item = item

    def perform (self, game, investigator):
        self.m_item.tokens = self._tokens (self.m_item) + 1
        if self.m_item.tokens == self.m_max:
            self.m_when_exhausted.perform (game, investigator)

class GameplayAction_Flag (ItemBoundGameplayAction):
    def __init__ (self, item, attribute):
        ItemBoundGameplayAction.__init__ \
            (self, item, "make %s %s" % (item.name (), attribute))
        assert not item.attributes ().has (attribute)
        self.m_item = item
        self.m_attribute = attribute

    def perform (self, game, investigator):
        assert not self.m_item.attributes ().has (self.m_attribute)
        self.m_item.attributes ().set (self.m_attribute, True)

class GameplayAction_Unflag (ItemBoundGameplayAction):
    def __init__ (self, item, attribute):
        ItemBoundGameplayAction.__init__ \
            (self, item, "end %s %s" % (item.name (), attribute))
        assert not item.attributes ().has (attribute)
        self.m_item = item
        self.m_attribute = attribute

    def perform (self, game, investigator):
        assert self.m_item.attributes ().flag (self.m_attribute)
        self.m_item.attributes ().set (self.m_attribute, None)

# Roll correction actions

class GameplayAction_AddRoll (GameplayAction):
    def __init__ (self, subject, skill_name, roll):
        GameplayAction.__init__ (self, "roll additional die")
        self.m_subject = subject
        self.m_skill_name = skill_name
        self.m_roll = roll

    def perform (self, game, investigator):
        self.m_roll.add_roll (game, investigator,
                              self.m_subject, self.m_skill_name)

class GameplayAction_Reroll (GameplayAction):
    def __init__ (self, subject, skill_name, roll):
        GameplayAction.__init__ (self, "reroll")
        self.m_subject = subject
        self.m_skill_name = skill_name
        self.m_roll = roll

    def perform (self, game, investigator):
        self.m_roll.reroll (game, investigator,
                            self.m_subject, self.m_skill_name)

class GameplayAction_FailRoll (GameplayAction):
    def __init__ (self):
        GameplayAction.__init__ (self, "fail check")

    def perform (self, game, investigator):
        raise arkham.EndPhase ()

# Damage correction actions

class GameplayAction_ReduceDamage (GameplayAction):
    def __init__ (self, damage, aspect, amount):
        GameplayAction.__init__ \
            (self, "reduce %s damage by %d" % (aspect.name (), amount))
        self.m_damage = damage
        self.m_aspect = aspect
        self.m_amount = amount

    def perform (self, game, investigator):
        self.m_damage.amount (self.m_aspect).reduce (self.m_amount)

class GameplayAction_CancelDamage (GameplayAction):
    def __init__ (self, damage, aspect):
        GameplayAction.__init__ \
            (self, "cancel %s damage" % aspect.name ())
        self.m_damage = damage
        self.m_aspect = aspect

    def perform (self, game, investigator):
        self.m_damage.amount (self.m_aspect).cancel ()

class GameplayAction_IncurDamage (GameplayAction):
    def __init__ (self):
        GameplayAction.__init__ (self, "incur damage")

    def perform (self, game, investigator):
        raise arkham.EndPhase ()

# Monster actions

class GameplayAction_ReduceMonsterToughness (MonsterBoundGameplayAction):
    def __init__ (self, monster, by, minimum):
        MonsterBoundGameplayAction.__init__ \
            (self, monster,
             "reduce toughness by %d to a minimum of %d" \
                 % (by, minimum))
        self.m_by = by
        self.m_minimum = minimum

    def perform (self, game, investigator):
        check = self.m_monster.combat_check ()
        diff = check.difficulty ()
        if diff > self.m_minimum:
            diff2 = max (self.m_minimum, diff - self.m_by)
            check.set_difficulty (diff2)
            print "reduced difficulty from %d to %d" % (diff, diff2)

class GameplayAction_SetMonsterToughness (MonsterBoundGameplayAction):
    def __init__ (self, monster, value):
        MonsterBoundGameplayAction.__init__ \
            (self, monster, "set toughness to %d" % value)
        self.m_value = value

    def perform (self, game, investigator):
        self.m_monster.combat_check ().set_difficulty (self.m_value)

class GameplayAction_DropSpecialAbility (MonsterBoundGameplayAction):
    def __init__ (self, monster, ability):
        MonsterBoundGameplayAction.__init__ \
            (self, monster, "drop %s ability" % ability.name ())
        self.m_ability = ability

    def perform (self, game, investigator):
        self.m_monster.remove_special_ability (self.m_ability)

class GameplayAction_CancelSpecialAbilityCustomization \
        (MonsterBoundGameplayAction):
    def __init__ (self, monster, ability):
        MonsterBoundGameplayAction.__init__ \
            (self, monster,
             "undo changes on monster's %s ability" % ability.name ())
        self.m_ability = ability

    def perform (self, game, investigator):
        self.m_monster.cancel_special_ability_customization (self.m_ability)

# Various

class GameplayAction_Quit (GameplayAction):
    def __init__ (self):
        GameplayAction.__init__ (self, "quit the game")

    def perform (self, game, investigator):
        game.drop_investigator (investigator)
