from obj import ObjectWithAttributes

class Neighborhood (ObjectWithAttributes):
    def __init__ (self):
        ObjectWithAttributes.__init__ (self)

class Connection (ObjectWithAttributes):
    def __init__ (self, dest):
        ObjectWithAttributes.__init__ (self)
        self.m_dest = dest

    def dest (self):
        return self.m_dest

class Location (ObjectWithAttributes):
    def __init__ (self, name, neighborhood = None):
        ObjectWithAttributes.__init__ (self)
        self.m_name = name
        self.m_neighborhood = neighborhood
        self.m_connections = set ()
        self.m_clue_tokens = 0

    def add_connection (self, conn):
        assert conn not in self.m_connections
        self.m_connections.add (conn)

    def name (self):
        return self.m_name

    def add_clue_tokens (self, n):
        assert n >= 0
        self.m_clue_tokens += n

    def connections (self):
        return list (self.m_connections)

class ObjectWithLocation:
    def __init__ (self, initial_location):
        self.m_location = initial_location

    def location (self):
        return self.m_location

    def move_to (self, location):
        print "ObjectWithLocation.move_to %s->%s" % (self.name (), location.name () if location else "None")
        self.m_location = location
