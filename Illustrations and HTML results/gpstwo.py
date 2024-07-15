import geopandas as gpd
import pandas as pd
import osmnx as ox
import networkx as nx
from shapely.geometry import Point, LineString
import requests
import folium
from folium.plugins import MarkerCluster
import imageio
from PIL import Image
import io
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
# 1. One World Trade Center, NYC
# 2. Madison Square Park, NYC

addresses = ["Mavalli, Bengaluru, Karnataka 560004, India", "Chitradurga, Karnataka 577501, India"]

# Geocode the addresses
geocode_url = "https://nominatim.openstreetmap.org/search"
locations = [[12.96557, 77.60624],[14.22554, 76.39821]]

# If we want to consider any other locations other than the above two, then we can uncomment this section. 
"""for address in addresses:
    params = {'q': address, 'format': 'json'}
    try:
        response = requests.get(geocode_url, params=params)
        response.raise_for_status()  # Check if the request was successful
        data = response.json()
        if data:
            lat, lon = float(data[0]['lat']), float(data[0]['lon'])
            locations.append((lat, lon))
        else:
            print(f"No data found for address: {address}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except (IndexError, ValueError, KeyError) as e:
        print(f"Error processing data for address '{address}': {e}")

print(locations)"""


# Create a GeoDataFrame for the locations
data = gpd.GeoDataFrame({'geometry': [Point(lon, lat) for lat, lon in locations]}, crs="EPSG:4326")

# Get the graph for the area
north, south = 14.3, 12.9  # Adjust these values to extend the bounding box
east, west = 77.7, 76.3 
G = ox.graph_from_bbox(bbox=(north, south, east, west), network_type='drive')
print(1)
# Get the nearest network nodes to the start and end points
start_node = ox.distance.nearest_nodes(G, locations[0][1], locations[0][0])
end_node = ox.distance.nearest_nodes(G, locations[1][1], locations[1][0])

# Get the route between the points
route = nx.shortest_path(G, start_node, end_node, weight='length')
route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]
route_line = LineString([(lon, lat) for lat, lon in route_coords])

# Sample route points
num_samples = 75
route_sampled = [route_line.interpolate(float(i) / (num_samples - 1), normalized=True) for i in range(num_samples)]
route_sampled_coords = [(point.y, point.x) for point in route_sampled]

# Initialize a list to store images
images = []

service = ChromeService(ChromeDriverManager(driver_version='126.0.6478.12').install())
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=options)


print(2)
i=0
for point in route_sampled_coords:
    # Create a new map for each frame using the base map
    m_frame = folium.Map(location=[locations[0][0], locations[0][1]], zoom_start=13)
    folium.TileLayer('OpenStreetMap',attr='OpenStreetMap').add_to(m_frame)
    folium.TileLayer('Stamen Terrain',attr='Stamen Terrain').add_to(m_frame)
    folium.TileLayer('Stamen Toner',attr='Stamen Toner').add_to(m_frame)
    folium.TileLayer('Stamen Watercolor',attr='Stamen Watercolor').add_to(m_frame)
    folium.TileLayer('cartodbpositron',attr='CartoDB Positron').add_to(m_frame)
    folium.TileLayer('cartodbdark_matter',attr='CartoDB Dark Matter').add_to(m_frame)
    
    folium.Marker(location=[locations[0][0], locations[0][1]], popup='Start', icon=folium.Icon(color='green')).add_to(m_frame)
    folium.Marker(location=[locations[1][0], locations[1][1]], popup='End', icon=folium.Icon(color='red')).add_to(m_frame)
    folium.PolyLine(route_coords, color='blue').add_to(m_frame)
    folium.CircleMarker(location=point, radius=10, color='red', fill=True, fill_color='red').add_to(m_frame)
    
    # Markers for toll plaza along the path
    folium.Marker(location=[13.092826736232652, 77.39473782625215], popup='Nelamangala', icon=folium.Icon(color='orange')).add_to(m_frame)
    folium.Marker(location=[14.055369833138183, 76.56271933416862], popup='Guilalu', icon=folium.Icon(color='orange')).add_to(m_frame)
    folium.Marker(location=[13.61198352649271, 76.95380633790906], popup='Karjeevanahalli', icon=folium.Icon(color='orange')).add_to(m_frame)
    folium.Marker(location=[13.339718899688936, 77.15355370553621], popup='Chokkanahalli', icon=folium.Icon(color='orange')).add_to(m_frame)

    # To adjust the zoom factor dynamically
    bounds = [[min(point[0], locations[0][0], locations[1][0]), min(point[1], locations[0][1], locations[1][1])],
              [max(point[0], locations[0][0], locations[1][0]), max(point[1], locations[0][1], locations[1][1])]]
    m_frame.fit_bounds(bounds)
    
    # Save the map as an image
    html = m_frame.get_root().render()
    # To store the rendered code in a temporary gpstwo.html file. A temp file must be created prior
    with open("gpstwo.html", "w") as file:
        file.write(html)
     
    # Takes the output of the rendered code to take a screenshoot
    driver.get("http://127.0.0.1:5500/gpstwo.html")
    time.sleep(5)  # Adjust delay as necessary
    img_data = driver.get_screenshot_as_png()
    img = Image.open(io.BytesIO(img_data))
    images.append(img)
    img.show()
    print("hi {}".format(i))
    i+=1

# Save the animation as a GIF
imageio.mimsave('animated_karnataka1.gif', images, duration=0.1)
