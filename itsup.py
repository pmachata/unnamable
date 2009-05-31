import arkham
import fun

class Type:
    def __init__ (self, name, matcher):
        self._name = name
        self._matcher = matcher
    def name (self):
        return self._name
    def match (self, arg):
        return self._matcher (arg)

class Slot:
    def __init__ (self, *types, **kwargs):
        self._types = types
        self._type = None

    def __str__ (self):
        return " or ".join (t.name () for t in self._types)

    def assignable (self):
        return not self.assigned ()

    def assign (self, value):
        found = False
        for t in self._types:
            if t.match (value):
                # Make sure we have exactly one match.  If not, that's
                # an error in design of matchers.
                assert not found
                found = True
                self.do_assign (value, t)
                assert self._type in self._types
                print "assign %s: %s" % (str (self), self._value)

        return found

    def type (self):
        return self._type

class SlotSingle (Slot):
    def __init__ (self, *types, **kwargs):
        self._default = kwargs.pop ("default", None)
        Slot.__init__ (self, *types, **kwargs)
        assert len (kwargs) == 0
        self._value = None

    def value (self):
        return self._value if self._value is not None \
            else self._default

    def assigned (self):
        return self._value is not None

    def do_assign (self, value, t):
        self._value = value
        self._type = t

    def fmt (self):
        return str (self._value)

class Slot_Obtainer (SlotSingle):
    def __init__ (self):
        SlotSingle.__init__ (self, obtainer_t, int_t)

class SlotMulti (Slot):
    def __init__ (self, *types, **kwargs):
        Slot.__init__ (self, *types, **kwargs)
        assert len (kwargs) == 0
        self._value = []

    def value (self):
        return list (self._value)

    def assigned (self):
        return len (self._value) > 0

    def assignable (self):
        return True

    def do_assign (self, value, t):
        assert self._type is None or t == self._type
        self._value.append (value)
        self._type = t

    def fmt (self):
        return "[%s]" % (", ".join (str (emt) for emt in self._value))


class Clause:
    def __init__ (self, name, slots):
        self._slots = list (slots)
        self._name = name

    def inbound (self, decls):
        for decl in decls:
            found = False
            for slot in self._slots:
                if not slot.assignable ():
                    continue

                if slot.assign (decl):
                    found = True
                    break

            if not found:
                raise AssertionError \
                    ("\n".join \
                         (["Couldn't bind argument %s" % decl,
                           " Slot states (%d slots total):" \
                               % len (self._slots)]
                          + ["  %s: %s" % (str (slot), slot.value ())
                             for slot in self._slots]))

    def __str__ (self):
        def fmt_unassigned ():
            unassigned = list (slot for slot in self._slots
                               if slot.value () is None)
            if len (unassigned) == 0:
                return ""
            else:
                return ", unassigned: %s" % (", ".join (str (slot)
                                                        for slot in unassigned))
        return "%s(%s%s)" % (self._name,
                             ", ".join (slot.fmt ()
                                        for slot in self._slots
                                        if slot.value () is not None),
                             fmt_unassigned ())

    def _monster_flag_matcher (self, slot):
        def match (arg):
            return all (flag.construct () (arg)
                        for flag in slot.value ())
        return match

    def _checkbase_matcher (self, slot):
        return slot.value ().matcher () if slot.assigned () else fun.any

    def _diesides_matcher (self, slot):
        if not slot.assigned ():
            return fun.any
        else:
            return fun.or_ (*(fun.val == roll.construct ()
                              for roll in slot.value ()))

    def _obtainer_construct (self, slot, **kwargs):
        if slot.type () == int_t:
            return slot.value ()
        else:
            assert slot.type () == obtainer_t
            return slot.value ().construct (**kwargs)


class BaseClass_C:
    def __init__ (self, cls):
        self._cls = cls
    def type (self):
        return item_base_class_t
    def construct (self):
        return self._cls

weapon = BaseClass_C (arkham.Weapon)
tome = BaseClass_C (arkham.Tome)

