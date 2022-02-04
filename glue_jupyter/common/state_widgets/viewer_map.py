import ipyvuetify as v

import traitlets

__all__ = ['MapViewerStateWidget']


class MapViewerStateWidget(v.VuetifyTemplate):
    template = traitlets.Unicode('<span></span>').tag(sync=True)

    def __init__(self, viewer_state):
        super().__init__()

    def cleanup(self):
        pass
