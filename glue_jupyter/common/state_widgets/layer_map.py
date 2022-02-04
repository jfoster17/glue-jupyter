import ipyvuetify as v
import traitlets
from ...state_traitlets_helpers import GlueState
from ...vuetify_helpers import load_template, link_glue_choices

__all__ = ['MapLayerStateWidget']

class MapLayerStateWidget(v.VuetifyTemplate):
    template = load_template('layer_map.vue', __file__)
    c_att_items = traitlets.List().tag(sync=True)
    c_att_selected = traitlets.Int(allow_none=True).tag(sync=True)
    glue_state = GlueState().tag(sync=True)

    def __init__(self, layer_state):
        super().__init__()
        
        self.glue_state = layer_state
        
        link_glue_choices(self, layer_state, 'c_att')