int_t = Type ("int_t", fun.matchclass (int))
str_t = Type ("str_t", fun.matchclass (str))
item_base_class_t = Type ("item_base_class_t", fun.matchclass (BaseClass_C))

def list_t (type):
    return Type ("list_t(%s)" % type.name (),
                 lambda arg: isinstance (arg, list) \
                     and all (type.match (emt) for emt in arg))

class _decks:
    def __init__ (self, ctx):
        self._decks = {}
        self._current = None
        self._ctx = ctx

    def __call__ (self, name):
        if name not in self._decks:
            self._decks[name] \
                = self._ctx._game.deck_matching (lambda deck:
                                                     deck.name () == name)
        self._current = self._decks[name]
        return self._current

    def current (self):
        return self._current

class _commit:
    def __init__ (self, ctx):
        self._que = []
        self._ctx = ctx
    def __call__ (self):
        for item in self._que:
            item.dump ()
            item.deploy (self._ctx)

class _item (Clause):
    def __init__ (self, ctx, *args):
        self._name_slot = SlotSingle (str_t)
        self._count_slot = SlotSingle (int_t, default = 1)
        self._inherit_slot = SlotMulti (item_base_class_t)
        Clause.__init__ (self, "item",
                         [self._name_slot,
                          self._count_slot,
                          self._inherit_slot])
        self.inbound (args)

        ctx.commit._que.append (self)
        ctx._current_item = self
        self._hands = 0
        self._price = 0
        self._overrides = []
        self._deck = ctx._current_deck ()

    def set_hands (self, hands):
        self._hands = hands

    def set_price (self, price):
        self._price = price

    def override_hook (self, hook):
        self._overrides.append (hook)

    def dump (self):
        print "item()"
        if self._hands > 0:
            print "hands(%d)" % self._hands
        if self._price > 0:
            print "price(%d)" % self._price
        for override in self._overrides:
            print str (override)

    def deploy (self, ctx):
        # xxx support both by-name (creation) and by-predicate (matching)
        name = self._name_slot.value ()
        cls = ctx._current_deck ().Item
        ctor = self
        class ItemProto (cls):
            def __init__ (self):
                cls.__init__ (self, name, ctor._price, ctor._hands)
        ItemProto.__bases__ = ItemProto.__bases__ \
            + tuple (base.construct ()
                     for base in self._inherit_slot.value ())
        item_proto = ItemProto ()
        self._deck.register (item_proto, self._count_slot.value ())

        for override in self._overrides:
            override.deploy (ctx, item_proto, ItemProto)

class _item_ctor:
    def __init__ (self, ctx):
        self._ctx = ctx
    def __call__ (self, *args):
        _item (self._ctx, *args)
        return self._ctx

class _Likewise:
    def __init__ (self):
        self._likewise = None
    def expand (self):
        return list (self._likewise)
    def update (self, decls):
        self._likewise = decls

likewise = _Likewise ()
def expand_likewise (decls):
    if len (decls) == 1 and decls[0] is likewise:
        return likewise.expand ()
    else:
        return decls

