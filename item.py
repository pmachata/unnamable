from obj import ObjectWithAttributes, NamedObject, SubjectProto

class ItemProto (ObjectWithAttributes, NamedObject, SubjectProto):
    def __init__ (self, name, **attributes):
        ObjectWithAttributes.__init__ (self)
        NamedObject.__init__ (self, name)
        SubjectProto.__init__ (self, {}) # no special abilities
        self.apply_attributes (attributes)

    def discard (self):
        pass

    def upkeep_2 (self, game, owner, item):
        return []

    def upkeep_3 (self, game, owner, item):
        return []

    def movement_points_bonus (self, game, owner, item):
        return 0

    def movement (self, game, owner, item):
        return []

    def pre_combat (self, combat, owner, monster, item):
        return []

    def combat_turn (self, combat, owner, monster, item):
        return []

    def deal_with (self, game, owner, item):
        return []

# Items that inherit from this class are considered Weapons.
class Weapon:
    pass
