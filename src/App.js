import React, { useState, useEffect } from 'react';
import DatePicker from 'react-datepicker';
import { format, addDays } from 'date-fns';
import 'react-datepicker/dist/react-datepicker.css';
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
    sodium: '',
    cholesterol: ''
  });

  const [entriesByDate, setEntriesByDate] = useState({});
  const [currentDate, setCurrentDate] = useState(new Date());
  const [totals, setTotals] = useState({
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0
  });

  useEffect(() => {
    const dateKey = format(currentDate, 'yyyy-MM-dd');
    const currentEntries = entriesByDate[dateKey] || [];
    const newTotals = currentEntries.reduce(
      (acc, entry) => {
        const regex = /(\d+(\.\d+)?) calories, (\d+(\.\d+)?)g of protein, (\d+(\.\d+)?)g of carbs, (\d+(\.\d+)?)g of fat/;
        const matches = entry.match(regex);
        if (matches) {
          const [, calories, , protein, , carbs, , fat] = matches.map(Number);
          return {
            calories: acc.calories + (calories || 0),
            protein: acc.protein + (protein || 0),
            carbs: acc.carbs + (carbs || 0),
            fat: acc.fat + (fat || 0)
          };
        }
        return acc;
      },
      { calories: 0, protein: 0, carbs: 0, fat: 0 }
    );
    setTotals({
      calories: Math.round(newTotals.calories),
      protein: Math.round(newTotals.protein),
      carbs: Math.round(newTotals.carbs),
      fat: Math.round(newTotals.fat)
    });
  }, [currentDate, entriesByDate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (value < 0) return;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const { carbs, fiber, sugarAlcohol } = formData;
    const fiberValue = parseFloat(fiber) || 0;
    const sugarAlcoholValue = parseFloat(sugarAlcohol) || 0;
    const carbsValue = parseFloat(carbs) || 0;
  
    if (fiberValue + sugarAlcoholValue > carbsValue) {
      alert("Fiber and sugar alcohols together cannot exceed total carbs.");
      return;
    }

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

  const handleDateChange = (date) => {
    setCurrentDate(date);
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
                  <input type="text" name="subclass" value={formData.subclass} onChange={handleChange}/>
                </div>
              </fieldset>
              <fieldset>
                <legend>Nutrition Label Information:</legend>
                <div className="form-group">
                  <label>Calories:</label>
                  <input type="number" name="calories" value={formData.calories} onChange={handleChange} />
                  <label>Serving size (g):</label>
                  <input type="number" name="servingSize" value={formData.servingSize} onChange={handleChange} required />
                </div>
                <div className="form-group">
                  <label>Fat (g):</label>
                  <input type="number" name="fat" value={formData.fat} onChange={handleChange} required />
                </div>
                <div className="form-group">
                  <label>Carbs (g):</label>
                  <input type="number" name="carbs" value={formData.carbs} onChange={handleChange} required />
                </div>
                <div className="form-group">
                  <label>Fiber (g):</label>
                  <input type="number" name="fiber" value={formData.fiber} onChange={handleChange} />
                  <label>Sugar Alcohol (g):</label>
                  <input type="number" name="sugarAlcohol" value={formData.sugarAlcohol} onChange={handleChange} />
                </div>
                <div className="form-group">
                  <label>Protein (g):</label>
                  <input type="number" name="protein" value={formData.protein} onChange={handleChange} required />
                </div>
                <div className="form-group">
                  <label>Sodium (mg):</label>
                  <input type="number" name="sodium" value={formData.sodium} onChange={handleChange} />
                  <label>Cholesterol (mg):</label>
                  <input type="number" name="cholesterol" value={formData.cholesterol} onChange={handleChange} />
                </div>
              </fieldset>
              <button type="submit">Submit</button>
            </form>
          </div>
          <div className="results-panel">
            <div className="date-navigation">
              <button onClick={() => handleDateChange(addDays(currentDate, -1))}>Previous</button>
              <DatePicker
                selected={currentDate}
                onChange={handleDateChange}
                dateFormat="MMMM dd, yyyy"
              />
              <button onClick={() => handleDateChange(addDays(currentDate, 1))}>Next</button>
            </div>
            <h2>Food Log</h2>
            <ul>
              {currentEntries.map((result, index) => (
                <li key={index}>{result}</li>
              ))}
            </ul>
            <div className="totals">
              <p>{totals.calories} total calories, {totals.protein}g total of protein, {totals.carbs}g total of carbs, {totals.fat}g total of fat</p>
            </div>
          </div>
        </div>
      </header>
    </div>
  );
}

export default App;