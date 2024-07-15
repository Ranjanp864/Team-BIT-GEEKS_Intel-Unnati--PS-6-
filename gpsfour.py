import folium
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
from geopy.distance import geodesic
from folium import IFrame
import pandas as pd
from twilio.rest import Client
import random
from phonenumbers import parse, format_number, PhoneNumberFormat
import numpy as np
from datetime import datetime

# Twilio credentials
account_sid = 'ACd914975a5d61cfb7a7e55cc685c44cd2'
auth_token = '3d0b8454a9bd36c3f8ec6b77e627bfc8'

twilio_number = '+12515778765'

# Create a Twilio client
client = Client(account_sid, auth_token)

# Define toll plaza coordinates (latitude, longitude)
toll_plazas = {
    'Nelamangala': [13.092826736232652, 77.39473782625215],
    'Guilalu': [14.055369833138183, 76.56271933416862],
    'Karjeevanahalli': [13.61198352649271, 76.95380633790906],
    'Chokkanahalli': [13.339718899688936, 77.15355370553621]
}

# Coordinates for Bangalore and Chitradurga
locations = [[12.96557, 77.60624], [14.22554, 76.39821]]

# Predefined route points (latitude, longitude)
route_coords = [
        (77.60624, 12.96557), (77.57576, 12.97541), (77.56777, 12.99311), (77.56774, 12.9934), (77.56495, 12.99813), (77.52938, 13.03475), (77.51554, 13.04203), (77.4995, 13.0479), (77.49688, 13.04885), (77.49663, 13.04887), (77.44744, 13.06898), (77.41624, 13.08349), (77.36231, 13.12742), (77.3588, 13.13114), (77.33538, 13.15175), (77.33353, 13.15294), (77.33232, 13.15349), (77.31581, 13.16508), (77.31517, 13.16558), (77.30648, 13.17159), (77.30549, 13.17211), (77.29638, 13.17683), (77.27157, 13.19799), (77.26813, 13.20141), (77.26634, 13.20316), (77.25375, 13.21585), (77.23014, 13.24375), (77.22858, 13.24517), (77.21737, 13.25321), (77.21259, 13.25718), (77.20992, 13.25954), (77.20304, 13.26697), (77.19561, 13.27361), (77.14882, 13.31115),(77.1464, 13.31434), (77.14623, 13.31438), (77.14563, 13.31443), (77.14479, 13.31445), (77.14438, 13.31447),(77.14479, 13.31445), (77.14408, 13.31454), (77.14438, 13.31447), (77.14408, 13.31454),  (77.13686, 13.32227), (77.11696, 13.36789), (77.1163, 13.36874), (77.11523, 13.36983), (77.11392, 13.37092), (77.1065, 13.37494), (77.09737, 13.38057), (77.09635, 13.38285), (77.09544, 13.38515), (77.09411, 13.38836), (77.09303, 13.39106), (77.09197, 13.39359), (77.09065, 13.39698), (77.08707, 13.40512), (77.0862, 13.40691), (77.0851, 13.40936), (77.08228, 13.41414), (77.07583, 13.42164), (77.07219, 13.42589), (77.06037, 13.43974), (77.05924, 13.441), (77.04091, 13.46713), (77.03184, 13.47912), (77.01468, 13.49322), (77.01431, 13.49355), (77.01126, 13.49725), (77.00461, 13.51411), (77.00339, 13.51741), (77.00189, 13.52165), (77.0002, 13.53137), (76.99968, 13.53293), (76.99803, 13.53639), (76.99334, 13.54495), (76.99227, 13.54827), (76.99096, 13.55296), (76.9867, 13.56089), (76.97729, 13.57772), (76.97581, 13.5802), (76.97315, 13.58479),  (76.94985, 13.61859), (76.93759, 13.63771), (76.93715, 13.6386), (76.93501, 13.6432), (76.93028, 13.65385), (76.92968, 13.65508), (76.92604, 13.66123), (76.9253, 13.6624), (76.92339, 13.66488), (76.92273, 13.66582), (76.92234, 13.66666), (76.91915, 13.6714), (76.91781, 13.67629), (76.91693, 13.68094), (76.91655, 13.68302), (76.9161, 13.6868), (76.91462, 13.7015), (76.91438, 13.70884), (76.90844, 13.71923), (76.90398, 13.72321), (76.90167, 13.72522), (76.90104, 13.72585), (76.89664, 13.72977), (76.89151, 13.73698), (76.89082, 13.73872), (76.88869, 13.74385), (76.87079, 13.76049), (76.84831, 13.76945), (76.83825, 13.77552), (76.83708, 13.77609), (76.82686, 13.78127), (76.82249, 13.78338), (76.82138, 13.78399), (76.81339, 13.78843), (76.80967, 13.79036), (76.8053, 13.79355), (76.80333, 13.79626), (76.80282, 13.79685), (76.79657, 13.80378), (76.79567, 13.80479), (76.79436, 13.80594), (76.78004, 13.81855), (76.77714, 13.82103), (76.77028, 13.82582), (76.76487, 13.82895), (76.76263, 13.83029), (76.76092, 13.83138), (76.75882, 13.83281), (76.75511, 13.83515), (76.75, 13.8368), (76.74909, 13.83702), (76.74667, 13.83776), (76.7282, 13.84512), (76.72384, 13.85043), (76.72321, 13.85095), (76.71741, 13.85564), (76.7136, 13.85982), (76.71156, 13.8621), (76.70919, 13.86453), (76.70733, 13.86636), (76.69787, 13.87531), (76.69563, 13.87741), (76.69252, 13.87968), (76.68964, 13.88178), (76.68414, 13.88785), (76.68372, 13.88832), (76.68094, 13.89113), (76.67967, 13.89237), (76.67215, 13.90001), (76.66769, 13.90555), (76.66483, 13.90789), (76.6621, 13.91), (76.66113, 13.91086), (76.6587, 13.9136), (76.6572, 13.91499), (76.65066, 13.91993), (76.64701, 13.92129), (76.6443, 13.92214), (76.64288, 13.92254), (76.6239, 13.94989), (76.62369, 13.95025), (76.60643, 13.9689), (76.60171, 13.97591), (76.60041, 13.97786), (76.59623, 13.98402), (76.58934, 13.99496), (76.58775, 14.00349), (76.58502, 14.01361), (76.57671, 14.0293), (76.55924, 14.05511), (76.53626, 14.09182), (76.53557, 14.0928), (76.5271, 14.10212), (76.52646, 14.10343), (76.52416, 14.10857), (76.52022, 14.11647), (76.51288, 14.12365), (76.50866, 14.12669), (76.50592, 14.12845), (76.50535, 14.12893), (76.50175, 14.13218), (76.49653, 14.13671), (76.49221, 14.14051), (76.48852, 14.14586), (76.4625, 14.1812), (76.45323, 14.19183), (76.45055, 14.19354), (76.43327, 14.1978), (76.43257, 14.19841), (76.42539, 14.20694), (76.42256, 14.21031), (76.40263, 14.22463), (76.39845, 14.22512), (76.39934, 14.22498), (76.39821, 14.22554)
]

