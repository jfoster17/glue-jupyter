import os
#from bqplot import PanZoom
#from bqplot.interacts import BrushSelector, BrushIntervalSelector
#from bqplot_image_gl.interacts import BrushEllipseSelector, MouseInteraction
from glue.core.subset import ElementSubsetState
from glue.core.edit_subset_mode import AndMode

from glue.core.roi import RectangularROI, RangeROI, CircularROI, EllipticalROI, PolygonalROI
from glue.core.subset import RoiSubsetState, MultiOrState
from glue.config import viewer_tool
from glue.viewers.common.tool import Tool, CheckableTool
from glue.core.exceptions import IncompatibleAttribute

import numpy as np

from ipywidgets import CallbackDispatcher
from traitlets import Instance

from ipyleaflet import Rectangle
import time
__all__ = []

ICON_WIDTH = 20
INTERACT_COLOR = '#cbcbcb'

ICONS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'icons')


class InteractCheckableTool(CheckableTool):

    def __init__(self, viewer):
        self.viewer = viewer

    def activate(self):

        # Disable any active tool in other viewers
        for viewer in self.viewer.session.application.viewers:
            if viewer is not self.viewer:
                viewer.toolbar.active_tool = None

        self.viewer._mouse_interact.next = self.interact

    def deactivate(self):
        self.viewer._mouse_interact.next = None


class IpyLeafletSelectionTool(InteractCheckableTool):

    def activate(self):
        # Jumps back to "create new" if that setting is active
        if self.viewer.session.application.get_setting('new_subset_on_selection_tool_change'):
            self.viewer.session.edit_subset_mode.edit_subset = None
        super().activate()

@viewer_tool
class PointSelect(IpyLeafletSelectionTool):

    icon = 'glue_crosshair'
    tool_id = 'ipyleaflet:pointselect'
    action_text = 'Select regions'
    tool_tip = 'Select regions'
    status_tip = 'Click to select regions to add to a subset'
    shortcut = 'D'

    def __init__(self, viewer):
        super(PointSelect, self).__init__(viewer)
        self.list_of_region_ids = []
        #print("PointSelect created...")

    def activate(self):
        """
        Capture point-select clicks. This is to select regions... 
        
        TODO:
        Currently we have this operate only on the bottom layer
        (bottom layer is easiest because subset layers get put on top)
        
        Currently the on_click function gets called twice on each
        actual click. I need to figure out the click model. 
        """
        print("PointSelect activated...")
        
        
        def on_click(event, feature, **kwargs):
            print("On click called...")
            self.list_of_region_ids = []
            #print(feature)
            feature_id = feature['id'] #This is the name of features in our geodata
            #print(feature_id)
            # List of region_ids should start with the current subset (how to get this?)
            active_subset = self.viewer.toolbar_active_subset.selected
            if active_subset:
                print(f'activate_subset is: {active_subset}')
                self.list_of_region_ids = list(self.viewer.session.data_collection.subset_groups[active_subset[0]].subsets[0].to_mask().nonzero()[0])
            else:
                print("No active_subset")
                print(f'active_subset is: {active_subset}')
            self.list_of_region_ids.append(int(feature_id))
            self.list_of_region_ids =  list(set(self.list_of_region_ids))
            print(f"List of region ids to draw... {self.list_of_region_ids}")
            #import pdb; pdb.set_trace()
            try:
                #inds = [key for key, val in enumerate(self.viewer.state.layers_data[0]['ids']) if val in self.list_of_region_ids]
                int_inds = [int(x) for x in self.list_of_region_ids]
                # Assume we are trying to interact with the top layer
                target_layer = self.viewer.layers[0].layer #This is just the bottom layer -- we need to think about how to get this properly
                #print(target_layer)
                # Get Geo geometries for these indices
                try:
                    region_geometries = target_layer.geometry[int_inds].explode(index_parts=False) #Expand multi-polygons to single polygons
                except AttributeError: #If there is not a geometry column defined, then what do we do?
                    pass
                    
                subset_states = []
                for region in region_geometries:
                    lons,lats = region.boundary.coords.xy
                    roi = PolygonalROI(vx=lons, vy =lats)
                    subset_state = RoiSubsetState(xatt=target_layer._centroid_component_ids[1],
                                                  yatt=target_layer._centroid_component_ids[0],
                                                  roi=roi)
                    subset_states.append(subset_state)
                #union = region_geometries.unary_union
                # Do a unary_union on these geometries
                # Convert to a glue-like ROI (bounds?). Could be a performance limitation?
                # subset_state = RoiSubsetState(xatt = centroid_lon, y_att=centroid_lat, roi=roi_from_above)
                # We need to have centroid_lon and centroid_lat well defined...
                final_subset_state = MultiOrState(subset_states)
                self.viewer.apply_subset_state(final_subset_state, override_mode=None) #What does override_mode do?
                print(f"Indices applied... {int_inds}")
                #print(final_subset_state)
            except IncompatibleAttribute:
                print("Got an IncompatibleAttribute")
            #print(inds)
            #print(subset_state.to_mask(self.viewer.state.layers_data[0]))
            #print(feature['id'])
        #Get current? layer geo_json object
        #print(self.viewer.layers[0])
        #layer_artist._click_callbacks = CallbackDispatcher() 
        layer_artist = self.viewer.layers[0].layer_artist
        layer_artist.on_click(on_click)
        #for layer in self.viewer.layers: #Perhaps we do not want to do this for every layer, but only the top one? 
        #That could become confusing in the case where we have multiple non-overlapping layers...
        #    print(f"Adding on_click to {layer}")
        #    layer_artist = layer.layer_artist
        #    layer_artist.on_click(on_click)

    def deactivate(self):
        layer_artist = self.viewer.layers[0].layer_artist
        layer_artist._click_callbacks = CallbackDispatcher() #This removes all on_click callbacks, but seems to work
        self.list_of_region_ids = [] #We need to trigger this when we switch modes too (to do a new region)
        #print(f"List of Region IDs: {list(set(self.list_of_region_ids))}") #For some reason this adds all regions twice

    def close(self):
        pass

