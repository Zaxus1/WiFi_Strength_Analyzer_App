import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

const MyScreen = () => {
  const [output, setOutput] = useState('');

  const handleButtonPress = async () => {
    try {
      // Get Access Points
      const accessPointsResponse = await fetch('http://192.168.68.116:8080/get_aps', {
        method: 'GET',
      });

      if (!accessPointsResponse.ok) {
        throw new Error('Network response was not ok');
      }

      const accessPointsData = await accessPointsResponse.json();
      console.log('Access Points:', accessPointsData);

      // Get Distance
      const accessPointMac = 'AP_MAC_ADDRESS'; // Replace with actual AP MAC address
      const distanceResponse = await fetch(`http://192.168.68.116:8080/get_distance?ap_mac=${accessPointMac}`, {
        method: 'GET',
      });

      if (!distanceResponse.ok) {
        throw new Error('Network response was not ok');
      }

      const distanceData = await distanceResponse.json();
      console.log('Distance Data:', distanceData);

      // Create Map
      const mapData = {
        ap_x: 100, // Replace with actual values
        ap_y: 200, // Replace with actual values
        map_dir: 'path/to/map', // Replace with actual path
      };

      const createMapResponse = await fetch('http://192.168.68.116:8080/create_map', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(mapData),
      });

      if (!createMapResponse.ok) {
        throw new Error('Network response was not ok');
      }

      const createMapData = await createMapResponse.json();
      console.log('Create Map Data:', createMapData);

      // Update output state
      setOutput('Data fetched successfully');
    } catch (error) {
      console.error('Error calling Python server:', error.message);
      setOutput('Error: ' + error.message);
    }
  };

  return (
    <View center>
      <TouchableOpacity onPress={handleButtonPress} style={styles.button}>
        <Text style={styles.buttonText}>Run Python Script</Text>
      </TouchableOpacity>

      {/* Display the output */}
      <Text>{output}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#007BFF',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 5,
    alignItems: 'center',
    marginBottom: 20,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default MyScreen;