class itsup_init:
    def __init__ (self, game):
        self._game = game
        self.commit = _commit (self)
        self._deck_ctor = _decks (self)
        self._item_ctor = _item_ctor (self)
        self._current_item = None

    def pr(self, *args):
        print args
        return self

    def deck (self, *args):
        likewise.update (None)
        self._deck_ctor (*args)
        return self

    def _current_deck (self):
        return self._deck_ctor.current ()

    def item (self, *args):
        likewise.update (None)
        self._item_ctor (*args)
        return self

    def hand (self, i):
        assert isinstance (i, int)
        self._current_item.set_hands (i)
        return self

    def hands (self, i):
        return self.hand (i)

    def usd (self, i):
        assert isinstance (i, int)
        self._current_item.set_price (i)
        return self


    def bonus (self, *decls):
        decls = expand_likewise (decls)
        likewise.update (decls)
        self._current_item.override_hook (BonusHook_C (*decls))
        return self

    def check_correction (self, *decls):
        decls = expand_likewise (decls)
        likewise.update (decls)
        self._current_item.override_hook (CheckCorrectionHook_C (*decls))
        return self

    def movement (self, *decls):
        decls = expand_likewise (decls)
        likewise.update (decls)
        self._current_item.override_hook (MovementHook_C (*decls))
        return self

    def damage_correction (self, *decls):
        decls = expand_likewise (decls)
        likewise.update (decls)
        self._current_item.override_hook (DamageCorrectionHook_C (*decls))
        return self

    def dice_roll_successes_bonus (self, *decls):
        decls = expand_likewise (decls)
        likewise.update (decls)
        self._current_item.override_hook (DiceRollSuccessesBonusHook_C (*decls))
        return self

    def combat_turn (self, *decls):
        decls = expand_likewise (decls)
        likewise.update (decls)
        self._current_item.override_hook (CombatTurnHook_C (*decls))
        return self

# Obtainers.

successes = None
toughness = None

obtainer_t = Type ("obtainer_t", fun.not_ (fun.any))

# Investigator attributes.

class InvestigatorParamModifier_C (Clause):
    pass

inv_param_mod_t = Type ("inv_param_mod_t",
                        fun.matchclass (InvestigatorParamModifier_C))

class HealthAmount (InvestigatorParamModifier_C):
    def __init__ (self, *decls):
        self._value_slot = Slot_Obtainer ()
        self._aspect_slot = SlotSingle (aspect_t)
        InvestigatorParamModifier_C.__init__ \
            (self, "modifier",
             [self._value_slot,
              self._aspect_slot])
        self.inbound (decls)

    def _aspects (self, **kwargs):
        return {self._aspect_slot.value ():
                    self._obtainer_construct (self._value_slot, **kwargs)}

    def construct (self, **kwargs):
        return arkham.ImpactHealth (self._aspects (**kwargs))

    def lose_action (self, **kwargs):
        game = kwargs["game"]
        investigator = kwargs["investigator"]
        item = kwargs["item"]
        harm = arkham.HarmDamage (arkham.Damage (self._aspects (**kwargs)))
        return arkham.GameplayAction_CauseHarm (game, investigator, item, harm)

aspect_t = Type ("aspect_t", fun.matchclass (arkham.HealthAspect))
health_t = Type ("health_t", fun.matchclass (HealthAmount))

def sanity (amount_or_obtainer):
    return HealthAmount (amount_or_obtainer, arkham.health_sanity)

def stamina (amount_or_obtainer):
    return HealthAmount (amount_or_obtainer, arkham.health_stamina)

class movement_points (InvestigatorParamModifier_C):
    def __init__ (self, amount_or_obtainer):
        self._value_slot = Slot_Obtainer ()
        InvestigatorParamModifier_C.__init__ \
            (self, "movement_points",
             [self._value_slot])
        self.inbound ([amount_or_obtainer])

    def construct (self, **kwargs):
        assert self._value_slot.assigned ()
        return self._obtainer_construct (self._value_slot, **kwargs)

    def lose_action (self, **kwargs):
        return arkham.GameplayAction_SpendMovementPoints \
            (self.construct (**kwargs))

class clues (InvestigatorParamModifier_C):
    def __init__ (self, amount_or_obtainer):
        self._value_slot = Slot_Obtainer ()
        InvestigatorParamModifier_C.__init__ \
            (self, "clues",
             [self._value_slot])
        self.inbound ([amount_or_obtainer])

    def construct (self, **kwargs):
        assert self._value_slot.assigned ()
        return self._obtainer_construct (self._value_slot, **kwargs)

    def gain_action (self, **kwargs):
        return arkham.GameplayAction_GainClues \
            (self.construct (**kwargs))

class MonsterSet:
    def __init__ (self):
        pass
    def __call__ (self, action):
        pass

class Location:
    def __init__ (self):
        self.monsters = MonsterSet ()

class Owner:
    def __init__ (self):
        self.location = Location ()

