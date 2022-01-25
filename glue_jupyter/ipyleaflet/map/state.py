import numpy as np

from glue.core import BaseData, Subset

from echo import delay_callback
from glue.viewers.matplotlib.state import (MatplotlibDataViewerState,
                                           MatplotlibLayerState,
                                           DeferredDrawCallbackProperty as DDCProperty,
                                           DeferredDrawSelectionCallbackProperty as DDSCProperty)
#from glue.core.state_objects import (StateAttributeLimitsHelper,
#                                     StateAttributeHistogramHelper)
from glue.core.exceptions import IncompatibleAttribute, IncompatibleDataException
from glue.core.data_combo_helper import ComponentIDComboHelper
from glue.utils import defer_draw, datetime64_to_mpl
from glue.utils.decorators import avoid_circular

__all__ = ['MapViewerState', 'MapLayerState']


class MapViewerState(MatplotlibDataViewerState):
    """
    A state class that includes all the attributes for a map viewer.
    """

    c_att = DDSCProperty(docstring='The attribute to display as a choropleth')

    def __init__(self, **kwargs):

        super(MapViewerState, self).__init__()

        self.add_callback('layers', self._layers_changed)

        self.c_att_helper = ComponentIDComboHelper(self, 'c_att')

        self.update_from_dict(kwargs)


    def reset_limits(self):
        pass

    def _update_priority(self, name):
        if name == 'layers':
            return 2
        elif name.endswith('_log'):
            return 0.5
        elif name.endswith(('_min', '_max', '_bin')):
            return 0
        else:
            return 1

    def flip_x(self):
        pass

    @defer_draw
    def _layers_changed(self, *args):
        self.c_att_helper.set_multiple_data(self.layers_data)


class MapLayerState(MatplotlibLayerState):
    """
    A state class that includes all the attributes for layers in a choropleth map.
    """

    @property
    def viewer_state(self):
        return self._viewer_state

    @viewer_state.setter
    def viewer_state(self, viewer_state):
        self._viewer_state = viewer_state


