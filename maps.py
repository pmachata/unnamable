import arkham

class draw_from:
    def __init__ (self, location):
        assert location
        # cursor for drawing main line
        self.m_cur = location
        # coordinates of last created connection
        self.m_loc_1 = None
        self.m_loc_2 = None

    def conn (self, loc1, loc2, attrs):
        assert loc1
        assert loc2
        conn = arkham.Connection (loc2)
        loc1.add_connection (conn)
        conn.apply_attributes (attrs)
        self.m_loc_1 = loc1
        self.m_loc_2 = loc2

    def to (self, location, **kwargs):
        self.conn (self.m_cur, location, kwargs)
        self.m_cur = location
        return self

    def out (self, location, **kwargs):
        self.conn (self.m_cur, location, kwargs)
        return self

    def back (self, **kwargs):
        self.conn (self.m_loc_2, self.m_loc_1, kwargs)
        return self

_cur_neighborhood = None
_game = None
def in_neighborhood (neighborhood):
    global _cur_neighborhood
    _cur_neighborhood = neighborhood

def neighborhood (game):
    global _game
    ret = arkham.Neighborhood ()
    _game = game
    _game.add_neighborhood (ret)
    return ret

def location (name, **kwargs):
    ret = arkham.Location (name, _cur_neighborhood)
    _game.add_location (ret)
    ret.apply_attributes (kwargs)
    return ret
