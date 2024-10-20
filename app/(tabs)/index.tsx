import { Image, StyleSheet, Platform, View, TouchableOpacity, Text, Alert, ActivityIndicator } from 'react-native';
import { Video } from 'expo-av';
import { CameraView, Camera } from 'expo-camera';

import { HelloWave } from '@/components/HelloWave';
import ParallaxScrollView from '@/components/ParallaxScrollView';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import React, { SetStateAction, useEffect, useRef, useState } from 'react';
import { CameraType } from 'expo-camera/build/legacy/Camera.types';
import WebView from 'react-native-webview';
import { io, Socket } from 'socket.io-client';

export default function HomeScreen() {

  const [loading, setLoading] = useState(true);
  const [frame, setFrame] = useState<string | null>(null);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    // Connect to the WebSocket server
    socketRef.current = io('http://localhost:5001'); // Replace with your server URL

    // Listen for the video frame event
    socketRef.current.on('video_frame', (data) => {
      const byteArray = new Uint8Array(data.frame); // Convert data to Uint8Array
      const base64String = btoa(String.fromCharCode.apply(null, Array.from(byteArray)));
      setFrame(`data:image/jpeg;base64,${base64String}`);
      setLoading(false);
    });

    // Clean up the connection on unmount
    return () => {
      socketRef.current?.disconnect();
    };
  }, []);

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#0000ff" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {frame && <Image source={{ uri: frame }} style={styles.webview} resizeMode="contain" />}
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
  webview: {
    width: '100%',
    height: '100%',
  },
});
