import numpy as np
import bqplot

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

    _layer_state_cls = MapLayerState

    def __init__(self, map, viewer_state, layer_state=None, layer=None):

        super(IPyLeafletMapLayerArtist, self).__init__(viewer_state,
                                                         layer_state=layer_state, layer=layer)

        #print(self.state.layer[self._viewer_state.c_att])
        #print(self.state.layer)
        choro_data = dict(zip(self.state.layer['ids'].tolist(), 
                            self.state.layer[self._viewer_state.c_att].tolist()))
        #print(choro_data)
        self.layer_artist = ipyleaflet.Choropleth(
                                    geo_data=self._viewer_state.c_geo_metadata, #This should be in a layer, not in the viewer state...
                                    choro_data=choro_data,
                                    colormap=linear.YlOrRd_04,
                                    border_color='black',
                                    style={'fillOpacity': 0.5, 'dashArray': '5, 5'},
                                    hover_style={'fillOpacity': 0.95},)
                                    #style_callback=subset_border)
        self.layer_artist.name = str(self._viewer_state.c_att) #We will have to sync this
        self._viewer_state.add_callback('c_att', self._on_attribute_change)
        self.map = map
        self.map.add_layer(self.layer_artist)
        control = LayersControl(position='bottomleft')
        map.add_control(control)
        
       #self.view = view

    #def subset_border()

    def clear(self):
        pass

    def remove(self):
        pass

    def _on_attribute_change(self, value=None):
    
        if self._viewer_state.c_att is None:
            return

        c = self.state.layer[self._viewer_state.c_att].tolist()
        choro_data = dict(zip(self.layer['ids'].tolist(), c))
        
        self.layer_artist.value_min = min(c)
        self.layer_artist.value_max = max(c)
        self.layer_artist.choro_data = choro_data
        self.redraw()


    def _update_visual_attributes(self):

        if not self.enabled:
            return
        # TODO: set visual attrs
        self.redraw()

    def update(self):
       # self.state.reset_cache()
        self.redraw()
        
    def redraw(self):
        #print("In layer artist redraw")
        if len(self.layer['ids'].tolist()) == 0:
            pass
        else:
            try:
                if len(self.map.layers) > 1:
                    old_layer = self.map.layers[-1]
                self.map.substitute_layer(old_layer, self.layer_artist)
            except LayerException:
                try: 
                    self.map.add_layer(self.layer_artist)
                except LayerException:
                    pass
            #if len(self.map.layers) > 1:
            #    old_layer = self.map.layers[-1]
            #    self.map.substitute_layer(old_layer, self.layer_artist)
            #else:
            #    self.map.add_layer(self.layer_artist)
                
class IPyLeafletMapSubsetLayerArtist(LayerArtist):

    _layer_state_cls = MapSubsetLayerState

    def __init__(self, map, viewer_state, layer_state=None, layer=None):

        super(IPyLeafletMapSubsetLayerArtist, self).__init__(viewer_state,
                                                         layer_state=layer_state, layer=layer)
        self.map = map
        self.layer = layer
        self.layer_state = layer_state
        #dlink((self.state, 'color'), (self.scatter, 'colors') #Can we link the color to Geo
        
    def redraw(self):
        """
        This is dumb -- it creates a new map layer each time we have to redraw
        
        What we need to do is manage the subset data in the state layer and just
        draw the most recent one here
        """
        if len(self.layer['ids'].tolist()) == 0:
            pass
        else:
            #print(f"subset layer: {self.layer}")
            #import pdb; pdb.set_trace()
            #print(f"subset ids: {self.layer['ids'].tolist()}")
            choro_data = dict(zip(self.layer['ids'].tolist(), 
                                self.layer[self._viewer_state.c_att].tolist()))
            features_in_subset = self.layer['ids'].tolist()
            #print(f"subset choro_data: {choro_data}")
            geo_json_data = self._viewer_state.c_geo_metadata #This should be in a layer, not in the viewer state...
            #print(len(geo_json_data['features']))
            new_features = []
            for feature in geo_json_data['features']:
                if feature['id'] in features_in_subset:
                    new_features.append(feature)
            subset_json = geo_json_data.copy()
            subset_json['features'] = new_features
            #print(self.layer.style.color)
            self.subset_artist = ipyleaflet.GeoJSON(
                                        data=subset_json,
                                        style={'fillOpacity': 0.5, 'color':self.layer.style.color},
                                        )
                                        #style_callback=subset_border)
            if len(self.map.layers) > 2:
                old_subset_map = self.map.layers[-1]
                self.map.substitute_layer(old_subset_map, self.subset_artist)
            else:
                self.map.add_layer(self.subset_artist)
        
        

    def clear(self):
        pass

    def remove(self):
        pass

    def _on_attribute_change(self, value=None):
    
        if self._viewer_state.c_att is None:
            return

        c = self.state.layer[self._viewer_state.c_att]

        self.redraw()


    def _update_visual_attributes(self):

        if not self.enabled:
            return
        # TODO: set visual attrs
        self.redraw()

    def update(self):
       # self.state.reset_cache()
        self.redraw()