from glue.core.data import Data
#from glue.core.coordinates import Coordinates
from glue.config import data_translator
import geopandas

#geo_data = GeoRegionData(, coords=GeoRegionCoordinates)

class InvalidGeoData(Exception):
    pass


class GeoRegionData(Data):
    """
    A class to hold descriptions of geographic regions in the style of GeoPandas (https://geopandas.org/en/stable/)
    
    data must be a GeoPandas object, either a GeoSeries or a GeoDataFrame
    
    We calculate centroid positions on the geometry column in order to provide components of the correct
    dimension for glue-ing/subsetting on and to serve as proxy components in the ipyleaflet viewer. 
    
    """
    
    def __init__(self, data, label="", coords=None, **kwargs):
        super(GeoRegionData, self).__init__()
        self.label = label
        self.geometry = None
        self.gdf = data #Expensive duplication of data, but it is easy. Could use a data translator instead.
        #self.coords = GeoRegionCoordinates(n_dim=1)
        #data must be a GeoPandas object
        if isinstance(data, geopandas.GeoSeries):
            self.geometry = None
            self.centroids = data.centroid
            self.add_component(self.centroids.x,label='Centroid '+ data.crs.axis_info[0].name)
            self.add_component(self.centroids.y,label='Centroid '+data.crs.axis_info[1].name)
    
        elif isinstance(data, geopandas.GeoDataFrame):
            self.geometry = data.geometry
            self.centroids = data.centroid
            self.add_component(self.centroids.x,label='Centroid '+data.crs.axis_info[0].name)
            self.add_component(self.centroids.y,label='Centroid '+data.crs.axis_info[1].name)
    
            for name,values in data.iteritems():
                if name != data.geometry.name: #Is this safe?
                    self.add_component(values, label=name)
        else:
            raise InvalidGeoData("Input data needs to be of type geopandas.GeoSeries or geopandas.GeoDataFrame")
        self.crs = data.crs
        
@data_translator(geopandas.GeoDataFrame)
class GeoPandasTranslator:
 
    def to_data(self, obj):
        self.geometry = None
        self.gdf = data #Expensive duplication of data, but it is easy. Could use a data translator instead.
         
        self.geometry = data.geometry
        self.centroids = data.centroid
        self.add_component(self.centroids.x,label='Centroid '+data.crs.axis_info[0].name)
        self.add_component(self.centroids.y,label='Centroid '+data.crs.axis_info[1].name)
        
        for name,values in data.iteritems():
            if name != data.geometry.name: #Is this safe?
                self.add_component(values, label=name)
        self.crs = data.crs
        
 
    def to_object(self, data_or_subset, attribute=None):
        return self.gdf #Does not work on subsets, and should actually put it back together instead of just keeping two copies in memory

    
    
# @data_translator(pd.DataFrame)
# class PandasTranslator:
# 
#     def to_data(self, obj):
#         result = Data()
#         for c in obj.columns:
#             result.add_component(obj[c], str(c))
#         return result
# 
#     def to_object(self, data_or_subset, attribute=None):
#         df = pd.DataFrame()
#         coords = data_or_subset.coordinate_components
#         for cid in data_or_subset.components:
#             if cid not in coords:
#                 df[cid.label] = data_or_subset[cid]
#         return df

    
#class GeoRegionCoordinates(Coordinates):
#    """
#    A class to provide access to geographic coordinates
#    """
#    def __init__(self):
#        super(GeoRegionCoordinates, self).__init__()