from glue.core.subset import roi_to_subset_state
from .state import MapViewerState

from .layer_artist import IPyLeafletMapLayerArtist, IPyLeafletMapSubsetLayerArtist
from glue_jupyter.common.state_widgets.layer_map import MapLayerStateWidget
from glue_jupyter.common.state_widgets.viewer_map import MapViewerStateWidget

from glue.core.roi import PointROI

from glue.core.subset import roi_to_subset_state
from glue.core.command import ApplySubsetState

from echo.callback_container import CallbackContainer

from ...view import IPyWidgetView
from ...link import dlink, on_change
from ...utils import float_or_none, debounced, get_ioloop

import ipyleaflet


__all__ = ['IPyLeafletMapView']


class IPyLeafletMapView(IPyWidgetView):

    allow_duplicate_data = True
    allow_duplicate_subset = False
    _default_mouse_mode_cls = None
    

    _state_cls = MapViewerState
    _options_cls = MapViewerStateWidget 
    _data_artist_cls = IPyLeafletMapLayerArtist
    _subset_artist_cls = IPyLeafletMapSubsetLayerArtist
    _layer_style_widget_cls = MapLayerStateWidget

    tools = ['ipyleaflet:pointselect','ipyleaflet:rectangleselect']

    def __init__(self, session, state=None):
        self.mapfigure = ipyleaflet.Map(center=(40, -100), zoom=4)
        
        super(IPyLeafletMapView, self).__init__(session, state=state)
        
        #self.state.remove_callback('layers', self._sync_layer_artist_container)
        #self.state.add_callback('layers', self._sync_layer_artist_container, priority=10000)
        
        self.create_layout()
        
    def get_layer_artist(self, cls, layer=None, layer_state=None):
        return cls(self.mapfigure, self.state, layer=layer, layer_state=layer_state)
    
    @property
    def figure_widget(self):
        return self.mapfigure
    
    def redraw(self):
        pass
    