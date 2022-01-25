import ipyvuetify as v

import traitlets

__all__ = ['MapLayerStateWidget']


class MapLayerStateWidget(v.VuetifyTemplate):
    template = traitlets.Unicode('<span></span>').tag(sync=True)

    def __init__(self, layer_state):
        super().__init__()

    def cleanup(self):
        pass
