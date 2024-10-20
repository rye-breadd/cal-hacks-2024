import React, { useEffect, useState } from 'react';
import { View, Text } from 'react-native';
import axios from 'axios';

const App: React.FC = () => {
  const [data, setData] = useState<string>('');

  useEffect(() => {
    axios.get('http://127.0.0.1:5001/api/debug')
      .then((response) => {
        setData(response.data.message);
      })
      .catch((error) => console.error(error));
  }, []);

  return (
    <View>
      <Text>{data}</Text>
    </View>
  );
};

export default App;
