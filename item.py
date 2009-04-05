from obj import *

class Item (ObjectWithAttributes):
    def __init__ (self, name, **attributes):
        ObjectWithAttributes.__init__ (self)
        self.apply_attributes (attributes)
        self.m_name = name

    def name (self):
        return self.m_name

    def discard (self):
        pass