# Initialize a folium map
m = folium.Map(location=[12.9716, 77.5946], zoom_start=13)

# Add tile layers for different map styles with attribution
folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)
folium.TileLayer('Stamen Terrain', name='Stamen Terrain', attr='Stamen Terrain').add_to(m)
folium.TileLayer('Stamen Toner', name='Stamen Toner', attr='Stamen Toner').add_to(m)
folium.TileLayer('Stamen Watercolor', name='Stamen Watercolor', attr='Stamen Watercolor').add_to(m)
folium.TileLayer('cartodbpositron', name='CartoDB Positron', attr='CartoDB Positron').add_to(m)
folium.TileLayer('cartodbdark_matter', name='CartoDB Dark Matter', attr='CartoDB Dark Matter').add_to(m)

# Add markers for start and end points
folium.Marker(location=[locations[0][0], locations[0][1]], popup='Bangalore', icon=folium.Icon(color='green')).add_to(m)
folium.Marker(location=[locations[1][0], locations[1][1]], popup='Chitradurga', icon=folium.Icon(color='red')).add_to(m)

# Add markers to toll plaza
for name, coords in toll_plazas.items():
    folium.Marker(location=coords, popup=name, icon=folium.Icon(color='orange')).add_to(m)

# Add the route to the map
folium.PolyLine(locations=[(route[1], route[0]) for route in route_coords], color='blue').add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Toll price per KM on highway
TOLL_PRICE_KM = 10

# To calculate the toll rate of the vehicle dynamically considering a variable
TOLL_PRICE_FOR_VEHICLE = 0

# Get the current time
current_time = datetime.now().time()

# Define the threshold time (6 PM)
threshold_time = datetime.strptime("18:00:00",'%H:%M:%S').time()  # 18:00:00 (6 PM)

# Compare the current time with the threshold
if current_time >= threshold_time:
    print("User is traveling after 6 PM.")

    # Penalty logic can go here
    TOLL_PRICE_FOR_VEHICLE += 200
    # For example, deducting points or adding penalty amount to be paid
else:
    print("User is traveling before 6 PM.")

# Define the coordinates for the where the highway start and end
source_hw = (13.01547, 77.55582)
destination_hw = (14.17418, 76.4685)
distance = 0

# Save map as HTML
m.save('route_map.html')
print(1)
time.sleep(10)

# Capture map image
img_data = m._to_png(5)
img = Image.open(io.BytesIO(img_data))

