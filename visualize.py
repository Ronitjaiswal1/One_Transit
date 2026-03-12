import folium
import pandas as pd

def create_digital_twin_map(stops_df):
    # Centered at Kashmere Gate, Delhi
    m = folium.Map(location=[28.6675, 77.2282], zoom_start=12, tiles="CartoDB dark_matter")
    
    for _, stop in stops_df.head(100).iterrows():
        folium.CircleMarker(
            location=[stop.stop_lat, stop.stop_lon],
            radius=3,
            color="cyan",
            fill=True,
            tooltip=stop.stop_name
        ).add_to(m)
    
    m.save("delhi_digital_twin.html")

# Run this to generate your interactive map file