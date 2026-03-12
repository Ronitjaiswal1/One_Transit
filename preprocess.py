import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def load_transit_data(folder="data/"):
    stops = pd.read_csv(f"{folder}stops.txt")
    # Convert to GeoDataFrame for spatial analysis
    geometry = [Point(xy) for xy in zip(stops.stop_lon, stops.stop_lat)]
    geo_stops = gpd.GeoDataFrame(stops, geometry=geometry, crs="EPSG:4326")
    
    # Add 2026 Merger Tags (Mocking DIMTS to DTC transition)
    routes = pd.read_csv(f"{folder}routes.txt")
    routes['operator'] = 'DTC' # In April 2026, all are DTC
    
    return geo_stops, routes

if __name__ == "__main__":
    stops, routes = load_transit_data()
    print(f"Successfully mapped {len(stops)} stops in Delhi.")