owner = Owner ()

class BonusHook_C (Clause):
    def __init__ (self, *decls):
        self._checkbase_slot = SlotSingle (checkbase_t,
                                           default = _checkbase_any)
        self._bonus_slot = SlotSingle (modifier_t, int_t)
        self._monster_flags_slot = SlotMulti (flag_t)
        self._actions_slot = SlotMulti (action_t)
        Clause.__init__ (self, "bonus",
                         [self._checkbase_slot,
                          self._bonus_slot,
                          self._monster_flags_slot,
                          self._actions_slot])
        self.inbound (decls)

    def deploy (self, ctx, item_proto, item_cls):
        if not self._bonus_slot.assigned ():
            assert not "Bonus value needs to be specified."

        actions = self._actions_slot.value ()

        @ctx._game.bonus_hook.match \
            (fun.any, fun.any,
             self._monster_flag_matcher (self._monster_flags_slot),
             arkham.match_proto (item_cls),
             self._checkbase_slot.value ().matcher ())
        def do (game, investigator, subject, item, checkbase):
            args = dict (game=game, investigator=investigator,
                         subject=subject, item=item, checkbase=checkbase)

            for action in actions:
                if not action.can_enter (**args):
                    return []

            return self._bonus_slot.value ().construct (**args)

        @ctx._game.item_after_use_hook.match \
            (fun.any, fun.any,
             self._monster_flag_matcher (self._monster_flags_slot),
             arkham.match_proto (item_cls),
             self._checkbase_slot.value ().matcher ())
        def do (game, investigator, subject, item, checkbase):
            args = dict (game=game, investigator=investigator,
                         subject=subject, item=item, checkbase=checkbase)

            return arkham.GameplayAction_Multiple \
                (list (action.action (**args)
                       for action in actions))

class CheckCorrectionHook_C (Clause):
    def __init__ (self, *decls):
        self._checkbase_slot = SlotSingle (checkbase_t)
        self._actions_slot = SlotMulti (action_t)
        self._monster_flags_slot = SlotMulti (flag_t)
        Clause.__init__ (self, "check_correction",
                         [self._checkbase_slot,
                          self._actions_slot,
                          self._monster_flags_slot])
        self.inbound (decls)

    def deploy (self, ctx, item_proto, item_cls):
        actions = self._actions_slot.value ()

        @ctx._game.check_correction_actions_hook.match \
            (fun.any, fun.any,
             self._monster_flag_matcher (self._monster_flags_slot),
             arkham.match_proto (item_cls),
             self._checkbase_matcher (self._checkbase_slot),
             fun.any)
        def do (game, investigator, subject, item, checkbase, roll):
            args = dict (game=game, investigator=investigator,
                         subject=subject, item=item,
                         checkbase=checkbase, roll=roll)

            for action in actions:
                if not action.can_enter (**args):
                    return []

            return [arkham.GameplayAction_Multiple \
                        (list (action.action (**args)
                               for action in actions))]

class DamageCorrectionHook_C (Clause):
    def __init__ (self, *decls):
        self._actions_slot = SlotMulti (action_t)
        self._monster_flags_slot = SlotMulti (flag_t)
        Clause.__init__ (self, "check_correction",
                         [self._actions_slot,
                          self._monster_flags_slot])
        self.inbound (decls)

    def deploy (self, ctx, item_proto, item_cls):
        actions = self._actions_slot.value ()

        @ctx._game.damage_correction_actions_hook.match \
            (fun.any, fun.any,
             self._monster_flag_matcher (self._monster_flags_slot),
             arkham.match_proto (item_cls),
             fun.any)
        def do (game, investigator, subject, item, damage):
            args = dict (game=game, investigator=investigator,
                         subject=subject, item=item, damage=damage)

            for action in actions:
                if not action.can_enter (**args):
                    return []

            return [arkham.GameplayAction_Multiple \
                        (list (action.action (**args)
                               for action in actions))]

