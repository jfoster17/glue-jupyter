import os
#from bqplot import PanZoom
#from bqplot.interacts import BrushSelector, BrushIntervalSelector
#from bqplot_image_gl.interacts import BrushEllipseSelector, MouseInteraction
from glue.core.subset import ElementSubsetState
from glue.core.edit_subset_mode import AndMode

from glue.core.roi import RectangularROI, RangeROI, CircularROI, EllipticalROI, PolygonalROI
from glue.core.subset import RoiSubsetState
from glue.config import viewer_tool
from glue.viewers.common.tool import Tool, CheckableTool
import numpy as np

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
class PointSelect(CheckableTool):

    icon = 'glue_crosshair'
    tool_id = 'ipyleaflet:pointselect'
    action_text = 'Select regions'
    tool_tip = 'Select regions'
    status_tip = 'Click to select regions to add to a subset'
    shortcut = 'D'

    def __init__(self, viewer):
        super(PointSelect, self).__init__(viewer)
        self.list_of_region_ids = []
        

    def activate(self):
        """
        Capture on click stuff
        """
        def on_click(event, feature, **kwargs):
            """On click should immediately add this to a subset.
            The layer artist can then worry about the coloring."""
            feature_id = feature['id'] #This is the name of features in our geodata
            #print(feature_id)
            
            self.list_of_region_ids.append(feature_id)
            self.list_of_region_ids = list(set(self.list_of_region_ids))
            
            #import pdb; pdb.set_trace()
            inds = [key for key, val in enumerate(self.viewer.state.layers_data[0]['ids']) if val in self.list_of_region_ids]
            #print(inds)
            subset_state = ElementSubsetState(indices=inds)
            #print(subset_state.to_mask(self.viewer.state.layers_data[0]))
            self.viewer.apply_subset_state(subset_state, override_mode=None) #What does override_mode do?
            #print(feature['id'])
        #Get current? layer geo_json object
        #print(self.viewer.layers[0])
        geo_json = self.viewer.layers[0].layer_artist
        geo_json.on_click(on_click)

    def deactivate(self):
        pass
        #print(f"List of Region IDs: {list(set(self.list_of_region_ids))}") #For some reason this adds all regions twice

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
