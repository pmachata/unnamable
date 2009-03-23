import arkham

class TerrorTrack (arkham.Track):
    def __init__ (self, owner):
        arkham.Track.__init__ (self, owner)

class Module (arkham.Module):
    def __init__ (self):
        arkham.Module.__init__ (self, "terror", "Terror Track")
        self.track = TerrorTrack (self)

    def consistent (self, mod_index):
        return True

    def terror_at_least_p (self, level):
        def predicate (*args):
            return self.track.level () >= level
        return predicate
