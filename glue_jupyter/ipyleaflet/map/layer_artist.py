import numpy as np
import bqplot

from glue.core.exceptions import IncompatibleAttribute
from glue.viewers.common.layer_artist import LayerArtist
from glue.utils import color2hex

from ...link import link, dlink
from .state import MapLayerState

__all__ = ['IPyLeafletMapLayerArtist']


class IPyLeafletMapLayerArtist(LayerArtist):

    _layer_state_cls = MapLayerState

    def __init__(self, view, viewer_state, layer_state=None, layer=None):

        super(IPyLeafletMapLayerArtist, self).__init__(viewer_state,
                                                         layer_state=layer_state, layer=layer)

        self.view = view


    def remove(self):
        pass

    def _update_visual_attributes(self):

        if not self.enabled:
            return
        # TODO: set visual attrs
        self.redraw()

    def update(self):
       # self.state.reset_cache()
        self.redraw()
