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
from glue.core.data import Subset

from glue.core.exceptions import IncompatibleAttribute
from glue.viewers.common.layer_artist import LayerArtist
from glue.utils import color2hex

from ...link import link, dlink
from .state import MapLayerState, MapSubsetLayerState


from ..data import GeoRegionData, GeoPandasTranslator

from ipyleaflet.leaflet import LayerException, LayersControl, CircleMarker
import ipyleaflet
from branca.colormap import linear


__all__ = ['IPyLeafletMapLayerArtist']#, 'IPyLeafletMapSubsetLayerArtist']


class IPyLeafletMapLayerArtist(LayerArtist):
    """
    ipyleaflet layers are slightly complicated
    
    Basically, there is an empty Map object that displays the basemap (controlled by Viewer State) and
    then there are layers for datasets/attributes that should be displayed on top of this
    """
    
    _layer_state_cls = MapLayerState
    
    _fake_geo_json = {"type":"FeatureCollection",
      "features":[{
          "type":"Feature",
          "id":"DE",
          "properties":{"name":"Delaware"},
          "geometry":{
              "type":"Polygon",
              "coordinates":[[[-75.414089,39.804456],[-75.507197,39.683964],[-75.611259,39.61824],[-75.589352,39.459409],[-75.441474,39.311532],[-75.403136,39.065069],[-75.189535,38.807653],[-75.09095,38.796699],[-75.047134,38.451652],[-75.693413,38.462606],[-75.786521,39.722302],[-75.616736,39.831841],[-75.414089,39.804456]]]
              }
       }]
      }
    

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
        self.state.add_callback('lat_att', self._on_attribute_change)
        self.state.add_callback('lon_att', self._on_attribute_change)
        self.state.add_callback('colormap', self._on_colormap_change)
        self._on_colormap_change()
        print(self.state)
        
        #choro_data = dict(zip(self.state.layer['ids'].tolist(), 
        #                        self.state.layer[self.state.color_att].tolist()))
        
        init_color = self.get_layer_color()
        try:
            float(init_color)
        except ValueError:
            init_color='black'
        if self.state.layer_type == 'regions':
            self.layer_artist = ipyleaflet.GeoJSON(data=self._fake_geo_json,
                                                   style={'fillOpacity': 0.5, 
                                                          'dashArray': '5, 5',
                                                          'color': init_color,
                                                          'weight':0.5},
                                                   hover_style={'fillOpacity': 0.95}
                                                )
            if isinstance(self.layer, Subset):
                #pass
                print(f"Layer color is: {self.get_layer_color()}")
                self.layer_artist.style['color'] = self.get_layer_color()
                self.layer_artist.style['weight'] = 1
                self.layer_artist.style['opacity'] = 1
                self.layer_artist.style['dashArray'] = '0'
                self.layer_artist.style['fillOpacity'] = 0
                print("Full layer_artist style")
                print(self.layer_artist.style)
                #self.layer_artist.border_color= self.layer.subset_state.style.color
                #self.layer_artist.style.weight= 1
            #data = self.layer.data
            #subset_state = self.layer.subset_state
            
        else:
            self.layer_artist = ipyleaflet.LayerGroup()
        self.layer_artist.name = self.state.name
        #Not all layers have a way to make them visible/invisible. 
        #And the built-in control does something complicated. 
        #Hard to keep these in sync!
        #link((self.state,'visible'), (self.layer_artist,'visible'))
        self.mapfigure.add_layer(self.layer_artist)
        
        #self.colormap = 
        #link((self.state, 'colormap'), (self.mapfigure.layers[1], 'colormap')) #We need to keep track of the layer?
        
    def _on_colormap_change(self, value=None):
        """
        self.state.colormap is a string
        self.colormap is the actual colormap object `branca.colormap.LinearColormap` object
        """
        
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
        print(f"self.colormap is now = {colormap}")
        self.colormap = colormap
        #self.layer_artist.colormap = colormap
        self.redraw()
    
    def _on_attribute_change(self, value=None):
        #if self.state.color_att is None:
        #    return
        if self.state.color_att is None:
            return
        if isinstance(self.layer, BaseData):
            layer = self.layer
        else:
            layer = self.layer.data
        
        print(f'color_att is {self.state.color_att}')
    
        #print(layer.get_kind(self.state.color_att))
        #if layer.get_kind(self.state.color_att) != 'numerical':
        #    return
        
        #with delay_callback(self, '')
        if self.state.layer_type == 'regions':
        
            #c = np.array(self.state.layer[self.state.color_att].tolist())
            #print(c)
            
            #What is diff between self.layer and self.state.layer? Probably nothing?
            trans = GeoPandasTranslator()
            gdf = trans.to_object(self.layer)
            
            self.layer_artist.data = json.loads(gdf.to_json())
            c = np.array(layer[self.state.color_att].tolist()) #First subset crashes unless we do this. Check for empty list?
            #if self.state.value_min is None:
            self.state.value_min = min(c)
            #if self.state.value_max is None:
            self.state.value_max = max(c)
            diff = self.state.value_max-self.state.value_min
            normalized_vals = (c-self.state.value_min)/diff
            #mapping =
            #c = self.state.layer[self.state.color_att].tolist()
            mapping = dict(zip([str(x) for x in layer['Pixel Axis 0 [x]']], normalized_vals)) #layer should probably go back to self.state.layer
            
            def feature_color(feature):
                feature_name = feature["id"]
                if isinstance(self.layer, Subset):
                    style_dict = {
                        #'fillColor': self.colormap(mapping[feature_name]),
                        'fillOpacity': 0,
                        'weight': 2,
                        'color': self.get_layer_color(),
                    }
                    print(f"style_dict inside of feature_color: {style_dict}")
                    return style_dict
                    
                else:
                    style_dict = {
                        'fillColor': self.colormap(mapping[feature_name]),
                    }
                    print(f"style_dict inside of feature_color: {style_dict}")
                    return style_dict
            #self.layer_artist.data = gdf
            #self.layer_artist.value_min = np.min(c) #I think this does not work on categorical
            #self.layer_artist.value_max = np.max(c)
            #self.layer_artist.choro_data = choro_data
            
            self.layer_artist.style_callback=feature_color

        elif self.state.layer_type == 'points':
            #There are two cases here, a GeoPandas object and a regular table with lat/lon
            if isinstance(self.state.layer, GeoRegionData):
                pass
            else:
                print("Making marker list")
                lats = self.state.layer[self.state.lat_att].tolist()
                lons = self.state.layer[self.state.lon_att].tolist()
                markers = []
                for lat,lon in zip(lats,lons):
                    markers.append(CircleMarker(location=(lat, lon),radius=5, stroke=False))
                self.layer_artist.layers=markers
        
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
        
#class IPyLeafletMapSubsetLayerArtist(LayerArtist):#
#
#    _layer_state_cls = MapSubsetLayerState
#
#    def __init__(self, mapfigure, viewer_state, layer_state=None, layer=None):
#
#        super(IPyLeafletMapSubsetLayerArtist, self).__init__(viewer_state,
#                                                         layer_state=layer_state, layer=layer)
#        self.mapfigure = mapfigure
#        self.layer = layer
#        self.layer_state = layer_state

