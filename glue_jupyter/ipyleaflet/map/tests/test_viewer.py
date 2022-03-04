import os
import json 

import pytest
import requests

import numpy as np
from numpy.testing import assert_allclose

import geopandas

from glue.core import Data
from glue.core.data_factories import pandas_read_table

from glue_jupyter.ipyleaflet.data import GeoRegionData, InvalidGeoData #TODO: Make this a more robust spec


DATA = os.path.join(os.path.dirname(__file__), 'data')


@pytest.fixture
def nycdata():
    path_to_data = geopandas.datasets.get_path("nybb")
    gdf = geopandas.read_file(path_to_data)
    nycdata = GeoRegionData(gdf,'nyc_boroughs')
    return nycdata

@pytest.fixture
def mapdata():
    with open(DATA+'/us-states.json','r') as f:
        geo_json_data = json.load(f)
    mapdata = pandas_read_table(DATA+'/test_map_data.csv')
    mapdata.meta['geo'] = geo_json_data
    return mapdata
    
def test_state_with_geopandas(mapapp, nycdata):
    mapapp.add_data(nycdata=nycdata)
    s = mapapp.map(data=nycdata)
    print(s.layers[0])
    assert s.layers[0].state.layer_type == 'regions'

def test_make_map_with_data(mapapp, mapdata):
    s = mapapp.map(data=mapdata)
    assert len(s.layers) == 1

def test_make_map_with_data_and_component(mapapp, mapdata):
    print(mapdata.components)
    s = mapapp.map(data=mapdata, color= 'Count_Person')
    assert len(s.layers) == 1

def test_colormap(mapapp, mapdata):
    purple_test_colors = np.array([(0.9882352941176471, 0.984313725490196, 0.9921568627450981, 1.0),
         (0.9372549019607843, 0.9294117647058824, 0.9607843137254902, 1.0),
         (0.8549019607843137, 0.8549019607843137, 0.9215686274509803, 1.0),
         (0.7372549019607844, 0.7411764705882353, 0.8627450980392157, 1.0),
         (0.6196078431372549, 0.6039215686274509, 0.7843137254901961, 1.0),
         (0.5019607843137255, 0.49019607843137253, 0.7294117647058823, 1.0),
         (0.41568627450980394, 0.3176470588235294, 0.6392156862745098, 1.0),
         (0.32941176470588235, 0.15294117647058825, 0.5607843137254902, 1.0),
         (0.24705882352941178, 0.0, 0.49019607843137253, 1.0)])
    s = mapapp.map(data=mapdata, color= 'Count_Person', colormap='Purples_09')
    assert s.layers[0].state.colormap == 'Purples_09'
    assert_allclose(s.mapfigure.layers[1].colormap.colors,purple_test_colors)

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
    