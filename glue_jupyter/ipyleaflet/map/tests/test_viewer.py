import os
import pytest
import numpy as np
from numpy.testing import assert_allclose
from glue.core import Data
from glue.core.data_factories import pandas_read_table

DATA = os.path.join(os.path.dirname(__file__), 'data')


@pytest.fixture
def mapdata():
    return pandas_read_table(DATA+'/test_map_data.csv')
    

def test_empty_map(mapapp):
    s = mapapp.map(data=None)
    assert len(s.layers) == 0

def test_adding_data_to_empty_map(mapapp, mapdata):
    s = mapapp.map(data=None)
    s.add_data(mapdata)
    assert len(s.layers) == 1
    