class MovementHook_C (Clause):
    def __init__ (self, *decls):
        self._actions_slot = SlotMulti (action_t)
        Clause.__init__ (self, "movement",
                         [self._actions_slot])
        self.inbound (decls)

    def deploy (self, ctx, item_proto, item_cls):
        actions = self._actions_slot.value ()
        assert len (actions) > 0

        def movement (proto, game, owner, item):
            args = dict (game=game, investigator=owner, item=item)

            for action in actions:
                if not action.can_enter (**args):
                    return []

            return [arkham.GameplayAction_Multiple \
                        (list (action.action (**args)
                               for action in actions))]

        item_cls.movement = movement

class CombatTurnHook_C (Clause):
    def __init__ (self, *decls):
        self._actions_slot = SlotMulti (action_t)
        Clause.__init__ (self, "combat_turn",
                         [self._actions_slot])
        self.inbound (decls)

    def deploy (self, ctx, item_proto, item_cls):
        actions = self._actions_slot.value ()
        assert len (actions) > 0

        def combat_turn (proto, combat, owner, monster, item):
            args = dict (combat=combat, game=combat.game,
                         investigator=owner, monster=monster, item=item)

            for action in actions:
                if not action.can_enter (**args):
                    return []

            return [arkham.GameplayAction_Multiple \
                        (list (action.action (**args)
                               for action in actions))]

        item_cls.combat_turn = combat_turn

class DiceRollSuccessesBonusHook_C (Clause):
    def __init__ (self, *decls):
        self._actions_slot = SlotMulti (action_t)
        self._diesides_slot = SlotMulti (dieside_t)
        self._value_slot = Slot_Obtainer ()
        self._monster_flags_slot = SlotMulti (flag_t)
        self._checkbase_slot = SlotSingle (checkbase_t)
        Clause.__init__ (self, "dice_roll_successes_bonus",
                         [self._actions_slot,
                          self._diesides_slot,
                          self._value_slot,
                          self._monster_flags_slot,
                          self._checkbase_slot])
        self.inbound (decls)

    def deploy (self, ctx, item_proto, item_cls):
        assert self._value_slot.assigned ()

        @ctx._game.dice_roll_successes_bonus_hook.match \
            (fun.any, fun.any,
             self._monster_flag_matcher (self._monster_flags_slot),
             arkham.match_proto (item_cls),
             self._checkbase_matcher (self._checkbase_slot),
             self._diesides_matcher (self._diesides_slot))
        def do (game, owner, subject, item, checkbase, dice):
            actions = self._actions_slot.value ()
            args = dict (game=game, investigator=owner, item=item,
                         checkbase=checkbase, dice=dice)

            for action in actions:
                if not action.can_enter (**args):
                    return []

            # xxx need to register after_use actions here... this
            # isn't solved yet.  Bonus hook currently takes after use
            # hook for itself.
            return self._obtainer_construct (self._value_slot, **args)


class flag (Clause):
    def __init__ (self, *decls):
        self._flag_name_slot = SlotSingle (str_t)
        Clause.__init__ (self, "flag", [self._flag_name_slot])
        self.inbound (decls)

    def construct (self):
        assert self._flag_name_slot.assigned ()
        return arkham.match_flag (self._flag_name_slot.value ())

flag_t = Type ("flag_t", fun.matchclass (flag))
undead = flag ("undead")


class _dieside (Clause):
    def __init__ (self, *decls):
        self._value_slot = Slot_Obtainer ()
        Clause.__init__ (self, "dieside",
                         [self._value_slot])
        self.inbound (decls)

    def construct (self, **kwargs):
        assert self._value_slot.assigned ()
        return self._obtainer_construct (self._value_slot, **kwargs)

dieside_t = Type ("dieside_t", fun.matchclass (_dieside))

r1 = _dieside (1)
r2 = _dieside (2)
r3 = _dieside (3)
r4 = _dieside (4)
r5 = _dieside (5)
r6 = _dieside (6)

# Checkbase wrappers.

