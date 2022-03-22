import numpy as np

from glue.core import BaseData, Subset, Data

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
from glue.core.data import Subset

from ..data import GeoRegionData

__all__ = ['MapViewerState', 'MapLayerState']


class MapViewerState(ViewerState):
    """
    A state class that manages the display of an ipyleaflet Map object:
    https://ipyleaflet.readthedocs.io/en/latest/api_reference/map.html
    which serves as the base for a MapViewer.
    
    lat_att : `~glue.core.component_id.ComponentID`
        The attribute to display as latitude. For choropleth-type data this is a special coordinate component.
    lon_att : `~glue.core.component_id.ComponentID`
        The attribute to display as longitude. For choropleth-type data this is a special coordinate component.
    
    """

    #center = CallbackProperty((40,-100),docstring='(Lon, Lat) at the center of the map')
    #zoom_level = CallbackProperty(4, docstring='Zoom level for the map')
    
    center = CallbackProperty((40, -100),docstring='(Lon, Lat) at the center of the map')
    zoom_level = CallbackProperty(4, docstring='Zoom level for the map')
    
    lon_att = SelectionCallbackProperty(default_index=1, docstring='The attribute to display as longitude')
    lat_att = SelectionCallbackProperty(default_index=0, docstring='The attribute to display as latitude')
    
    
    #basemap = CallbackProperty(basemaps.OpenStreetMap.Mapnik, docstring='Basemap to display')

    basemap = CallbackProperty(basemaps.Esri.WorldImagery)

    def __init__(self, **kwargs):

        super(MapViewerState, self).__init__()
        self.lat_att_helper = ComponentIDComboHelper(self, 'lat_att', 
                                                    numeric=True,
                                                    pixel_coord=True, 
                                                    world_coord=True, 
                                                    datetime=False, 
                                                    categorical=False)
        
        self.lon_att_helper = ComponentIDComboHelper(self, 'lon_att', 
                                                    numeric=True,
                                                    pixel_coord=True, 
                                                    world_coord=True, 
                                                    datetime=False, 
                                                    categorical=False)
        
        
        self.add_callback('layers', self._layers_changed)
        #self.add_callback('basemap', self._basemap_changed)
        #self.add_callback('basemap', self._basemap_changed)
        #print(f'layers={self.layers}')
        #print("Trying to update_from_dict...")
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
        self.lon_att_helper.set_multiple_data(self.layers_data)
        self.lat_att_helper.set_multiple_data(self.layers_data)


class MapLayerState(LayerState):
    """
    A state class that includes all the attributes for layers in a choropleth map.
    
    This should have attributes for:
    
    
    Parameters
    ----------
    color_att : `~glue.core.component_id.ComponentID`
        The values of this attribute determine the color of points or regions
    colormap : string
        A string (because colormap object themselves cannot travel through json) describing the colormap to 
        apply to color_att values.                
    visible : boolean
    
    color_steps (whether to turn a continuous variable into a stepped display) <-- less important
    """
    
    color_att = SelectionCallbackProperty(docstring='The attribute to display as a choropleth')
    
    colormap = SelectionCallbackProperty(docstring='Colormap used to display this layer')

    value_min = None
    value_max = None
    
    color = None

    name = "" #Name for display in the 
    def __init__(self, layer=None, viewer_state=None, **kwargs): #Calling this init is fubar
            
        super(MapLayerState, self).__init__()
        
        self.color_att_helper = ComponentIDComboHelper(self, 'color_att', numeric=True, categorical=False)
        
        #To be fancy we should determine the type of color_att and set the colormap choices based on that
        #Except ipyleaflet seems to have a limited set of colormaps -- and are any categorical?
        
        self.colormap_helper = ComboHelper(self, 'colormap')
        self.colormap_helper.choices = ['viridis','YlOrRd_04','PuBuGn_04','PuOr_04','Purples_09','YlGnBu_09','Blues_08','PuRd_06']
        self.colormap_helper.selection = 'viridis'
        #self.add_callback('color_att', self._on_attribute_change)
        
        self.add_callback('layer', self._layer_changed)

        #self.cmap = 'viridis'#colormaps.members[0][1]
        #print(f'cmap = {self.cmap}')
        #self.add_callback('colormap', self._on_colormap_change) Do we need this, actually?
        
        #print(layer)
        self.layer = layer #This is critical!
        # We distinguish between layers that plot regions and those that plot points
        # Glue can only plot region-type data for datasets stored as GeoData objects
        #if isinstance(self.layer, GeoRegionData):
        
        self._get_geom_type()
        #if self.viewer_state is not None:
        #    self._on_attribute_change()
        #self._on_attribute_change()
        #self.color_att_helper.set_multiple_data([layer])
        #self.add_callback('layers', self._update_attribute)
        
        #if layer is not None:
        #    self._update_attribute()
        #self.c_geo_metadata = None
       # self.update_from_dict(kwargs)
        if isinstance(layer, Subset):
            #print("Layer is a Subset")
            self.name = f"{self.name} {(self.layer.data.label)}"
        
        #self.ids = self.layer['ids']

    #def update(self, *args):
    #    print("In update function...")

    #def _update_attribute(self, *args):
    #    pass
        #if self.layer is not None:
        #    self.color_att_helper.set_multiple_data([self.layer])
        #    #self.color_att = self.layer.main_components[0]
        #    print(self.layer)
        #    print(self.color_att_helper._data)
        #    self.c_geo_metadata = self.color_att_helper._data[0].meta['geo']
        
    def _get_geom_type(self):
        if self.layer is not None:
            #print(f"layer type is: {type(self.layer)}")
            if isinstance(self.layer, Data):
                #print(f"geom_type is: {self.layer.geometry.geom_type}")
                try:
                    geom_type = self.layer.geometry.geom_type
                except AttributeError:
                    self.layer_type = 'points'
            else:
                #print(f"geom_type is: {self.layer.data.geometry.geom_type}")
                try:
                    geom_type = self.layer.data.geometry.geom_type
                except AttributeError:
                    self.layer_type = 'points'
                
            try:
                self.layer_type = 'regions'
                if (geom_type == 'Point').all():
                    self.layer_type = 'points'
                elif (geom_type == 'LineString').all():
                    self.layer_type = 'lines'
            except:
                self.layer_type = 'points'
            
        
    def _layer_changed(self, *args):
        if self.layer is not None:
            self.color_att_helper.set_multiple_data([self.layer])
            self.name = self.layer.label
            self._get_geom_type()
        
    def _on_attribute_change(self, *args):
        #print("In _on_attribute_change")
        #print(self.layer)
        if self.layer is not None:
            self.color_att_helper.set_multiple_data([self.layer])


    @property
    def viewer_state(self):
        return self._viewer_state

    @viewer_state.setter
    def viewer_state(self, viewer_state):
        self._viewer_state = viewer_state

#class MapSubsetLayerState(LayerState):
#    """
#    Currently this does not do anything
#    """
#    def __init__(self, *args, **kwargs):
#    #self.uuid = str(uuid.uuid4())
#        super(MapSubsetLayerState, self).__init__(*args, **kwargs)
    
