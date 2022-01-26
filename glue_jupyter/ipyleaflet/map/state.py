import numpy as np

from glue.core import BaseData, Subset

from echo import delay_callback
from glue.viewers.common.state import ViewerState, LayerState

from glue.viewers.matplotlib.state import (DeferredDrawCallbackProperty as DDCProperty,
                                           DeferredDrawSelectionCallbackProperty as DDSCProperty)
#from glue.core.state_objects import (StateAttributeLimitsHelper,
#                                     StateAttributeHistogramHelper)
from glue.core.exceptions import IncompatibleAttribute, IncompatibleDataException
from glue.core.data_combo_helper import ComponentIDComboHelper
from glue.utils import defer_draw, datetime64_to_mpl
from glue.utils.decorators import avoid_circular

__all__ = ['MapViewerState', 'MapLayerState']


class MapViewerState(ViewerState):
    """
    A state class that includes all the attributes for a map viewer.
    """

    c_att = DDSCProperty(docstring='The attribute to display as a choropleth')
    lon = DDCProperty(docstring='Longitude at the center of the map')
    lat = DDCProperty(docstring='Latitude at the center of the map')
    zoom_level = DDCProperty(docstring='Zoom level for the map')

    def __init__(self, **kwargs):

        super(MapViewerState, self).__init__()

        self.add_callback('layers', self._layers_changed)

        self.c_att_helper = ComponentIDComboHelper(self, 'c_att')
        #print(self.c_att_helper)
        #print(self.c_att_helper._data)
        #import pdb; pdb.set_trace()
        #self._viewer_state.add_callback('c_att', self._on_attribute_change)

        self.c_metadata = None
        #print(self.layers_data)
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
        print(self.c_att_helper)
        print(self.c_att_helper._data)
        self.c_geo_metadata = self.c_att_helper._data[0].meta['geo']


class MapLayerState(LayerState):
    """
    A state class that includes all the attributes for layers in a choropleth map.
    
    This should have attributes for:
    
    colorscale (a list of available cmaps: 
                from branca.colormap import linear for continuous
                qualitative for categorical)
    visible, of course
    color_steps (whether to turn a continuous variable into a stepped display) <-- less important
    """

    #def __init__(self, **kwargs): #Calling this init is fubar
    #        
    #    super(MapLayerState, self).__init__()
    #    #self.ids = self.layer['ids']

    @property
    def viewer_state(self):
        return self._viewer_state

    @viewer_state.setter
    def viewer_state(self, viewer_state):
        self._viewer_state = viewer_state

class MapSubsetLayerState(LayerState):
    """
    Currently this does not do anything
    """
    def __init__(self, *args, **kwargs):
    #self.uuid = str(uuid.uuid4())
        super(MapSubsetLayerState, self).__init__(*args, **kwargs)
    
