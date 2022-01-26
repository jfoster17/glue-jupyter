import numpy as np
import bqplot

from glue.core.exceptions import IncompatibleAttribute
from glue.viewers.common.layer_artist import LayerArtist
from glue.utils import color2hex

from ...link import link, dlink
from .state import MapLayerState

import ipyleaflet
from branca.colormap import linear


__all__ = ['IPyLeafletMapLayerArtist']


class IPyLeafletMapLayerArtist(LayerArtist):

    _layer_state_cls = MapLayerState

    def __init__(self, map, viewer_state, layer_state=None, layer=None):

        super(IPyLeafletMapLayerArtist, self).__init__(viewer_state,
                                                         layer_state=layer_state, layer=layer)

        print(self.state.layer[self._viewer_state.c_att])
        #print(self.state.layer.layer)
        choro_data = dict(zip(self.state.layer['ids'].tolist(), 
                            self.state.layer[self._viewer_state.c_att].tolist()))
        print(choro_data)
        self.layer_artist = ipyleaflet.Choropleth(
                                    geo_data=self._viewer_state.c_geo_metadata, #This should be in a layer, not in the viewer state...
                                    choro_data=choro_data,
                                    colormap=linear.YlOrRd_04,
                                    border_color='black',
                                    style={'fillOpacity': 0.8, 'dashArray': '5, 5'})
        
        self.map = map
        self.map.add_layer(self.layer_artist)
       #self.view = view

    def clear(self):
        pass

    def remove(self):
        pass

    def _on_attribute_change(self, value=None):
    
        if self._viewer_state.c_att is None:
            return

        c = self.state.layer[self._viewer_state.c_att]
        import pdb; pdb.set_trace()
        self.artist.set_data(x, y)

        #Recenter map here?
        #self.axes.set_xlim(np.nanmin(x), np.nanmax(x))
        #self.axes.set_ylim(np.nanmin(y), np.nanmax(y))

        self.redraw()


    def _update_visual_attributes(self):

        if not self.enabled:
            return
        # TODO: set visual attrs
        self.redraw()

    def update(self):
       # self.state.reset_cache()
        self.redraw()
