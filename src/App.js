import React, { useState, useEffect } from 'react';
import { format, addDays } from 'date-fns';
import './App.css';

function App() {
  const [formData, setFormData] = useState({
    foodName: '',
    subclass: '',
    weight: '',
    calories: '',
    servingSize: '',
    fat: '',
    protein: '',
    carbs: '',
    fiber: '',
    sodium: ''
  });

  const [entriesByDate, setEntriesByDate] = useState({});
  const [currentDate, setCurrentDate] = useState(new Date());

  useEffect(() => {
  }, [currentDate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    fetch('http://127.0.0.1:5000/api/calories', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
      console.log('Success:', data);
      const dateKey = format(currentDate, 'yyyy-MM-dd');
      setEntriesByDate(prevEntries => ({
        ...prevEntries,
        [dateKey]: [...(prevEntries[dateKey] || []), data.result]
      }));
    })
    .catch(error => {
      console.error('Error:', error);
    });
  };

  const handleDateChange = (days) => {
    setCurrentDate(addDays(currentDate, days));
  };

  const currentEntries = entriesByDate[format(currentDate, 'yyyy-MM-dd')] || [];

  return (
    <div className="App">
      <header className="App-header">
        <h1>Simple Calorie Counter</h1>
        <div className="container">
          <div className="form-panel">
            <form onSubmit={handleSubmit}>
              <fieldset>
                <legend>Food Item Information:</legend>
                <div className="form-group">
                  <label>Item:</label>
                  <input type="text" name="foodName" value={formData.foodName} onChange={handleChange} required />
                  <label>Weight (g):</label>
                  <input type="number" name="weight" value={formData.weight} onChange={handleChange} required />
                </div>
                <div className="form-group">
                  <label>Sub-description:</label>
                  <input type="text" name="subclass" value={formData.subclass} onChange={handleChange} required />
                </div>
              </fieldset>
              <fieldset>
                <legend>Nutrition Label Information:</legend>
                <div className="form-group">
                  <label>Calories:</label>
                  <input type="number" name="calories" value={formData.calories} onChange={handleChange} required />
                  <label>Serving size (g):</label>
                  <input type="number" name="servingSize" value={formData.servingSize} onChange={handleChange} required />
                </div>
                <div className="form-group">
                  <label>Protein (g):</label>
                  <input type="number" name="protein" value={formData.protein} onChange={handleChange} required />
                </div>
                <div className="form-group">
                  <label>Fat (g):</label>
                  <input type="number" name="fat" value={formData.fat} onChange={handleChange} required />
                </div>
                <div className="form-group">
                  <label>Carbs (g):</label>
                  <input type="number" name="carbs" value={formData.carbs} onChange={handleChange} required />
                  <label>Dietary Fiber (g):</label>
                  <input type="number" name="fiber" value={formData.fiber} onChange={handleChange} />
                </div>
                <div className="form-group">
                  <label>Sodium (mg):</label>
                  <input type="number" name="sodium" value={formData.sodium} onChange={handleChange} />
                </div>
              </fieldset>
              <button type="submit">Submit</button>
            </form>
          </div>
          <div className="results-panel">
            <div className="date-navigation">
              <button onClick={() => handleDateChange(-1)}>Previous</button>
              <span>{format(currentDate, 'MMMM dd, yyyy')}</span>
              <button onClick={() => handleDateChange(1)}>Next</button>
            </div>
            <h2>Today's Entries</h2>
            <ul>
              {currentEntries.map((result, index) => (
                <li key={index}>{result}</li>
              ))}
            </ul>
          </div>
        </div>
      </header>
    </div>
  );
}

export default App;
