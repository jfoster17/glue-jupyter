import numpy as np
import pytest
import geopandas

from ..data import GeoRegionData, InvalidGeoData


def test_creation():
    path_to_data = geopandas.datasets.get_path("nybb")
    gdf = geopandas.read_file(path_to_data)
    #print(gdf)
    assert len(gdf) == 5
    nyc_boroughs = GeoRegionData(gdf,'nyc_boroughs')
    
    assert nyc_boroughs.shape == (5,)
    assert len(nyc_boroughs.components) == 7
    
    assert nyc_boroughs.crs == gdf.crs
    
def test_error_on_bad_creation():
    not_geo_data = np.array(([1,2,3],[3,4,5]))
    with pytest.raises(InvalidGeoData):
        glue_data = GeoRegionData(not_geo_data,'bad')
    