# Save map image
img.save('route_map.png')
print(2)
# Create animated GIF
frames = []
i = 1

service = ChromeService(ChromeDriverManager(driver_version='126.0.6478.12').install())
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=options)


# Load user data
df = pd.read_csv('C:\\Users\\ASUS\\all python files\\gpswithpaymentsimulation\\user_data.csv')
amount_balance = df.at[df.index[df['vehicle_id'] == 1][0], 'account_balance']

# Function to check if a vehicle is near a toll plaza
def is_near_toll_plaza(vehicle_coords, toll_coords, radius=0.025):
    return abs(vehicle_coords[0] - toll_coords[0]) < radius and abs(vehicle_coords[1] - toll_coords[1]) < radius

# Function to deduct toll amount from the user's account balance and send SMS
def deduct_amount_and_notify(vehicle_id, toll_name, distance, toll_amount):
    global df
    
    user_row_index = df[df['vehicle_id'] == vehicle_id].index[0]
    user_row = df[df['vehicle_id'] == vehicle_id].iloc[0]
    
    phone_number = user_row['mobile_number']

    # Ensure phone_number is a string
    if isinstance(phone_number, (np.int64, np.float64)):
        phone_number_str = str(int(phone_number))
    else:
        phone_number_str = str(phone_number)

    parsed_number = parse(phone_number_str, "IN")
    formatted_number = format_number(parsed_number, PhoneNumberFormat.E164)

    
    if user_row['account_balance'] >= toll_amount:
        global amount_balance
        new_balance = amount_balance - int(toll_amount)
        
        message = f"Toll Deduction: {toll_amount} INR has been deducted from your account at {toll_name}. New balance: {new_balance:.2f} INR. Distance travelled: {distance:.2f} km."
        client.messages.create(
            body=message,
            from_=twilio_number,
            to=formatted_number
        )
        print(message)
    else:
        print(f"Insufficient funds for vehicle_id {vehicle_id}")
        message = f"Toll Deduction: Insufficient funds to deduct {toll_amount} INR at {toll_name}. Your current balance is {new_balance:.2f} INR."
        client.messages.create(
            body=message,
            from_=twilio_number,
            to=formatted_number
        )
    amount_balance -= int(toll_amount) 

# Simulate the vehicle moving and checking for toll crossings
vehicle_id = 1  # Example vehicle_id
prev_coords = route_coords[0]  # Initial vehicle coordinates
distance_traveled = 0

