from loc import ObjectWithLocation
from obj import Subject

class Module:
    def __init__ (self, game, type):
        self.m_game = game
        self.m_type = type

    def game (self):
        return self.m_game

    def name (self):
        return self.m_type.name ()

    # Game construction phases.
    def construct (self):
        return self.m_type.construct (self.m_game)

    def post_construct (self):
        return self.m_type.post_construct (self.m_game)

    def before_turn_0 (self):
        return self.m_type.before_turn_0 (self.m_game)

    def turn_0 (self):
        return self.m_type.turn_0 (self.m_game)

    # Game play phases.
    def upkeep_1 (self):
        return self.m_type.upkeep_1 (self.m_game)
    def upkeep_2 (self):
        return self.m_type.upkeep_2 (self.m_game)
    def upkeep_3 (self):
        return self.m_type.upkeep_3 (self.m_game)

    def movement (self):
        return self.m_type.movement (self.m_game)

    def encounters_1 (self):
        return self.m_type.encounters_1 (self.m_game)
    def encounters_2 (self):
        return self.m_type.encounters_2 (self.m_game)

    def mythos (self):
        return self.m_type.mythos (self.m_game)

    # Combat phases.
    def pre_combat (self, combat, investigator, monster):
        return self.m_type.pre_combat (combat, investigator, monster)

    def combat_turn (self, combat, investigator, monster):
        return self.m_type.combat_turn (combat, investigator, monster)

    # Unconscious/Insane actions.
    def investigator_dead (self, investigator):
        return self.m_type.investigator_dead (self.m_game, investigator)

class Monster (ObjectWithLocation, Subject):
    def __init__ (self, proto):
        ObjectWithLocation.__init__ (self, None)
        Subject.__init__ (self, proto)

    def name (self):
        return self.m_proto.name ()

    def movement (self, game):
        return self.proto ().movement (game)

    def pre_combat (self, combat, investigator):
        return self.proto ().pre_combat (combat, investigator)

    def combat_turn (self, combat, investigator):
        return self.proto ().combat_turn (combat, investigator)

    def attributes (self):
        return self.proto ().attributes ()

    def discard (self):
        return self.proto ().discard ()

class Item (Subject):
    def __init__ (self, proto):
        Subject.__init__ (self, proto)
        self.m_exhausted = False

    def name (self):
        return self.proto ().name ()

    def attributes (self):
        return self.proto ().attributes ()

    def hands (self):
        return self.proto ().hands ()

    def exhausted (self):
        return self.m_exhausted

    def exhaust (self):
        assert not self.m_exhausted
        self.m_exhausted = True

    def discard (self):
        return self.proto ().discard ()

    def __repr__ (self):
        return "<Item \"%s\">" % self.name ()

    # Game phases
    def upkeep_1 (self, game, owner):
        self.m_exhausted = False

    def upkeep_2 (self, game, owner):
        return self.proto ().upkeep_2 (game, owner, self)

    def upkeep_3 (self, game, owner):
        return self.proto ().upkeep_3 (game, owner, self)

    def movement_points_bonus (self, game, owner):
        return self.proto ().movement_points_bonus (game, owner, self)

    def movement (self, game, owner):
        return self.proto ().movement (game, owner, self)

    def deal_with (self, game, owner):
        return self.proto ().deal_with (game, owner, self)

    def pre_combat (self, combat, owner, monster):
        return self.proto ().pre_combat (combat, owner, monster, self)

    def combat_turn (self, combat, owner, monster):
        return self.proto ().combat_turn (combat, owner, monster, self)
