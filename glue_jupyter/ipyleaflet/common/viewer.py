import bqplot

from glue.core.subset import roi_to_subset_state
from glue.core.command import ApplySubsetState

from bqplot_image_gl.interacts import MouseInteraction, keyboard_events, mouse_events

from echo.callback_container import CallbackContainer

from ...view import IPyWidgetView
from ...link import dlink, on_change
from ...utils import float_or_none, debounced, get_ioloop


import ipyleaflet
__all__ = ['IpyLeafletBaseView']


class IpyLeafletBaseView(IPyWidgetView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    is2d = True
    _default_mouse_mode_cls = None

    def __init__(self, session, state=None):

        self.mapfigure = ipyleaflet.Map(center=(40, -100), zoom=4)

        # Set up a MouseInteraction instance here tied to the figure. In the
        # tools we then chain this with any other active interact so that we can
        # always listen for certain events. This allows us to then have e.g.
        # mouse-over coordinates regardless of whether tools are active or not.
        self._event_callbacks = CallbackContainer()
        self._events_for_callback = {}

        #self.scale_x = 0 #These are used throughout the toolbar things
        #self.scale_y = 0 
        super(IpyLeafletBaseView, self).__init__(session, state=state)

        self.create_layout()

    def get_layer_artist(self, cls, layer=None, layer_state=None):
        return cls(self.mapfigure, self.state, layer=layer, layer_state=layer_state)

    def add_event_callback(self, callback, events=None):
        """
        Add a callback function for mouse and keyboard events when the mouse is over the figure.

        Parameters
        ----------
        callback : func
            The callback function. This should take a single argument which is a
            dictionary containing the event details. One of the keys of the
            dictionary is ``event`` which is a string that describes the event
            (see the ``events`` parameter for possible strings). The rest of the
            dictionary depends on the specific event triggered.
        events : list, optional
            The list of events to listen for. The following events are available:

            * ``'click'``
            * ``'dblclick'``
            * ``'mouseenter'``
            * ``'mouseleave'``
            * ``'contextmenu'``
            * ``'mousemove'``
            * ``'keydown'``
            * ``'keyup'``

            If this parameter is not passed, all events will be listened for.
        """

        if events is None:
            events = keyboard_events + mouse_events

        self._events_for_callback[callback] = set(events)

        self._event_callbacks.append(callback)
        self._update_interact_events()

    def remove_event_callback(self, callback):
        """
        Remove a callback function for mouse and keyboard events.
        """
        self._events_for_callback.pop(callback)
        self._event_callbacks.remove(callback)
        self._update_interact_events()

    def _update_interact_events(self):
        events = set()
        for individual_events in self._events_for_callback.values():
            events |= individual_events
        events = sorted(events)
        self._mouse_interact.events = sorted(events)

    def _on_mouse_interaction(self, interaction, data, buffers):
        for callback in self._event_callbacks:
            callback(data)

    @property
    def figure_widget(self):
        return self.mapfigure


    def redraw(self):
        pass
