"""

state_geo_data is a GeoRegionData dataset with state regions defined

state_table_data is a normal glue dataset which is join_on_key by state_id to state_geo_data

capitol_data is a normal glue dataset which is joined by latitude and longitude to state_geo_data

Defining a subset of state_geo_data should select those elements in state_table_data AND the subset of
points in capitol_data that are inside those elements

So inside new_subset_group we could look for a GeoRegionData object and do something special iff there is

That's... not an elegant solution, but... 

What happens if we remove that DataSet that defines the link? Well, what happens with a current ElementSubsetState? Presumably these things get translated to MultiOr? 
but we've lost the original definition of the subset (in terms of geo...)

I think we need a custom subsetstate that contains BOTH definitions AND is automatically created from an ElementSubsetState or something else IF there is a RegionData dataset in the data_collection (and linked?). Of course then if we define a subset and THEN link, it should still work the same way. 

"""


def test_elementsubsetstate_on_regiondata_transfers_by_key():
    """
    """
    region_subset_state = ElementSubsetState(inds, state_geo_data)
    data_collection.new_subset_group(subset_state=region_subset_state,label='subset')
    data_collection.subset_groups[0].subsets[0].subset_state should be an ElementSubsetState on state_geo_data
    data_collection.subset_groups[0].subsets[1].subset_state should be an ElementSubsetState on state_table_data
    data_collection.subset_groups[0].subsets[2].subset_state should be an ElementSubsetState (or MaskSubsetState) on capitol_data but it needs to be computed via regions...
    
    
def test_elementsubsetstate_on_regiondata_transfers_by_lonlat():
    """
    """
    region_subset_state = ElementSubsetState(inds, state_geo_data)
    data_collection.new_subset_group(subset_state=region_subset_state,label='subset')
    data_collection.subset_groups[0].subsets[0].subset_state should be an ElementSubsetState on state_geo_data
    data_collection.subset_groups[0].subsets[2].subset_state should be an ElementSubsetState (or MaskSubsetState) on capitol_data but it needs to be computed via regions...
    The above should ONLY be the case if things are "properly" linked