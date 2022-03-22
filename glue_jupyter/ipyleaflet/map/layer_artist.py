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
from .state import MapLayerState#, MapSubsetLayerState


from ..data import GeoRegionData, GeoPandasTranslator

from ipyleaflet.leaflet import LayerException, LayersControl, CircleMarker, Heatmap
import ipyleaflet
from branca.colormap import linear

from glue.utils import defer_draw, color2hex

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
        self._viewer_state = viewer_state
        #self.layer_state = layer_state
        self.mapfigure = mapfigure
        self.state.add_callback('color_att', self._on_attribute_change)
        self._viewer_state.add_callback('lat_att', self._on_attribute_change)
        self._viewer_state.add_callback('lon_att', self._on_attribute_change)
        self.state.add_callback('colormap', self._on_colormap_change)
        self._on_colormap_change()
        #print(self.state)
        
        if self.state.layer_type == 'regions':
            self.layer_artist = ipyleaflet.GeoJSON(data=self._fake_geo_json,
                                                   style={'fillOpacity': 0.5, 
                                                          'dashArray': '5, 5',
                                                          'weight':0.5},
                                                   hover_style={'fillOpacity': 0.95}
                                                )
            
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
        #print(f"self.colormap is now = {colormap}")
        self.colormap = colormap
        #self.layer_artist.colormap = colormap
        self.redraw()
    
    def _on_attribute_change(self, value=None):
        if self.state.color_att is None:
            return
        if isinstance(self.layer, BaseData):
            layer = self.layer
        else:
            layer = self.layer.data
        
            
        #with delay_callback(self, '')
        if self.state.layer_type == 'regions':
        
            # XX TODO XX -- We need to verify that we should be plotting this
            # i.e. that the lat/lon attributes are appropriately linked/set
            trans = GeoPandasTranslator()
            gdf = trans.to_object(self.layer)
            
            if isinstance(self.layer, Subset):
                new_layer_artist = ipyleaflet.GeoJSON(data=json.loads(gdf.to_json()),
                                                       style={'fillOpacity': 0.5, 
                                                              'dashArray': '0',
                                                              'color': self.get_layer_color(),
                                                              'weight':3},
                                                       hover_style={'fillOpacity': 0.95},
                                                    )
            else:
                c = np.array(layer[self.state.color_att].tolist())
                self.state.value_min = min(c)
                self.state.value_max = max(c)
                diff = self.state.value_max-self.state.value_min
                normalized_vals = (c-self.state.value_min)/diff
                mapping = dict(zip([str(x) for x in layer['Pixel Axis 0 [x]']], normalized_vals)) 
                
                def feature_color(feature):
                    feature_name = feature["id"]
                    return {'fillColor': self.colormap(mapping[feature_name])}
                
                new_layer_artist = ipyleaflet.GeoJSON(data=json.loads(gdf.to_json()),
                                               style={'fillOpacity': 0.5, 
                                                      'dashArray': '5, 5',
                                                      'weight':0.5},
                                               hover_style={'fillOpacity': 0.95},
                                               style_callback = feature_color,
                                            )
            new_layer_artist.name = self.state.name
            self.mapfigure.substitute_layer(self.layer_artist, new_layer_artist) #Swapping out the full layer seems to work better than updating attributes. Which is a bit unfortunate since it means we have more work to keep state attributes in sync
            self.layer_artist = new_layer_artist

        elif self.state.layer_type == 'points':
            #print(self)
            #There are two cases here, a GeoPandas object and a regular table with lat/lon
            #print("Inside layer_type == points")
            if isinstance(self.state.layer, GeoRegionData):
                pass
            else:
                #print("Clearing layers")
                #self.layer_artist.clear_layers()
                #print("Making marker list")
                lats = self.state.layer[self._viewer_state.lat_att]
                lons = self.state.layer[self._viewer_state.lon_att]
                in_color = self.get_layer_color()
                #print(in_color)
                try: #Ugly hack to make the starting points white. 
                    float(in_color)
                    in_color = 'white'
                except:
                    pass
                color = color2hex(in_color)
                #print(color)
                small = True
                if small:
                    markers = []
                    for lat,lon in zip(lats,lons):
                        markers.append(CircleMarker(location=(lat, lon),radius=2, stroke=False, fill_color=color, fill_opacity=0.7))#, weight=1, color='#FFFFFF'))
                    #print("Markers made")
                    self.layer_artist.layers = markers
                else:
                    #Fast, and generally good, but color options on heatmap are very limited
                    locs = list(zip(lats,lons))
                    new_layer_artist = Heatmap(locations=locs, radius=2, blur=1, min_opacity=0.5, gradient={0:color,1:color})
                    #print("Heatmap made")
                    self.mapfigure.substitute_layer(self.layer_artist, new_layer_artist)
                    self.layer_artist = new_layer_artist
                    
                #if isinstance(self.layer, Subset):
                #    print(f"Plotting a subset of {len(lats)}")
                    #print(markers)
                
            
        
        #self._on_colormap_change()
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
        #print(f"Update called for {self}")
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

