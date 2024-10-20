import React, { useEffect, useState } from 'react';
import { View, Image, StyleSheet, Text } from 'react-native';
import axios from 'axios';

const CameraStream: React.FC = () => {
  const [image, setImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch the video feed from Flask backend every 100ms
    const interval = setInterval(() => {
      axios
        .get('http://127.0.0.1:5001/video_feed', { responseType: 'blob' })
        .then((response) => {
          const url = URL.createObjectURL(response.data);
          setImage(url);
        })
        .catch((err) => {
          setError('Error fetching video stream');
          console.error(err);
        });
    }, 100); // Adjust this interval as needed

    return () => {
      clearInterval(interval);
    };
  }, []);

  return (
    <View style={styles.container}>
      {error && <Text style={styles.errorText}>{error}</Text>}
      {image ? (
        <Image source={{ uri: image }} style={styles.camera} />
      ) : (
        <Text style={styles.loadingText}>Loading video feed...</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  camera: {
    width: 300,
    height: 300,
    borderRadius: 10,
  },
  loadingText: {
    fontSize: 18,
    color: '#333',
  },
  errorText: {
    fontSize: 16,
    color: 'red',
  },
});

export default CameraStream;