class CheckbaseWrapper:
    def __init__ (self, checkbase):
        self._checkbase = checkbase

    def __call__ (self, *decls):
        return CheckGen_Skill (self, *decls)

    def __str__ (self):
        return self._checkbase.name ()

    def matcher (self):
        return fun.val == self._checkbase

    def construct (self, **kwargs):
        return self._checkbase

class CheckbaseWrapper_Any:
    def matcher (self):
        return fun.any
    # construct () intentionally left out

fight = CheckbaseWrapper (arkham.checkbase_fight)
lore = CheckbaseWrapper (arkham.checkbase_lore)
luck = CheckbaseWrapper (arkham.checkbase_luck)
sneak = CheckbaseWrapper (arkham.checkbase_sneak)
speed = CheckbaseWrapper (arkham.checkbase_speed)
will = CheckbaseWrapper (arkham.checkbase_will)

evade = CheckbaseWrapper (arkham.checkbase_evade)
horror = CheckbaseWrapper (arkham.checkbase_horror)
combat = CheckbaseWrapper (arkham.checkbase_combat)
spell = CheckbaseWrapper (arkham.checkbase_spell)

_checkbase_any = CheckbaseWrapper_Any ()

checkbase_t = Type ("checkbase_t", fun.matchclass ((CheckbaseWrapper,
                                                    CheckbaseWrapper_Any)))

# Checks.

class CheckGen_C (Clause):
    pass

check_gen_t = Type ("check_gen_t", fun.matchclass (CheckGen_C))

class CheckGen_Skill (CheckGen_C):
    def __init__ (self, *decls):
        self._checkbase_slot = SlotSingle (checkbase_t)
        self._value_slot = Slot_Obtainer () # modifier
        # number of successes needed
        self._diff_value_slot = SlotSingle (list_t (obtainer_t), list_t (int_t),
                                            default = [1])

        CheckGen_C.__init__ (self, "check_gen",
                             [self._checkbase_slot,
                              self._value_slot,
                              self._diff_value_slot])
        self.inbound (decls)

    def construct (self, **kwargs):
        slot = Slot_Obtainer ()
        assert slot.assign (*self._diff_value_slot.value ())

        return arkham.SkillCheck \
            (self._checkbase_slot.value ().construct (**kwargs),
             self._obtainer_construct (self._value_slot, **kwargs),
             self._obtainer_construct (slot, **kwargs))

class CheckGen_Fixed (CheckGen_C):
    def __init__ (self, *decls):
        self._value_slot = Slot_Obtainer ()
        # number of successes needed
        self._diff_value_slot = SlotSingle (list_t (obtainer_t), list_t (int_t),
                                            default = [1])
        CheckGen_C.__init__ (self, "fixed",
                             [self._value_slot,
                              self._diff_value_slot])
        self.inbound (decls)

    def construct (self, **kwargs):
        slot = Slot_Obtainer ()
        assert slot.assign (*self._diff_value_slot.value ())

        return arkham.SkillCheck \
            (arkham.CheckBase_Fixed (self._obtainer_construct \
                                         (self._value_slot, **kwargs)),
             0, self._obtainer_construct (slot, **kwargs))

def fixed (*decls):
    return CheckGen_Fixed (*decls)

# Action wrappers.

class Action_C (Clause):
    pass

class CardAction_C (Action_C):
    def can_enter (self, **kwargs):
        return True

class RollAction_C (Action_C):
    pass

class InvestigatorAction_C (Action_C):
    pass

action_t = Type ("action_t", fun.matchclass (Action_C))

class ExhaustAction_C (CardAction_C):
    def __init__ (self):
        CardAction_C.__init__ (self, "exhaust", [])

    def can_enter (self, **kwargs):
        return not kwargs["item"].exhausted ()

    def action (self, **kwargs):
        return arkham.GameplayAction_Exhaust (kwargs["item"])

class DiscardAction_C (CardAction_C):
    def __init__ (self):
        CardAction_C.__init__ (self, "discard", [])

    def action (self, **kwargs):
        return arkham.GameplayAction_Discard (kwargs["item"])

