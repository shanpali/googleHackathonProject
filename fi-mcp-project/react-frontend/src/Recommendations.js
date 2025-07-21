import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Recommendations() {
  const [recommendations, setRecommendations] = useState('');

  useEffect(() => {
    axios.get('/recommendations').then(res => {
      setRecommendations(res.data.recommendations || JSON.stringify(res.data, null, 2));
    });
  }, []);

  return (
    <div>
      <h2>Recommendations</h2>
      <pre>{recommendations}</pre>
    </div>
  );
}

export default Recommendations; 