import ipyvuetify as v
import traitlets
from ...state_traitlets_helpers import GlueState
from ...vuetify_helpers import load_template, link_glue_choices

__all__ = ['MapViewerStateWidget']

class MapViewerStateWidget(v.VuetifyTemplate):
    template = traitlets.Unicode('<span></span>').tag(sync=True)

    def __init__(self, layer_state):
        super().__init__()
    
    def cleanup(self):
        pass
