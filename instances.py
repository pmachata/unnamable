from loc import ObjectWithLocation
from obj import Subject

class ModuleInstance:
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
    def upkeep (self):
        return self.m_type.upkeep (self.m_game)

    def movement (self):
        return self.m_type.movement (self.m_game)

    def encounters (self):
        return self.m_type.encounters (self.m_game)

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
        self.m_proto = proto

    def name (self):
        return self.m_proto.name ()

    def movement (self, game):
        return self.m_proto.movement (game)

    def pre_combat (self, combat, investigator):
        return self.m_proto.pre_combat (combat, investigator)

    def combat_turn (self, combat, investigator):
        return self.m_proto.combat_turn (combat, investigator)

    def proto (self):
        return self.m_proto

    def attributes (self):
        return self.m_proto.attributes ()

    def discard (self):
        return self.m_proto.discard ()


class Item (Subject):
    def __init__ (self, proto):
        self.m_proto = proto
        self.m_exhausted = False

    def name (self):
        return self.m_proto.name ()

    def proto (self):
        return self.m_proto

    def attributes (self):
        return self.m_proto.attributes ()

    def hands (self):
        return self.m_proto.hands ()

    def exhausted (self):
        return self.m_exhausted

    def exhaust (self):
        assert not self.m_exhausted
        self.m_exhausted = True

    def discard (self):
        return self.m_proto.discard ()

    def __repr__ (self):
        return "<Item \"%s\">" % self.name ()

    # Game phases
    def upkeep (self, game, owner):
        self.m_exhausted = False
        return self.m_proto.upkeep (game, owner, self)

    def movement_points_bonus (self, game, owner):
        return self.m_proto.movement_points_bonus (game, owner, self)

    def movement (self, game, owner):
        return self.m_proto.movement (game, owner, self)

    def deal_with (self, game, owner):
        return self.m_proto.deal_with (game, owner, self)

    def pre_combat (self, combat, owner, monster):
        return self.m_proto.pre_combat (combat, owner, monster, self)

    def combat_turn (self, combat, owner, monster):
        return self.m_proto.combat_turn (combat, owner, monster, self)
