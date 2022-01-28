import ipyvuetify as v
import traitlets
from ...state_traitlets_helpers import GlueState
from ...vuetify_helpers import load_template, link_glue_choices

__all__ = ['MapViewerStateWidget']

class MapViewerStateWidget(v.VuetifyTemplate):
    template = load_template('viewer_map.vue', __file__)
    c_att_items = traitlets.List().tag(sync=True)
    c_att_selected = traitlets.Int(allow_none=True).tag(sync=True)
    glue_state = GlueState().tag(sync=True)

    def __init__(self, viewer_state):
        super().__init__()
        
        self.glue_state = viewer_state
        
        link_glue_choices(self, viewer_state, 'c_att')