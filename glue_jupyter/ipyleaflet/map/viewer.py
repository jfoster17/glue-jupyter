from glue.core.subset import roi_to_subset_state
from .state import MapViewerState

from ..common.viewer import IpyLeafletBaseView

from .layer_artist import IPyLeafletMapLayerArtist, IPyLeafletMapSubsetLayerArtist
from glue_jupyter.common.state_widgets.layer_map import MapLayerStateWidget
from glue_jupyter.common.state_widgets.viewer_map import MapViewerStateWidget

from glue.core.roi import PointROI


__all__ = ['IPyLeafletMapView']


class IPyLeafletMapView(IpyLeafletBaseView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    large_data_size = 1e5
    is2d = False

    _state_cls = MapViewerState
    _options_cls = MapViewerStateWidget #Need a new one of these
    _data_artist_cls = IPyLeafletMapLayerArtist
    _subset_artist_cls = IPyLeafletMapSubsetLayerArtist
    _layer_style_widget_cls = MapLayerStateWidget #Need a new one of these

    tools = ['ipyleaflet:pointselect']#'bqplot:home', 'bqplot:panzoom', 'bqplot:xrange']

    def _roi_to_subset_state(self, roi):
        # TODO: copy paste from glue/viewers/histogram/qt/data_viewer.py
        # TODO Does subset get applied to all data or just visible data?

        #if isistance(roi, PointROI): #This will be an OR/AND? not sure this will work
        #    subset_state = ElementSubsetState()
        
        #else:
        #    raise TypeError("Only PointROI selections are supported")


        return roi_to_subset_state(roi_new, c_att=self.state.c_att)
