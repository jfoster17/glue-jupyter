import os
from bqplot import PanZoom
from bqplot.interacts import BrushSelector, BrushIntervalSelector
from bqplot_image_gl.interacts import BrushEllipseSelector, MouseInteraction
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

        #self.viewer._mouse_interact.next = self.interact

    def deactivate(self):
        pass
        #self.viewer._mouse_interact.next = None



@viewer_tool
class HomeTool(Tool):

    tool_id = 'bqplot:home'
    icon = 'glue_home'
    action_text = 'Home'
    tool_tip = 'Reset original zoom'

    def activate(self):
        self.viewer.state.reset_limits()
