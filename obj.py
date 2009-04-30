import fun

class Attributes:
    def __init__ (self):
        self.m_attributes = {}

    def set (self, name, value):
        if value is None:
            del self.m_attributes[name]
        else:
            self.m_attributes[name] = value

    def has (self, name):
        return name in self.m_attributes

    def flag (self, name):
        if not self.has (name):
            return False
        else:
            ret = self.m_attributes[name]
            if ret != True and ret != False:
                raise RuntimeError ("Flag attribute not a boolean")
            return ret

    def get (self, name):
        if not self.has (name):
            return None
        else:
            return self.m_attributes[name]

    def fmt_flags (self):
        ret = []
        for attr, val in self.m_attributes.iteritems ():
            if val != True and val != False:
                ret.append ("%s=%s" % (attr, val))
            else:
                ret.append ("%s%s" % ("" if val else "not ",
                                      attr))
        return ";".join (ret)

def match_attribute (**kwargs):
    key, = kwargs.keys ()
    value, = kwargs.values ()
    def match (arg):
        try:
            has = arg.has (key)
        except AttributeError:
            has = False

        if not has:
            return False
        else:
            return arg.get (key) == value

    return match

def match_flag (flag):
    def match (arg):
        return arg.attributes ().flag (flag)
    return match

def get_flag (flag):
    def match (arg):
        return arg.attributes ().get (flag)
    return match

def cond_bind_attrib (attrib):
    return fun.if_else (match_flag (attrib), get_flag (attrib))

class ObjectWithAttributes:
    def __init__ (self):
        self.m_attributes = Attributes ()

    def apply_attributes (self, dict):
        for k, v in dict.iteritems ():
            assert not self.m_attributes.has (k)
            self.m_attributes.set (k, v)

    def attributes (self):
        return self.m_attributes

class GameplayObject:
    # Game play phases.
    def turn_start (self, game):
        return []
    def upkeep (self, game):
        return []
    def movement (self, game):
        return []
    def encounters (self, game):
        return []
    def mythos (self, game):
        return []

class Subject:
    def resistances (self):
        return self.m_proto.resistances ()
