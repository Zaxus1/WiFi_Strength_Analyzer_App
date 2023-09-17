from PIL import Image
import matplotlib.pyplot as plt
from math import sqrt, sin, cos, atan, fabs, pi, e
import os.path
from matplotlib.colors import LinearSegmentedColormap
import subprocess
import webbrowser
import requests


def get_location_coordinates(location_name):
    try:
        # Use a geocoding service to get latitude and longitude based on location name
        geocoding_url = f"https://nominatim.openstreetmap.org/search?format=json&q={location_name}"
        response = requests.get(geocoding_url)
        data = response.json()
        if data and len(data) > 0:
            latitude = float(data[0]['lat'])
            longitude = float(data[0]['lon'])
            return latitude, longitude
        else:
            return None
    except Exception as e:
        print(f"Error getting location coordinates: {str(e)}")
        return None


def get_map_image(map_file_path_or_url):
    try:
        # Check if the input is a URL (starts with 'http' or 'https')
        if map_file_path_or_url.startswith('http://') or map_file_path_or_url.startswith('https://'):
            # You can use a library like requests to download the image
            # Here, we assume you have downloaded it already and provide the file path
            # Replace with the downloaded image path
            map_image_path = 'downloaded_map_image.png'
        else:
            map_image_path = map_file_path_or_url

        if os.path.exists(map_image_path):
            return Image.open(map_image_path)
        else:
            return None
    except Exception as e:
        print(f"Error loading map image: {str(e)}")
        return None


# Constants for geographic coordinates (you can customize these)
MIN_LAT = 39.902541
MAX_LAT = 39.909508
MAX_LON = -75.351278
MIN_LON = -75.357601

MIN_EAST = 0  # Replace with actual values
MAX_NORTH = 0  # Replace with actual values
EAST_LEN = 0  # Replace with actual values

MAX_X = 1000
MAX_Y = 1000


def get_path_obstacle(rgb_map, x1, y1, x2, y2):
    rssi_subtract = 0
    dx = x2 - x1
    dy = y2 - y1
    px_distance = sqrt(dy ** 2 + dx ** 2)
    path_angle = fabs(atan(dy / dx)) if not dx == 0 else pi / 2
    x_neg = dx < 0
    y_neg = dy < 0
    for path_distance in range(int(px_distance)):
        path_x = path_distance * cos(path_angle) * (-1 if x_neg else 1)
        path_y = path_distance * sin(path_angle) * (-1 if y_neg else 1)
        path_x = path_x + x1
        path_y = path_y + y1
        r, g, b = rgb_map.getpixel((path_x, path_y))
        if b - r > 30 and g - r > 30:
            rssi_subtract += 2
        elif r - g > 30 and r - b > 30:
            rssi_subtract += 8
        elif g - r > 30 and g - b > 30:
            rssi_subtract += 6
        elif b - r > 30 and b - g > 30:
            rssi_subtract += 4
    return rssi_subtract


def draw_heat_map(rssi_map, min_val, max_val, width, height):
    cmap = LinearSegmentedColormap.from_list(
        'custom_cmap', [(0, 'black'), (1, 'red')])
    heat_map = plt.imshow([[0, 0], [0, 0]], cmap=cmap)
    heat_map.set_data([[rssi_map[(x, y)] for y in range(height)]
                      for x in range(width)])
    plt.colorbar(heat_map)
    plt.show()


def create_map(location_name):
    # Get location coordinates
    location_coordinates = get_location_coordinates(location_name)
    if location_coordinates:
        latitude, longitude = location_coordinates
        print(
            f"Location Coordinates - Latitude: {latitude}, Longitude: {longitude}")

        # Use latitude and longitude to dynamically fetch a map image
        map_dir = f"https://maps.openstreetmap.de/staticmap.php?center={latitude},{longitude}&zoom=15&size=800x600&maptype=mapnik"
        response = requests.get(map_dir)
        if response.status_code == 200:
            with open("map_image.png", "wb") as file:
                file.write(response.content)

            obstacle_map = Image.open("map_image.png")
            width, height = obstacle_map.size
            rgb_map = obstacle_map.convert("RGB")
            rssi_map = {}
            ap_x = latitude  # Set the AP x-coordinate based on latitude
            ap_y = longitude  # Set the AP y-coordinate based on longitude

            for x in range(width):
                for y in range(height):
                    r, g, b = rgb_map.getpixel((x, y))
                    if r == g == b == 0:
                        rssi_map[(x, y)] = -1
                        continue
                    dy = x - ap_x
                    dx = y - ap_y
                    distance = sqrt(dy**2 + dx**2) / 10
                    # Replace with your equation
                    raw_rssi = e ** (-0.232584 * distance) * \
                        (87.4389 - 81 * e ** (0.232584 * distance))
                    adjusted_rssi = raw_rssi - \
                        get_path_obstacle(rgb_map, x, y, ap_x, ap_y)
                    rssi_map[(x, y)] = adjusted_rssi
            draw_heat_map(rssi_map, -90, -30, width, height)
        else:
            print('Error fetching map image.')
    else:
        print('Location not found.')


if __name__ == "__main__":
    location_name = input("Enter the location name (e.g., city or address): ")
    create_map(location_name)
