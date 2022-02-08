import numpy as np

from glue.core import BaseData, Subset

from echo import delay_callback
from glue.viewers.common.state import ViewerState, LayerState

from echo import CallbackProperty, SelectionCallbackProperty

from glue.core.exceptions import IncompatibleAttribute, IncompatibleDataException
from glue.core.data_combo_helper import ComponentIDComboHelper, ComboHelper
from glue.utils import defer_draw, datetime64_to_mpl
from glue.utils.decorators import avoid_circular
from ipyleaflet import Map, basemaps, basemap_to_tiles

from glue.config import colormaps
from branca.colormap import linear

__all__ = ['MapViewerState', 'MapLayerState']


class MapViewerState(ViewerState):
    """
    A state class that manages the display of an ipyleaflet Map object:
    
    https://ipyleaflet.readthedocs.io/en/latest/api_reference/map.html
    
    which serves as the base for a MapViewer
    """

    center = CallbackProperty((40,-100),docstring='(Lon, Lat) at the center of the map')
    #lon = CallbackProperty(docstring='Longitude at the center of the map')
    #lat = CallbackProperty(docstring='Latitude at the center of the map')
    zoom_level = CallbackProperty(4, docstring='Zoom level for the map')
    basemap = CallbackProperty(basemaps.OpenStreetMap.Mapnik, docstring='Basemap to display')

    def __init__(self, **kwargs):

        super(MapViewerState, self).__init__()

        self.add_callback('layers', self._layers_changed)
        #self.add_callback('basemap', self._basemap_changed)
        #self.add_callback('basemap', self._basemap_changed)
        #print(f'layers={self.layers}')
        self.update_from_dict(kwargs)

        #self.mapfigure = None
    
    
    #def _basemap_changed(self, basemap):
    #    """
    #    The syntax to update a the basemap is sort of funky but this sort of thing
    #    could work if we attach a callback to the layers (first layer?) of the map
    #    """
    #    print(f"Called _basemap_changed with {basemap}")
    #    if (self.map is not None):# and (len(self.map.layers) > 0):
    #        print(f"self.map is not None")
    #        
    #        self.map.layers=[basemap_to_tiles(basemap)]
        
    def _on_attribute_change(self):
        pass

    def reset_limits(self):
        pass

    def _update_priority(self, name):
        pass
        
    def flip_x(self):
        pass

    @defer_draw
    def _layers_changed(self, *args):
        #print(f'layers={self.layers}')
        #print(f'layers={self.layers_data}')
        #print("Layers have changed!")
        #print(args)
        pass
        #self.c_att_helper.set_multiple_data(self.layers_data)
        #print(self.c_att_helper)
        #print(self.c_att_helper._data)
        #self.c_geo_metadata = self.c_att_helper._data[0].meta['geo']


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
    c_att = SelectionCallbackProperty(docstring='The attribute to display as a choropleth')
    
    colormap = SelectionCallbackProperty(docstring='Colormap used to display this layer')
    

    def __init__(self, layer=None, viewer_state=None, **kwargs): #Calling this init is fubar
            
        super(MapLayerState, self).__init__()
        self.c_att_helper = ComponentIDComboHelper(self, 'c_att', numeric=True)
        self.colormap_helper = ComboHelper(self, 'colormap')
        self.colormap_helper.choices = ['YlOrRd_04','viridis']
        self.colormap_helper.selection = 'viridis'
        self.add_callback('c_att', self._on_attribute_change)
        
        #self.cmap = 'viridis'#colormaps.members[0][1]
        #print(f'cmap = {self.cmap}')
        #self.add_callback('colormap', self._on_colormap_change) Do we need this, actually?
        
        #print(layer)
        self.layer = layer #This is critical!
        
        self._on_attribute_change()
        #self.c_att_helper.set_multiple_data([layer])
        #self.add_callback('layers', self._update_attribute)
        
        #if layer is not None:
        #    self._update_attribute()
        #self.c_geo_metadata = None
       # self.update_from_dict(kwargs)
        
        
        #self.ids = self.layer['ids']

    #def update(self, *args):
    #    print("In update function...")

    #def _update_attribute(self, *args):
    #    pass
        #if self.layer is not None:
        #    self.c_att_helper.set_multiple_data([self.layer])
        #    #self.c_att = self.layer.main_components[0]
        #    print(self.layer)
        #    print(self.c_att_helper._data)
        #    self.c_geo_metadata = self.c_att_helper._data[0].meta['geo']
            
    def _on_attribute_change(self, *args):
        #print("In _on_attribute_change")
        #print(self.layer)
        if self.layer is not None:
            self.c_att_helper.set_multiple_data([self.layer])
            self.c_geo_metadata = self.layer.meta['geo']
            #print(self.c_att_helper)
            #print(self.c_att)
            #print(self.c_geo_metadata)

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
    
