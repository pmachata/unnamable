import arkham
import modules
import maps
import fun

class EndTest (Exception):
    def __init__ (self, success):
        self.m_success = success
    def success (self):
        return self.m_success

class TestUI (arkham.UI):
    def __init__ (self, controller):
        self.m_controller = controller

    def setup_players (self, game):
        self.m_controller.setup_players (game)

    def select_action (self, game, investigator, actions):
        print actions
        selector = self.m_controller.next ()
        actions = [action for action in actions if selector (action)]
        assert len (actions) == 1
        return actions[0]

class FixedSkills:
    def __init__ (self, **skills):
        self.m_skills = dict (skills)

    def check (self, skill):
        return self.m_skills[skill]

class TestInvestigator (arkham.CommonInvestigator):
    def __init__ (self, name, home,
                  sanity=1, stamina=1,
                  money=0, clues=0, **skills):
        arkham.CommonInvestigator.__init__ \
            (self, name,
             {arkham.health_sanity: sanity,
              arkham.health_stamina: stamina},
             money, clues,
             FixedSkills (**skills), home)

    def initial_movement_points (self):
        return 0

class ModuleProto (arkham.ModuleProto):
    def __init__ (self, constructor, request):
        arkham.ModuleProto.__init__ (self, "test", "Test Board")
        self.m_constructor = constructor
        self.m_locations = {}
        self.m_request = list (request)

    def consistent (self, mod_index):
        for req in self.m_request:
            if not mod_index.request (req):
                return False
        return True

    def construct (self, game):
        self.m_constructor.construct (game, self)

    def add_locations (self, *names):
        ret = []
        for name in names:
            if isinstance (name, tuple):
                name, attributes = name
            else:
                attributes = {}
            loc = maps.location ("Loc" + name, **attributes)
            self.m_locations[name] = loc
            ret.append (loc)
        return ret

    def add_investigator (self, game, name, location, **skills):
        ret = TestInvestigator ("Inv" + name,
                                self.m_locations[location], **skills)
        game.add_investigator (ret)
        return ret

    def add_monster (self, game, location, proto):
        mon = arkham.Monster (proto)
        game.add_monster (mon, self.m_locations[location])
        return [mon]

def match_investigator (name):
    return lambda arg: arg.name () == "Inv" + name

def match_combat (klass):
    return lambda arg: isinstance (arg.game, klass)

class TestGame (arkham.Game):
    def __init__ (self, controller, request=[]):
        idx = arkham.ModuleIndex ()
        modules.discover_modules (idx)
        controller.add_modules (idx)
        idx.add_module (ModuleProto (controller, request))
        idx.request ("test")

        arkham.Game.__init__ (self, idx.requested_modules (),
                              TestUI (controller))
        self.m_controller = controller

    def roll (self):
        ret = self.m_controller.next ()
        assert isinstance (ret, int), ret
        assert ret > 0
        return ret

@arkham.normal_one_dice_roll_hook.match (fun.matchclass (TestGame), fun.any, fun.any, fun.any)
def do (game, investigator, subject, skill_name):
    return game.roll ()

class Controller:
    def __init__ (self):
        self.m_generator = self.actions ()

    def next (self):
        return self.m_generator.next ()

    def use_investigators (self, game, investigators):
        ret = []
        for investigator in game.all_investigators ():
            if investigator.name () in investigators:
                game.use_investigator (investigator)
                ret.append (investigator)
        return ret

    def construct (self, game, module):
        pass

    def add_modules (self, idx):
        pass

def run_test (game):
    try:
        game.run ()
    except EndTest, e:
        if not e.success ():
            print "FAILURE"
