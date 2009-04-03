class TrackEvent:
    def event (self, game, owner, level):
        pass

class ConditionalEvent (TrackEvent):
    def __init__ (self, predicate, event_pass, event_fail = TrackEvent ()):
        self.m_pred = predicate
        self.m_pass = event_pass
        self.m_fail = event_fail
    def event (self, game, owner, level):
        if self.m_pred (game, owner, level):
            return self.m_pass.event (game, owner, level)
        else:
            return self.m_fail.event (game, owner, level)

class Track:
    def __init__ (self, owner):
        self.m_level = 0
        self.m_owner = owner
        self.m_events = []

    def add_event (self, event):
        self.m_events.append (event)

    def advance (self, game):
        self.m_level += 1
        for event in self.m_events:
            event.event (game, self.m_owner, self.m_level)

    def level (self):
        return self.m_level
