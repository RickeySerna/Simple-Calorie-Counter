import React, { useState } from 'react';
import './App.css'; // Make sure to create this file for styling

function App() {
  const [formData, setFormData] = useState({
    foodName: '',
    subclass: '',
    amount: '',
    calories: '',
    fat: '',
    protein: '',
    carbs: '',
    fiber: '',
    sodium: ''
  });

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
      // Handle the response data as needed
    })
    .catch(error => {
      console.error('Error:', error);
    });
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Simple Calorie Counter</h1>
        <form onSubmit={handleSubmit}>
          <fieldset>
            <legend>Food Item Information:</legend>
            <div className="form-group">
              <label>Item:</label>
              <input type="text" name="foodName" value={formData.foodName} onChange={handleChange} required />
              <label>Weight (g):</label>
              <input type="number" name="amount" value={formData.amount} onChange={handleChange} required />
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
              <label>Weight (g):</label>
              <input type="number" name="amount" value={formData.amount} onChange={handleChange} required />
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
      </header>
    </div>
  );
}

export default App;
