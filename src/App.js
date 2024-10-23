import React, { useEffect, useState } from 'react';

function App() {
  const [calories, setCalories] = useState(null);

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/calories')
      .then(response => response.json())
      .then(data => setCalories(data.calories))
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Calorie Counter</h1>
        {calories !== null ? (
          <p>Today's calorie intake: {calories}</p>
        ) : (
          <p>Loading...</p>
        )}
      </header>
    </div>
  );
}

export default App;