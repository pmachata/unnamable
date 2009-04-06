import arkham
import checks
import fun

def build (game, module):

    # xxx .18 Derringer cannot be lost or stolen unless you choose to
    # allow it.
    class Derringer18 (arkham.InvestigatorItem):
        pass

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, fun.matchclass (Derringer18), fun.matchvalue ("combat"))
    def do (game, investigator, subject, item, skill_name):
        return 2

    module.m_common_deck.register (Derringer18 (".18 Derringer", 3, 1), 1)


    # ---

    class Revolver38 (arkham.InvestigatorItem):
        pass

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, fun.matchclass (Revolver38), fun.matchvalue ("combat"))
    def do (game, investigator, subject, item, skill_name):
        return 3

    module.m_common_deck.register (Derringer18 (".38 Revolver", 4, 1), 1)


    # ---

    class Automatic45 (arkham.InvestigatorItem):
        pass

    @arkham.bonus_hook.match \
        (fun.any, fun.any, fun.any, fun.matchclass (Revolver38), fun.matchvalue ("combat"))
    def do (game, investigator, subject, item, skill_name):
        return 4

    module.m_common_deck.register (Derringer18 (".45 Automatic", 5, 1), 1)