class RerollAction_C (RollAction_C):
    def __init__ (self):
        RollAction_C.__init__ (self, "reroll", [])

    def can_enter (self, **kwargs):
        return True

    def action (self, **kwargs):
        return arkham.GameplayAction_Reroll \
            (kwargs["subject"], kwargs["checkbase"], kwargs["roll"])

class lose (InvestigatorAction_C):
    def __init__ (self, *decls):
        self._inv_param_mod_slot = SlotMulti (inv_param_mod_t)
        InvestigatorAction_C.__init__ (self, "lose",
                                       [self._inv_param_mod_slot])
        self.inbound (decls)

    def can_enter (self, **kwargs):
        if kwargs["item"].exhausted ():
            return False

        # We don't check whether the investigator can sustain the harm
        # before offering the action, because the player may wish to
        # perform that action nonetheless.  Besides the investigator
        # can have a couple aces up his sleeve, such as a card that
        # reduces caused damage by 1.  Checking accurately for that is
        # not worth the trouble.  We do however check for movement
        # points or clues.
        for to_lose in self._inv_param_mod_slot.value ():
            if isinstance (to_lose, movement_points):
                investigator = kwargs["investigator"]
                item = kwargs["item"]
                mp = investigator.movement_points ()
                if mp == None or mp < to_lose.construct (**kwargs):
                    return False

            if isinstance (to_lose, clues):
                investigator = kwargs["investigator"]
                item = kwargs["item"]
                c = investigator.clues ()
                if c < to_lose.construct (**kwargs):
                    return False

        return True

    def action (self, **kwargs):
        assert self._inv_param_mod_slot.assigned ()
        return arkham.GameplayAction_Multiple \
            (list (to_lose.lose_action (**kwargs)
                   for to_lose in self._inv_param_mod_slot.value ()))

class gain (InvestigatorAction_C):
    def __init__ (self, *decls):
        self._inv_param_mod_slot = SlotSingle (inv_param_mod_t)
        InvestigatorAction_C.__init__ (self, "gain",
                                       [self._inv_param_mod_slot])
        self.inbound (decls)

    def can_enter (self, **kwargs):
        return not kwargs["item"].exhausted ()

    def action (self, **kwargs):
        assert self._inv_param_mod_slot.assigned ()
        return self._inv_param_mod_slot.value ().gain_action (**kwargs)

class reduce (InvestigatorAction_C):
    def __init__ (self, *decls):
        self._health_slot = SlotSingle (health_t)
        InvestigatorAction_C.__init__ (self, "reduce", [self._health_slot])
        self.inbound (decls)

    def can_enter (self, **kwargs):
        damage = kwargs["damage"]
        to_reduce = self._health_slot.value ().construct (**kwargs)
        if not any (aspect in damage.aspects ()
                    for aspect in to_reduce.aspects ()):
            return False

        return not kwargs["item"].exhausted ()

    def action (self, **kwargs):
        damage = kwargs["damage"]
        to_reduce = self._health_slot.value ().construct (**kwargs)
        return arkham.GameplayAction_Multiple \
            ([arkham.GameplayAction_ReduceDamage \
                  (damage, aspect, to_reduce.amount (aspect).amount ())
              for aspect in to_reduce.aspects ()])

class select (Action_C):
    def __init__ (self, *decls):
        self._actions_slot = SlotMulti (action_t)
        Action_C.__init__ (self, "select", [self._actions_slot])
        self.inbound (decls)

    def can_enter (self, **kwargs):
        return all (action.can_enter (**kwargs)
                    for action in self._actions_slot.value ())

    def action (self, **kwargs):
        return arkham.GameplayAction_Select \
            (list (action.action (**kwargs)
                   for action in self._actions_slot.value ()))

