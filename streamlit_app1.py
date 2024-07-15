import streamlit as st
import folium
import pandas as pd
import time
import gpxpy
from geopy.distance import geodesic


# Load GPX data
def parse_gpx(file_path):
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    data = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                data.append({
                    'latitude': point.latitude,
                    'longitude': point.longitude,
                    'time': point.time
                })
    return pd.DataFrame(data)

# Calculate speed between two points
def calculate_speed(start_point, end_point):
    distance = geodesic((start_point['longitude'], start_point['latitude']),
                        (end_point['longitude'], end_point['latitude'])).kilometers
    time_taken = (end_point['time'] - start_point['time']).total_seconds() / 3600  # Convert seconds to hours
    speed = distance / time_taken if time_taken > 0 else 0
    return speed

# Function to determine the toll rate based on the time
def get_toll_rate(current_time):
    morning_peak_start = pd.to_datetime('07:00').time()
    morning_peak_end = pd.to_datetime('09:00').time()
    evening_peak_start = pd.to_datetime('17:00').time()
    evening_peak_end = pd.to_datetime('19:00').time()
    
    if morning_peak_start <= current_time <= morning_peak_end:
        return 150
    elif evening_peak_start <= current_time <= evening_peak_end:
        return 150
    else:
        return 100

# Load and parse GPX file
gpx_file_path = 'acpath.gpx'
df = parse_gpx(gpx_file_path)

# Calculate speeds
df['speed'] = df.apply(lambda row: calculate_speed(df.iloc[row.name-1], row) if row.name > 0 else 0, axis=1)

# Define toll plaza coordinates
toll_plazas = {
    'Nelamangala': [13.092826736232652, 77.39473782625215],
    'Guilalu': [14.055369833138183, 76.56271933416862],
    'Karjeevanahalli': [13.61198352649271, 76.95380633790906],
    'Chokkanahalli': [13.339718899688936, 77.15355370553621]
}

# Function to display folium map in Streamlit
def folium_static(map):
    map.save('map2.html')
    with open('map2.html', 'r', encoding='utf-8') as f:
        map_html = f.read()
    st.components.v1.html(map_html, width=700, height=500)

# Initialize Streamlit app
def main():
    st.title('GPS Toll Based Simulation Using Python')

    st.markdown("## Route Map")
    st.markdown("This map shows the route and toll plazas along the journey.")

    # Initialize a folium map
    start_coord = [df.iloc[0]['longitude'], df.iloc[0]['latitude']]
    m = folium.Map(location=start_coord, zoom_start=7)

    # Add markers for start and end points
    folium.Marker(location=start_coord, popup='Bengaluru', icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(location=[df.iloc[-1]['longitude'], df.iloc[-1]['latitude']], popup='Chitradurga', icon=folium.Icon(color='red')).add_to(m)

    # Add markers for toll plazas
    for name, coords in toll_plazas.items():
        folium.Marker(location=coords, popup=name, icon=folium.Icon(color='orange')).add_to(m)

    # Add the route to the map
    route_coords = df[['longitude', 'latitude']].values.tolist()
    folium.PolyLine(route_coords, color='blue').add_to(m)

    # Display the map in Streamlit
    folium_static(m)
    
    st.markdown("---")
    st.markdown("## GPS Simulation Animation")
    st.markdown("This animation shows the vehicle's journey with toll deduction.")

    # Display the GIF animation
    gif_path = 'D:\\tekey\\work\\Intel Project\\gps_animation.gif'  # Replace with your actual path
    gif_file = open(gif_path, "rb").read()
    st.image(gif_file, caption='GPS Toll Based Simulation', use_column_width=True)

    st.markdown("---")
    st.markdown("## Coordinates Of Toll Plaza Along The Route")
    st.markdown("Nelamangala : 13.092826736232652, 77.39473782625215")
    st.markdown("Chokkanahalli : 13.339718899688936, 77.15355370553621")
    st.markdown("Karjeevanahalli : 13.61198352649271, 76.95380633790906")
    st.markdown("Guilalu : 14.055369833138183, 76.56271933416862")
    st.markdown("---")
    
    st.markdown("## Speed Monitoring")
    st.markdown("This section shows the current speed of the vehicle.")

    speed_limit = 60  # Speed limit in km/h

    for index, row in df.iterrows():
        if row['speed'] > speed_limit:
            st.error(f"Speed Limit Exceeded at index {index}! Current Speed: {row['speed']:.2f} km/h")
        else:
            st.success(f"Current Speed at index {index}: {row['speed']:.2f} km/h")

    st.markdown("## Dynamic Pricing Simulation")

    # Assume initial balance
    initial_balance = 10000
    balance = initial_balance

    for index, row in df.iterrows():
        current_time = pd.to_datetime(row['time']).time()
        toll_rate = get_toll_rate(current_time)
        
        for name, coords in toll_plazas.items():
            if geodesic((row['longitude'], row['latitude']), coords).kilometers < 0.25:
                balance -= toll_rate
                st.warning(f"Toll at {name}! New Balance: {balance} (Rate: {toll_rate})")

    st.markdown(f"## Final Balance: {balance}")

if __name__ == '__main__':
    main()