@viewer_tool
class RectangleSelect(IpyLeafletSelectionTool):

    icon = 'glue_square'
    tool_id = 'ipyleaflet:rectangleselect'
    action_text = 'Rectangular ROI'
    tool_tip = 'Hold down SHIFT and drag to define a rectangular region of interest'
    status_tip = 'Define a rectangular region of interest'
    shortcut = 'D'

    def __init__(self, viewer):
        super(RectangleSelect, self).__init__(viewer)
        self.start_coords = None
        self.end_coords = None

    def activate(self):
        """
        This gets the information we want, but we need to disable dragging and we need to 
        draw a rectangle on the map. The DrawControl stuff in ipyleaflet does all this
        
        """
        #self.viewer.mapfigure.dragging = False #This SHOULD work, but it does not
        #https://github.com/jupyter-widgets/ipyleaflet/issues/711#issuecomment-704311279
        #Until then, we have to hold down SHIFT
        def map_interaction(**kwargs):
            #print(kwargs)
            if kwargs['type'] == 'mousedown':
                print(f'mousedown {kwargs["coordinates"]}')
                self.start_coords = kwargs['coordinates']
                self.rect = Rectangle(bounds=(self.start_coords, kwargs['coordinates']),
                                        weight=1, fill_opacity=0, dash_array= '5, 5', color='gray')
                self.viewer.mapfigure.add_layer(self.rect)
            elif kwargs['type'] == 'mouseup' and self.start_coords:
                print(f'mouseup {kwargs["coordinates"]}')
                self.end_coords = kwargs['coordinates']
                
                xmin = self.end_coords[1]
                xmax = self.start_coords[1]
                ymin = self.end_coords[0]
                ymax = self.start_coords[0]
                xmin, xmax = sorted((xmin, xmax))
                ymin, ymax = sorted((ymin, ymax))
                roi = RectangularROI(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
                subset_state = RoiSubsetState(xatt=self.viewer.state.lon_att,
                                              yatt=self.viewer.state.lat_att,
                                              roi=roi)
                self.viewer.apply_subset_state(subset_state, override_mode=None)
                
                self.start_coords = None
                time.sleep(0.1)
                self.viewer.mapfigure.remove_layer(self.rect)
            elif kwargs['type'] == 'mousemove' and self.start_coords:
                new_rect = Rectangle(bounds=(self.start_coords, kwargs['coordinates']),
                                        weight=1, fill_opacity=0.1, dash_array= '5, 5', color='gray', fill_color='gray')
                # This is nice because it colors regions as we go, but it gets VERY slow with larger rectangles
                # Need to heavily optimize or something.
                
                #self.end_coords = kwargs['coordinates']
                #xmin = self.end_coords[1]
                #xmax = self.start_coords[1]
                #ymin = self.end_coords[0]
                #ymax = self.start_coords[0]
                #xmin, xmax = sorted((xmin, xmax))
                #ymin, ymax = sorted((ymin, ymax))
                
                #roi = RectangularROI(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
                #subset_state = RoiSubsetState(xatt=self.viewer.state.lon_att,
                #                              yatt=self.viewer.state.lat_att,
                #                              roi=roi)
                #This is slow IFF we cover a significant NUMBER of points
                #Why? It is not the size of the region covered, and it does not seem to matter
                #whether we have points or regions. 
                #It is possible that 
                #self.viewer.apply_subset_state(subset_state, override_mode=None) 
                
                self.viewer.mapfigure.substitute_layer(self.rect,new_rect) 
                self.rect = new_rect
            #print(kwargs)
        self.viewer.mapfigure.on_interaction(map_interaction)

    def deactivate(self):
        self.viewer.mapfigure._interaction_callbacks = CallbackDispatcher()
        #self.viewer.mapfigure.dragging = True
        
        
    def close(self):
        pass


@viewer_tool
class HomeTool(Tool):

    tool_id = 'ipyleaflet:home'
    icon = 'glue_home'
    action_text = 'Home'
    tool_tip = 'Reset original zoom'

    def activate(self):
        self.viewer.state.reset_limits()
