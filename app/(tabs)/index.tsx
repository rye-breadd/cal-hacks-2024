import { Image, StyleSheet, Platform, View, TouchableOpacity, Text, Alert } from 'react-native';
import { CameraView, Camera } from 'expo-camera';

import { HelloWave } from '@/components/HelloWave';
import ParallaxScrollView from '@/components/ParallaxScrollView';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { SetStateAction, useEffect, useRef, useState } from 'react';
import { CameraType } from 'expo-camera/build/legacy/Camera.types';

export default function HomeScreen() {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [cameraVisible, setCameraVisible] = useState(true);
  const [cameraRef, setCameraRef] = useState(null);

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  if (hasPermission === null) {
    return <View />;
  }
  if (hasPermission === false) {
    return <Text>No access to camera</Text>;
  }

  return (
    <View style={styles.container}>
      {/* Logo at the top */}
      <Image style={styles.logo} />

      {/* Camera view */}
      <View style={styles.cameraContainer}>
        <TouchableOpacity
          style={styles.hideCameraButton}
          onPress={() => setCameraVisible(!cameraVisible)}
        >
          <Text style={styles.hideCameraText}>
            {cameraVisible ? 'Hide camera' : 'Show camera'}
          </Text>
        </TouchableOpacity>

        {cameraVisible && (
          <CameraView
            style={styles.cameraView}
          >
            <View style={styles.cameraView}>
              <TouchableOpacity>
                <Text>Flip Camera</Text>
              </TouchableOpacity>
            </View>
          </CameraView> 
        )}
      </View>

      {/* OK to drive button */}
      <View style={styles.okButtonContainer}>
        <TouchableOpacity style={styles.okButton} onPress={() => Alert.alert('Checked', 'You are OK to drive!')}>
          <Text style={styles.okButtonText}>OK TO DRIVE</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  logo: {
    width: 100,
    height: 100,
    resizeMode: 'contain',
    marginBottom: 20,
  },
  cameraContainer: {
    width: '90%',
    alignItems: 'center',
    backgroundColor: '#e0e0e0',
    borderRadius: 10,
    marginBottom: 20,
    padding: 10,
  },
  hideCameraButton: {
    marginBottom: 10,
  },
  hideCameraText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  cameraView: {
    width: '100%',
    height: 200,
    // backgroundColor: '#a52a2a', // Placeholder for the camera feed (brown/red)
    borderRadius: 10,
  },
  okButtonContainer: {
    width: '90%',
    alignItems: 'center',
  },
  okButton: {
    width: '100%',
    padding: 20,
    backgroundColor: '#d3d3d3', // Light grey background for the button
    borderRadius: 10,
    alignItems: 'center',
  },
  okButtonText: {
    color: '#4caf50', // Green checkmark color
    fontWeight: 'bold',
    fontSize: 18,
  },
});
