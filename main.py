import requests

# Function to get RSSI and distance from the server


def get_rssi_and_distance(ap_mac):
    try:
        response = requests.get(
            f'http://127.0.0.1:8080/get_distance?ap_mac={ap_mac}')
        if response.status_code == 200:
            data = response.json()
            ap_rssi = data['ap_rssi']
            distance = data['distance']
            return ap_rssi, distance
        else:
            return None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None


if __name__ == '__main__':
    ap_mac = input("Enter the MAC address of the Access Point (AP): ")

    ap_rssi, distance = get_rssi_and_distance(ap_mac)

    if ap_rssi is not None and distance is not None:
        print(f"RSSI: {ap_rssi} dBm, Distance: {distance} meters")
    else:
        print("Error getting RSSI and distance. Please check the MAC address or try again later.")
