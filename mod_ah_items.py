import arkham
import checks

def build (game, module):

    class Derringer18 (arkham.InvestigatorItem):
        pass

    module.m_common_deck.register (Derringer18 (".18 Derringer", 3, 1), 1)
