# wifi_scanner.py

import ctypes
import os
import subprocess
import time
import pywifi
import json
import utm
import numpy as np
from math import log10

# Constants for geographic coordinates
MIN_LAT = 39.902541
MAX_LAT = 39.909508
MAX_LON = -75.351278
MIN_LON = -75.357601

MIN_EAST, MAX_NORTH, _, _ = utm.from_latlon(MIN_LAT, MIN_LON)
MAX_EAST, MIN_NORTH, _, _ = utm.from_latlon(MAX_LAT, MAX_LON)

EAST_LEN = MAX_EAST - MIN_EAST
NORTH_LEN = MAX_NORTH - MIN_NORTH

MAX_X = 1000
MAX_Y = 1000


def list_wifi_interfaces():
    wifi = pywifi.PyWiFi()
    interfaces = wifi.interfaces()

    if not interfaces:
        print("No WiFi interfaces found.")
        return []

    print("Available WiFi Interfaces:")
    for i, iface in enumerate(interfaces):
        print(f"Interface {i}: {iface.name()}")

    return interfaces


def get_mac_address():
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.disconnect()
    time.sleep(0.5)
    iface.scan()
    time.sleep(1)
    scan_results = iface.scan_results()

    for result in scan_results:
        ssid = result.ssid
        bssid = result.bssid
        if ssid and bssid:
            return bssid.lower()
    return None


def get_aps():
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    time.sleep(1.5)
    scan_out_data = {}
    scan_out_results = iface.scan_results()
    for result in scan_out_results:
        ssid = result.ssid
        bssid = result.bssid.lower()
        rssi = result.signal
        scan_out_data[bssid] = {"SSID": ssid, "RSSI": rssi}
    return scan_out_data


def get_distance(ap_mac):
    nearby_aps = get_aps()
    if ap_mac is None:
        print("MAC Address of the Wi-Fi interface not found")
        return -1, None
    if ap_mac not in nearby_aps.keys():
        print("Specified Access Point Not Found!")
        return -1, None
    ap_rssi = nearby_aps[ap_mac]["RSSI"]
    distance = -log10(2 * ((ap_rssi + 160) ** 9.9)) + \
        50  # Replace this with your equation
    return ap_rssi, distance


def main():
    interfaces = list_wifi_interfaces()
    if not interfaces:
        print("No WiFi interfaces available.")
        return

    print("Number of WiFi Interfaces:", len(interfaces))

    for i, iface in enumerate(interfaces):
        print(f"Interface {i + 1}: {iface}")

    print("\nWiFi Interfaces:")
    if interfaces:
        selected_iface = interfaces[0]
        print(f"Selected Interface: {selected_iface}")

        print(f"\nAvailable WiFi Networks for Interface '{selected_iface}':")
        networks = get_aps()
        for ssid, info in networks.items():
            print(f"SSID: {info['SSID']}, RSSI: {info['RSSI']} dBm")


def get_connected_network_ssid():
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True, check=True)
        output = result.stdout

        # Find the SSID in the output
        lines = output.split('\n')
        for line in lines:
            if "SSID" in line:
                ssid = line.strip().split(":")[1].strip()
                return ssid
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    return None


def display_available_networks():
    wifi = pywifi.PyWiFi()
    # Assuming you want to use the first interface
    iface = wifi.interfaces()[0]

    # Disconnect from any existing network and scan for nearby networks
    iface.disconnect()
    time.sleep(0.5)
    iface.scan()
    time.sleep(1)
    scan_results = iface.scan_results()

    available_networks = {}
    for result in scan_results:
        ssid = result.ssid
        if ssid:
            available_networks[ssid] = result.signal

    return available_networks


def get_connected_network_rssi():
    wifi = pywifi.PyWiFi()
    # Assuming you want to use the first interface
    iface = wifi.interfaces()[0]

    # Check if the interface is connected
    if iface.status() == pywifi.const.IFACE_CONNECTED:
        connected_ssid = get_connected_network_ssid()
        if connected_ssid:
            scan_results = iface.scan_results()
            for result in scan_results:
                ssid = result.ssid
                bssid = result.bssid
                if ssid == connected_ssid:
                    return result.signal  # Return the RSSI for the connected network

    return None

# function to establish a new connection


def createNewConnection(name, SSID, password):
    config = f"""<?xml version=\"1.0\"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
	<name>{name}</name>
	<SSIDConfig>
		<SSID>
			<name>{SSID}</name>
		</SSID>
	</SSIDConfig>
	<connectionType>ESS</connectionType>
	<connectionMode>auto</connectionMode>
	<MSM>
		<security>
			<authEncryption>
				<authentication>WPA2PSK</authentication>
				<encryption>AES</encryption>
				<useOneX>false</useOneX>
			</authEncryption>
			<sharedKey>
				<keyType>passPhrase</keyType>
				<protected>false</protected>
				<keyMaterial>{password}</keyMaterial>
			</sharedKey>
		</security>
	</MSM>
</WLANProfile>"""
    with open(name + ".xml", 'w') as file:
        file.write(config)
    command = "netsh wlan add profile filename=\"" + \
        name + ".xml\"" + " interface=Wi-Fi"
    os.system(command)

# function to connect to a network


def connect(name, SSID):
    command = "netsh wlan connect name=\"" + name + \
        "\" ssid=\"" + SSID + "\" interface=Wi-Fi"
    os.system(command)

# function to display available Wifi networks


def displayAvailableNetworks():
    command = "netsh wlan show networks interface=Wi-Fi"
    os.system(command)


def scan_wifi_networks():
    try:
        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]
        iface.scan()
        time.sleep(2)  # Wait for 2 seconds to allow the scan to complete
        scan_results = iface.scan_results()
        return scan_results
    except Exception as e:
        print(f"Error scanning WiFi networks: {str(e)}")
        return []


def calculate_distance(ap_rssi):
    # Replace this with your distance calculation logic
    # Example: Distance calculation based on RSSI (replace with your formula)
    # Formula used here is just a placeholder; you should use an appropriate formula
    # based on your specific wireless environment and hardware.
    # For illustration, we'll use a simple linear formula:
    # distance = 10 ^ ((-ap_rssi - A) / (10 * n))
    # Where A and n are constants for your wireless environment.

    A = 27  # Example constant (adjust as needed)
    n = 2   # Example constant (adjust as needed)

    distance = 10 ** ((-ap_rssi - A) / (10 * n))

    return distance


def get_rssi_and_distance(ap_mac):
    try:
        scan_results = scan_wifi_networks()

        for result in scan_results:
            if result.bssid.lower() == ap_mac.lower():
                ap_rssi = result.signal
                # Replace with your distance calculation function
                distance = calculate_distance(ap_rssi)
                return ap_rssi, distance

        # If the AP MAC address is not found in scan results
        return None, None
    except Exception as e:
        print(f"Error getting RSSI and distance: {str(e)}")
        return None, None


# display available networks
displayAvailableNetworks()

# input wifi name and password
name = input("Name of Wi-Fi: ")
password = input("Password: ")

# establish a new connection
createNewConnection(name, name, password)

# connect to the wifi network
connect(name, name)
print("If you aren't connected to this network, try connecting with the correct password!")

if __name__ == "__main__":
    rssi = get_connected_network_rssi()

    if rssi is not None:
        print(f"RSSI for connected network: {rssi} dBm")
    else:
        print("No connected network found.")

        available_networks = display_available_networks()
        if available_networks:
            print("Available Networks:")
            for ssid, signal in available_networks.items():
                print(f"SSID: {ssid}, RSSI: {signal} dBm")
        else:
            print("No available networks found.")
