import numpy as np
import pytest
import geopandas
from geopandas.testing import assert_geodataframe_equal
from glue.core.subset import ElementSubsetState

from glue.core.data import Data

from ..data import GeoRegionData, InvalidGeoData


@pytest.fixture
def nycbb():
    path_to_data = geopandas.datasets.get_path("nybb")
    gdf = geopandas.read_file(path_to_data)
    nyc_boroughs = GeoRegionData(gdf,'nyc_boroughs')
    print(nyc_boroughs)
    assert nyc_boroughs.meta['crs'] == gdf.crs
    return nyc_boroughs

@pytest.fixture
def gdf():
    path_to_data = geopandas.datasets.get_path("nybb")
    gdf = geopandas.read_file(path_to_data)
    return gdf

@pytest.fixture
def earthdata():
    path_to_data = geopandas.datasets.get_path("naturalearth_lowres")
    gdf = geopandas.read_file(path_to_data)
    earthdata = GeoRegionData(gdf,'countries')
    return earthdata


def test_creation(nycbb):
    
    assert nycbb.shape == (5,)
    assert len(nycbb.components) == 8
    
def test_error_on_bad_creation():
    not_geo_data = np.array(([1,2,3],[3,4,5]))
    with pytest.raises(InvalidGeoData):
        glue_data = GeoRegionData(not_geo_data,'bad')
    
def test_define_on_init():
    ind = np.array([0, 1])
    state = ElementSubsetState(indices=ind)
    np.testing.assert_array_equal(ind, state._indices)
        

def test_get_mask_element_subset_state(nycbb, gdf):
    subset = nycbb.new_subset()
    subset.subset_state = ElementSubsetState(indices=[1, 2])
    np.testing.assert_array_equal(nycbb.subsets[0].to_mask(),[0,1,1,0,0])
    auto_subset = nycbb.get_subset_object(subset_id=0,cls=geopandas.geodataframe.GeoDataFrame)
    assert isinstance(auto_subset, geopandas.GeoDataFrame)
    hand_subset = gdf.iloc[[1,2]].reset_index(drop=True)
    assert(len(auto_subset) == len(hand_subset))
    #print(auto_subset)
    #print(hand_subset)
    assert_geodataframe_equal(auto_subset,hand_subset)
    #assert hand_subset == 