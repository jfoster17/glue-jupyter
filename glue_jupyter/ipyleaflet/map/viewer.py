from glue.core.subset import roi_to_subset_state
from glue.core.roi import RangeROI
from .state import MapViewerState

from ..common.viewer import IpyLeafletBaseView

from .layer_artist import IPyLeafletMapLayerArtist
from glue_jupyter.common.state_widgets.layer_map import MapLayerStateWidget
from glue_jupyter.common.state_widgets.viewer_map import MapViewerStateWidget

__all__ = ['IPyLeafletMapView']


class IPyLeafletMapView(IpyLeafletBaseView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    large_data_size = 1e5
    is2d = False

    _state_cls = MapViewerState
    _options_cls = MapViewerStateWidget #Need a new one of these
    _data_artist_cls = IPyLeafletMapLayerArtist
    _subset_artist_cls = IPyLeafletMapLayerArtist
    _layer_style_widget_cls = MapLayerStateWidget #Need a new one of these

    tools = []#'bqplot:home', 'bqplot:panzoom', 'bqplot:xrange']

    def _roi_to_subset_state(self, roi):
        # TODO: copy paste from glue/viewers/histogram/qt/data_viewer.py
        # TODO Does subset get applied to all data or just visible data?

        bins = self.state.bins

        x = roi.to_polygon()[0]
        lo, hi = min(x), max(x)

        if lo >= bins.min():
            lo = bins[bins <= lo].max()
        if hi <= bins.max():
            hi = bins[bins >= hi].min()

        roi_new = RangeROI(min=lo, max=hi, orientation='x')

        return roi_to_subset_state(roi_new, x_att=self.state.x_att)
