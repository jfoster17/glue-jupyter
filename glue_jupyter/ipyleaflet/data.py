from glue.core.data import Data
#from glue.core.coordinates import Coordinates
from glue.config import data_translator
import geopandas
from glue.core.subset import ElementSubsetState, Subset
from glue.core.component import Component, CoordinateComponent
from glue.core.component_id import ComponentIDList

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
        
        self._centroid_component_ids = ComponentIDList()
        #self.gdf = data #Expensive duplication of data, but it is easy. Could use a data translator instead.
        #self.coords = GeoRegionCoordinates(n_dim=1)
        #data must be a GeoPandas object
        #self.coordinate_componenets = []
        if isinstance(data, geopandas.GeoSeries) or isinstance(data, geopandas.GeoDataFrame):
            self.geometry = None
            self.centroids = data.representative_point() #Naming of centroid is a bit misleading, but easier than representative point
            #self.add_component(self.centroids.y,label='Centroid '+data.crs.axis_info[1].name)
            for i in range(2):
                label = data.crs.axis_info[i].name + ' (Centroid)'
                if i == 0:
                    cid = self.add_component(self.centroids.y,label=label)
                elif i == 1:
                    cid = self.add_component(self.centroids.x,label=label)
                self._centroid_component_ids.append(cid)
            
            if isinstance(data, geopandas.GeoDataFrame):
                self.geometry = data.geometry    
                for name,values in data.iteritems():
                    if name != data.geometry.name: #Is this safe?
                        self.add_component(values, label=name)
                    else:
                        #https://leblancfg.com/unhashable-python-unique-locations-geometry-geodataframe.html
                        self.add_component(values.apply(lambda x: x.wkt).values,label='geometry')
            
        else:
            raise InvalidGeoData("Input data needs to be of type geopandas.GeoSeries or geopandas.GeoDataFrame")
        self.meta['crs'] = data.crs
        
        #def get_mask(self, subset_state, view=None):
        #    if isinstance(subset_state, ElementSubsetState):
                
        
@data_translator(geopandas.GeoDataFrame)
class GeoPandasTranslator:
 
    def to_data(self, data):
        return GeoRegionData(data)
 
    def to_object(self, data_or_subset, attribute=None):
        gdf = geopandas.GeoDataFrame()
        coords = data_or_subset.coordinate_components
        if isinstance(data_or_subset, Subset):
            #geom = data_or_subset.data.geometry
            centroids = data_or_subset.data._centroid_component_ids #because these are sort of fake coords
            crs = data_or_subset.data.meta['crs']
        else:
            #geom = data_or_subset.geometry
            centroids = data_or_subset._centroid_component_ids #because these are sort of fake coords
            crs = data_or_subset.meta['crs']
            
        #gdf.geometry = geom
        for cid in data_or_subset.components:
            if (cid not in coords) and (cid not in centroids):
                if cid.label == 'geometry':
                    g = geopandas.GeoSeries.from_wkt(data_or_subset[cid])
                    gdf[cid.label] = g
                else:
                    gdf[cid.label] = data_or_subset[cid]
        gdf.set_geometry("geometry",inplace=True)
        gdf.crs = crs
        return gdf

    
    
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