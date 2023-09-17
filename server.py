from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import pywifi
import time
from math import log10
from wifi_scanner import get_aps, get_distance
from map_creator import create_map
from wifi_scanner import get_rssi_and_distance

app = Flask(__name__)
CORS(app, origins="http://localhost:8080")

app.logger.setLevel(logging.DEBUG)

# ... Other Flask code ...


@app.route('/get_aps', methods=['GET'])
def get_access_points():
    try:
        nearby_aps = get_aps()
        return jsonify({'access_points': nearby_aps}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_distance', methods=['GET'])
def get_access_point_distance():
    try:
        ap_mac = request.args.get('ap_mac')
        if ap_mac is None:
            return jsonify({'error': 'ap_mac parameter is missing'}), 400

        ap_rssi, distance = get_distance(ap_mac)
        return jsonify({'ap_rssi': ap_rssi, 'distance': distance}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/create_map', methods=['POST'])
def create_obstacle_map():
    try:
        data = request.json  # Assuming you send data to create the map

        # Add debugging code to print the received data
        print("Received data:", data)

        if data is None:
            return jsonify({'error': 'Invalid JSON data'}), 400

        ap_x = data.get('ap_x')
        ap_y = data.get('ap_y')
        map_dir = data.get('map_dir')

        if ap_x is None or ap_y is None or map_dir is None:
            return jsonify({'error': 'Missing required data fields'}), 400

        create_map(ap_x, ap_y, map_dir)
        return jsonify({'message': 'Map created successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='192.168.68.116', port=8080)
