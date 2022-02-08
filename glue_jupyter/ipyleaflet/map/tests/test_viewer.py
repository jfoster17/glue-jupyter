import os
import json 

import pytest
import requests

import numpy as np
from numpy.testing import assert_allclose

from glue.core import Data
from glue.core.data_factories import pandas_read_table

DATA = os.path.join(os.path.dirname(__file__), 'data')


@pytest.fixture
def mapdata():
    with open(DATA+'/us-states.json','r') as f:
        geo_json_data = json.load(f)
    mapdata = pandas_read_table(DATA+'/test_map_data.csv')
    mapdata.meta['geo'] = geo_json_data
    return mapdata
    
def test_make_map_with_data(mapapp, mapdata):
    s = mapapp.map(data=mapdata)
    assert len(s.layers) == 1

def test_make_map_with_data_and_component(mapapp, mapdata):
    s = mapapp.map(data=mapdata, c= 'Count_Person')
    assert len(s.layers) == 1


def test_empty_map_set_init_and_check_sync(mapapp):
    
    initial_zoom_level = 5
    initial_center = (-40,100)
    
    s = mapapp.map(data=None, zoom_level=initial_zoom_level, center=initial_center)
    assert s.state.zoom_level == initial_zoom_level
    assert s.state.center == initial_center
    
    new_zoom_level = 2
    
    s.state.zoom_level = new_zoom_level
    assert s.mapfigure.zoom == s.state.zoom_level
    assert list(s.mapfigure.center) == list(s.state.center)


def test_empty_map(mapapp):
    s = mapapp.map(data=None)
    assert len(s.layers) == 0


def test_adding_data_to_empty_map(mapapp, mapdata):
    s = mapapp.map(data=None)
    s.add_data(mapdata)
    assert len(s.layers) == 1
    