class repeat (Action_C):
    def __init__ (self, *decls):
        self._actions_slot = SlotMulti (action_t)
        self._value_slot = Slot_Obtainer () # how many times
        Action_C.__init__ (self, "repeat",
                           [self._actions_slot,
                            self._value_slot])
        self.inbound (decls)

    def can_enter (self, **kwargs):
        return all (action.can_enter (**kwargs)
                    for action in self._actions_slot.value ())

    def action (self, **kwargs):
        return arkham.GameplayAction_Repeat \
            (self._obtainer_construct (self._value_slot, **kwargs),
             arkham.GameplayAction_Multiple \
                 (list (action.action (**kwargs)
                        for action in self._actions_slot.value ())))

class NoAction_C (CardAction_C, RollAction_C, InvestigatorAction_C):
    def __init__ (self):
        CardAction_C.__init__ (self, None, [])

    def action (self, **kwargs):
        return None

class check (Action_C):
    def __init__ (self, *decls):
        self._check_gen_slot = SlotSingle (check_gen_t)
        self._actions_slot = SlotMulti (list_t (action_t))
        Clause.__init__ (self, "check",
                         [self._check_gen_slot,
                          self._actions_slot])
        self.inbound (decls)

    def can_enter (self, **kwargs):
        for action_group in self._actions_slot.value ():
            for action in action_group:
                if not action.can_enter (**kwargs):
                    return False
        return True

    def action (self, **kwargs):
        game = kwargs["game"]
        investigator = kwargs["investigator"]
        item = kwargs["item"]

        ac = self._actions_slot.value ()
        assert len (ac) in (1, 2)
        pass_actions = ac[0]
        fail_actions = ac[1] if len (ac) > 1 else []

        return arkham.GameplayAction_Conditional \
            (game, investigator, item,
             self._check_gen_slot.value ().construct (**kwargs),
             arkham.GameplayAction_Multiple \
                 (list (action.action (**kwargs) for action in pass_actions)) \
                 if pass_actions else None,
             arkham.GameplayAction_Multiple \
                 (list (action.action (**kwargs) for action in fail_actions)) \
                 if fail_actions else None)

class draw (InvestigatorAction_C):
    def __init__ (self, *decls):
        self._deckname_slot = SlotSingle (str_t)
        Clause.__init__ (self, "draw",
                         [self._deckname_slot])
        self.inbound (decls)

    def can_enter (self, **kwargs):
        return True

    def action (self, **kwargs):
        game = kwargs["game"]
        name = self._deckname_slot.value ()
        return arkham.GameplayAction_DrawItem \
            (game.deck_matching (lambda deck: deck.name () == name))

class PassCheck_C (Action_C):
    def __init__ (self):
        Clause.__init__ (self, "pass_check", [])

    def can_enter (self, **kwargs):
        return True

    def action (self, **kwargs):
        return arkham.GameplayAction_PassCheck ()

exhaust = ExhaustAction_C ()
discard = DiscardAction_C ()
reroll = RerollAction_C ()
_no_action = NoAction_C ()
pass_check = PassCheck_C ()

defeat = None # has implicit argument of MonsterSet

def cancel (*health_aspect):
    pass

def mark (amount, *actions):
    pass

# Bonuses

class C_Modifier (Clause):
    def __init__ (self, *decls):
        self._value_slot = Slot_Obtainer ()
        self._family_slot = SlotSingle (family_t)
        Clause.__init__ (self, "modifier",
                         [self._value_slot,
                          self._family_slot])
        self.inbound (decls)

    def type (self):
        return modifier_t

    def construct (self, **kwargs):
        # xxx proper checking & error message
        assert self._value_slot.assigned () and self._family_slot.assigned ()
        return arkham.Bonus (self._obtainer_construct (self._value_slot,
                                                       **kwargs),
                             self._family_slot.value ())

modifier_t = Type ("modifier_t", fun.matchclass (C_Modifier))

def physical (i):
    return C_Modifier (i, arkham.family_physical)

def magical (i):
    return C_Modifier (i, arkham.family_magical)

def indifferent (i):
    return C_Modifier (i, arkham.family_indifferent)

family_t = Type ("family_t", fun.matchclass (arkham.Family))