for point in route_coords[1:]:
    m_frame = folium.Map(location=[locations[0][0], locations[0][1]], zoom_start=13)

    # Add tile layers
    folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m_frame)
    folium.TileLayer('Stamen Terrain', name='Stamen Terrain', attr='Stamen Terrain').add_to(m_frame)
    folium.TileLayer('Stamen Toner', name='Stamen Toner', attr='Stamen Toner').add_to(m_frame)
    folium.TileLayer('Stamen Watercolor', name='Stamen Watercolor', attr='Stamen Watercolor').add_to(m_frame)
    folium.TileLayer('cartodbpositron', name='CartoDB Positron', attr='CartoDB Positron').add_to(m_frame)
    folium.TileLayer('cartodbdark_matter', name='CartoDB Dark Matter', attr='CartoDB Dark Matter').add_to(m_frame)

    if(point[1] >= source_hw[0] and point[0] <= source_hw[1] and point[1] <= destination_hw[0] and point[0] >= destination_hw[1]):
        # Calculate the geodesic distance
        distance_traveled += geodesic(prev_coords, (point[1], point[0])).kilometers
        TOLL_PRICE_FOR_VEHICLE = distance_traveled * TOLL_PRICE_KM
        print(TOLL_PRICE_FOR_VEHICLE, distance_traveled)
    prev_coords = (point[1], point[0])

    # Add markers to toll plaza
    for name, coords in toll_plazas.items():
        if is_near_toll_plaza((point[1], point[0]), coords):
            html = f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>{name}</title>
                    </head>
                    <body>
                        <div style="background-color:white; padding:10px; border-radius:5px;">
                            <h4><center>{name}</center></h4>
                            <p>The distance travelled is {distance_traveled:.2f} km</p>
                            <p>Toll fees is {TOLL_PRICE_FOR_VEHICLE:.2f} INR</p>
                        </div>
                    </body>
                    </html>
                   """
            iframe = IFrame(html=html, height=200, width=200)
            folium.Marker(location=coords, popup=folium.Popup(iframe, show=True), icon=folium.Icon(color='orange')).add_to(m_frame)
            # Deduct amount and notify user
            deduct_amount_and_notify(vehicle_id, name, distance_traveled, TOLL_PRICE_FOR_VEHICLE)
        else:
            folium.Marker(location=coords, popup=name, icon=folium.Icon(color='orange')).add_to(m_frame)
            
    alternate_path_coords =[(77.07226, 13.42549), (77.07118, 13.4254), (77.06192, 13.42558), (77.05643, 13.42524), (77.04434, 13.4234), (77.04056, 13.42376), (77.03597, 13.42414), (77.03541, 13.42403), (77.03483, 13.42378), (77.03435, 13.4237), (77.02597, 13.41943), (77.02134, 13.41905), (77.01795, 13.415), (77.01532, 13.41924), (77.00924, 13.42368), (77.00807, 13.42461), (77.00664, 13.42558), (77.00481, 13.42629), (76.99398, 13.43191), (76.99196, 13.43357), (76.99158, 13.43392), (76.99093, 13.43868), (76.99062, 13.44014), (76.99035, 13.44078), (76.98522, 13.44164), (76.98365, 13.44187),(76.98122, 13.44222), (76.98139, 13.44358), (76.98161, 13.44467), (76.98225, 13.44724), (76.98229, 13.44758), (76.98219, 13.45105), (76.98299, 13.45632), (76.98451, 13.45776), (76.98577, 13.45889), (76.98577, 13.45914), (76.98552, 13.4596), (76.98553, 13.45989), (76.98588, 13.46151), (76.98675, 13.46536), (76.98742, 13.46649), (76.9888, 13.46898), (76.98933, 13.47023), (76.99091, 13.47337), (76.99509, 13.48127), (77.00415, 13.48402), (77.00636, 13.48438), (77.01075, 13.48629), (77.01095, 13.48632), (77.01431, 13.48641), (77.01797, 13.48903), (77.01863, 13.48928), (77.02034, 13.49012)]

    folium.PolyLine(locations=[[route[1], route[0]] for route in alternate_path_coords], color='red').add_to(m_frame)
        # Initialize variables
    is_on_alternate_path = False
    distance = 0
    toll_amount = 0

        
    # Check if the vehicle is on the alternate path
    if (point[1], point[0]) in alternate_path_coords:
        is_on_alternate_path = True
        continue  # Skip toll calculation when on alternate path

            # Calculate toll only if not on alternate path
    if not is_on_alternate_path:
            # Calculate distance traveled and toll amount
        if distance == 0:
            prev_coords = (point[1], point[0])
        else:
            distance_traveled += geodesic(prev_coords, (point[1], point[0])).kilometers
            toll_amount = distance * TOLL_PRICE_KM
            prev_coords = (point[1], point[0])

            # Process toll payment and notifications
    if is_near_toll_plaza((point[1], point[0]),[13.61198352649271, 76.95380633790906],0.01 ):
        if not is_on_alternate_path :
            deduct_amount_and_notify(vehicle_id,'Karjeevanahalli' , distance_traveled, toll_amount)
        else:
            print("Vehicle is on alternate path. No toll deduction.")

    # Reset distance and toll for specific points
    if (point[0], point[1]) in [(77.41624, 13.08349), (76.55924, 14.05511), (76.94985, 13.61859), (77.13686, 13.32227)]:
        distance_traveled = 0
        TOLL_PRICE_FOR_VEHICLE = 0

    # Add start and end markers
    folium.Marker(location=[locations[0][0], locations[0][1]], popup='Start', icon=folium.Icon(color='green')).add_to(m_frame)
    folium.Marker(location=[locations[1][0], locations[1][1]], popup='End', icon=folium.Icon(color='red')).add_to(m_frame)    
    folium.PolyLine(locations=[[route[1], route[0]] for route in route_coords], color='blue').add_to(m_frame)

    icon = folium.CustomIcon('ads.png', icon_size=(50, 50))
    folium.Marker(location=[point[1], point[0]], icon=icon).add_to(m_frame)

    bounds = [[min(point[1], locations[0][0], locations[1][0]), min(point[0], locations[0][1], locations[1][1])],
              [max(point[1], locations[0][0], locations[1][0]), max(point[0], locations[0][1], locations[1][1])]]
    m_frame.fit_bounds(bounds)

    # Capture map image
    html = m_frame.get_root().render()
    with open("C:\\Users\\ASUS\\all python files\\gpswithpaymentsimulation\\gpsfour.html", "w") as file:
        file.write(html)

    driver.get("file:///C:/Users/ASUS/all%20python%20files/gpswithpaymentsimulation/gpsfour.html")
    time.sleep(7)  # Adjust as needed to ensure the map loads fully
    map_elem = driver.find_element(By.CLASS_NAME, "folium-map")
    png = map_elem.screenshot_as_png
    img = Image.open(io.BytesIO(png))
    img.show()
    frames.append(img)
    i += 1

df.at[df.index[df['vehicle_id'] == 1][0], 'account_balance'] = int(amount_balance)
# Save the animated GIF
frames[0].save('gps_animation2.gif', save_all=True, append_images=frames[1:], duration=0.07, loop=0)
driver.quit()
