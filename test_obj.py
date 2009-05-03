from obj import Subject, SubjectProto

class Proto (SubjectProto):
    def __init__ (self):
        SubjectProto.__init__ (self, [1, 2])

proto = Proto ()
obj1 = Subject (proto)
obj2 = Subject (proto)
assert obj1.has_special_ability (1)
assert obj1.has_special_ability (2)
assert obj2.has_special_ability (1)
assert obj2.has_special_ability (2)

obj1.add_special_ability (3)
assert obj1.has_special_ability (3)
assert not obj2.has_special_ability (3)

obj1.remove_special_ability (3)
assert not obj1.has_special_ability (3)

obj1.remove_special_ability (2)
assert not obj1.has_special_ability (2)
assert obj2.has_special_ability (2)

obj1.add_special_ability (3)
assert obj1.has_special_ability (3)
assert not obj1.has_special_ability (2)

obj1.add_special_ability (2)
assert obj1.has_special_ability (2)

obj1.add_special_ability (4, "ahoj")
assert obj1.special_ability_param (4) == "ahoj"
