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
    def upkeep_1 (self, game):
        return []
    def upkeep_2 (self, game):
        return []
    def upkeep_3 (self, game):
        return []
    def movement (self, game):
        return []
    def encounters_1 (self, game):
        return []
    def encounters_2 (self, game):
        return []
    def mythos (self, game):
        return []

class ObjectWithPrototype:
    def __init__ (self, proto):
        self.m_proto = proto

    def proto (self):
        return self.m_proto

class SubjectProto:
    def __init__ (self, special_abilities = []):
        try:
            # is it convertible to a dictionary?
            self.m_special_abilities = dict (special_abilities)
        except TypeError:
            # no it's not
            self.m_special_abilities \
                = dict ((ability, None)
                        for ability in special_abilities)

    def special_abilities (self):
        return dict (self.m_special_abilities)

    def has_special_ability (self, ability):
        return ability in self.m_special_abilities

    def special_ability_param (self, ability):
        return self.m_special_abilities[ability]

class Subject (ObjectWithPrototype):
    def __init__ (self, proto):
        ObjectWithPrototype.__init__ (self, proto)
        self.m_added_abilities = {}
        self.m_removed_abilities = set ()

    def special_abilities (self):
        ret = self.m_proto.special_abilities ()
        for ability in self.m_removed_abilities:
            del ret[ability]
        ret.update (self.m_added_abilities)
        return ret

    def has_special_ability (self, ability):
        return ability in self.special_abilities ()

    def add_special_ability (self, ability, argument = None):
        assert ability not in self.special_abilities ()
        if ability in self.m_removed_abilities:
            self.m_removed_abilities.remove (ability)
        else:
            self.m_added_abilities[ability] = argument
        assert ability in self.special_abilities ()

    def remove_special_ability (self, ability):
        assert ability in self.special_abilities ()
        if ability in self.m_added_abilities:
            del self.m_added_abilities[ability]
        else:
            self.m_removed_abilities.add (ability)
        assert ability not in self.special_abilities ()

    def special_ability_param (self, ability):
        return self.special_abilities ()[ability]

    def cancel_special_ability_customization (self, ability):
        if ability in self.m_removed_abilities:
            self.m_removed_abilities.remove (ability)
        if ability in self.m_added_abilities:
            del self.m_added_abilities[ability]

class NamedObject:
    def __init__ (self, name):
        self.m_name = name

    def name (self):
        return self.m_name

def has_special_ability (ability):
    def match (arg):
        return arg.has_special_ability (ability)
    return match
