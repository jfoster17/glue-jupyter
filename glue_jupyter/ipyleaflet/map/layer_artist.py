"""
Next steps
- Should we use GeoPandas as our base data type? The main advantage is that it allows
us to have a single layer for points and shapes 
https://ipyleaflet.readthedocs.io/en/latest/api_reference/geodata.html
although I'm not sure how well it will play as a glue data type. Geopandas has some 
nice tools to handle geometry stuff, but how does it work for glue subsets and all that?
- If we do not do the above, we need to handle at least markers... perhaps as marker clusters? https://ipyleaflet.readthedocs.io/en/latest/api_reference/marker_cluster.html. Basic handling is probably pretty simple. The state class for a layer needs to 
know what kind of data we are plotting in this layer and then it can communicate this to the layer artist to handle
all the actual logic
- I broke subset creation/display in my re-org, and we need to bring this back in
- Layers currently cannot be hidden or re-ordered. Maybe work on this at the same time as doing sync with native controls?
- Viewer state can display zoom level (but this is not that great) and center
- When we add data to a layer it makes sense to try and center on it.

"""

import numpy as np
import bqplot
import json 

from glue.core import BaseData
from glue.core.exceptions import IncompatibleAttribute
from glue.viewers.common.layer_artist import LayerArtist
from glue.utils import color2hex

from ...link import link, dlink
from .state import MapLayerState, MapSubsetLayerState


from ipyleaflet.leaflet import LayerException, LayersControl
import ipyleaflet
from branca.colormap import linear


__all__ = ['IPyLeafletMapLayerArtist', 'IPyLeafletMapSubsetLayerArtist']


class IPyLeafletMapLayerArtist(LayerArtist):
    """
    ipyleaflet layers are slightly complicated
    
    Basically, there is an empty Map object that displays the basemap (controlled by Viewer State) and
    then there are layers for datasets/attributes that should be displayed on top of this
    """
    
    _layer_state_cls = MapLayerState

    def __init__(self, mapfigure, viewer_state, layer_state=None, layer=None):

        super(IPyLeafletMapLayerArtist, self).__init__(viewer_state,
                                                         layer_state=layer_state, layer=layer)
        #print("We are creating a layer artists...")
        #print(f'layer at time of LayerArtist init = {self.layer}')
        #print(f'layer_state at time of LayerArtist init = {layer_state}')
        #if self._viewer_state.map is None: #If we pass in a layer state
        #    self._viewer_state.map = map
        self.layer=layer
        #self.layer_state = layer_state
        self.mapfigure = mapfigure
        self.state.add_callback('color_att', self._on_attribute_change)
        self.state.add_callback('colormap', self._on_colormap_change)
        print(self.state)
        #choro_data = dict(zip(self.state.layer['ids'].tolist(), 
        #                        self.state.layer[self.state.color_att].tolist()))
        
        
        if self.state.layer_type == 'regions':
            #gdf = self.state.layer.gdf
            #choro_data = dict(zip([str(x) for x in self.state.layer['Pixel Axis 0 [x]']], 
            #                        self.state.layer[self.state.color_att].tolist()))
            self.layer_artist = ipyleaflet.Choropleth(#geo_data = json.loads(gdf.to_json()),
                                                      #choro_data = choro_data,
                                                      border_color='black',
                                                      style={'fillOpacity': 0.5, 'dashArray': '5, 5'},
                                                      hover_style={'fillOpacity': 0.95},)
            
            
            
          #  self.layer_artist = ipyleaflet.Choropleth(
          #                                              border_color='black',
        #                                            style={'fillOpacity': 0.5, 'dashArray': '5, 5'},
        #                                            hover_style={'fillOpacity': 0.95},)
                                    #geo_data=self.state.c_geo_metadata, #This should be in a layer, not in the viewer state...
                                    #choro_data=choro_data,
                                    #colormap=self.state.colormap,
                                    #border_color='black',
                                    #style={'fillOpacity': 0.5, 'dashArray': '5, 5'},
                                    #hover_style={'fillOpacity': 0.95},)
        
        self.mapfigure.add_layer(self.layer_artist)
        
        #self.colormap = 
        #link((self.state, 'colormap'), (self.mapfigure.layers[1], 'colormap')) #We need to keep track of the layer?
        
    def _on_colormap_change(self, value=None):
        #print(f'in _on_colormap_change')
        #print(f'state.colormap = {self.state.colormap}')
        #print(f'value = {value}')
        
        if self.state.colormap is None:
            return
        #self.state.colormap = value
        
        try:
            colormap = getattr(linear,self.state.colormap)
        except AttributeError:
            print("attribute error")
            colormap = linear.viridis #We need a default
        self.layer_artist.colormap = colormap
        self.redraw()
    
    def _on_attribute_change(self, value=None):
        if self.state.color_att is None:
            return
        
        if isinstance(self.layer, BaseData):
            layer = self.layer
        else:
            layer = self.layer.data
        
        print(f'color_att is {self.state.color_att}')
    
        #print(layer.get_kind(self.state.color_att))
        if layer.get_kind(self.state.color_att) != 'numerical':
            return
        
        #with delay_callback(self, '')
        if self.state.layer_type == 'regions':
        
            gdf = self.state.layer.gdf
            c = self.state.layer[self.state.color_att].tolist()
            choro_data = dict(zip([str(x) for x in self.state.layer['Pixel Axis 0 [x]']], c))
            #choro_data = dict(zip(self.state.layer['ids'].tolist(), c))
            #print(choro_data)
            #self.new_layer_artist = ipyleaflet.Choropleth(
            #                            geo_data=self.state.c_geo_metadata, 
            #                            choro_data=choro_data)
            self.layer_artist.value_min = np.min(c) #I think this does not work on categorical
            self.layer_artist.value_max = np.max(c)
            self.layer_artist.choro_data = choro_data
            self.layer_artist.geo_data = json.loads(gdf.to_json())
        
        self._on_colormap_change()
        #self.mapfigure.substitute_layer(self.layer_artist, self.new_layer_artist)
        #Update zoom and center?
        
        self.redraw()
        
    def clear(self):
        """Req: Remove the layer from viewer but allow it to be added back."""
        pass
    
    def remove(self):
        """Req: Permanently remove the layer from the viewer."""
        self.redraw()
    
    def update(self):
        """Req: Update appearance of the layer before redrawing. Called when a subset is changed."""
        self._on_attribute_change()
        self.redraw()
                
    def redraw(self):
        """Req: Re-render the plot."""
        pass
        
class IPyLeafletMapSubsetLayerArtist(LayerArtist):

    _layer_state_cls = MapSubsetLayerState

    def __init__(self, mapfigure, viewer_state, layer_state=None, layer=None):

        super(IPyLeafletMapSubsetLayerArtist, self).__init__(viewer_state,
                                                         layer_state=layer_state, layer=layer)
        self.mapfigure = mapfigure
        self.layer = layer
        self.layer_state = layer_state

