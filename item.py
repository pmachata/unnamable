from obj import ObjectWithAttributes

class ItemProto (ObjectWithAttributes):
    def __init__ (self, name, **attributes):
        ObjectWithAttributes.__init__ (self)
        self.apply_attributes (attributes)
        self.m_name = name

    def name (self):
        return self.m_name

    def discard (self):
        pass

    def upkeep (self, game, owner, item):
        return []

    def movement (self, game, owner, item):
        return []

    def combat_turn (self, combat, owner, monster, item):
        return []

    def deal_with (self, game, owner, item):
        return []

    def resistances (self):
        # Items in general have no resistances, so don't insist on
        # overriding this.
        return {}
