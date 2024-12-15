import React, { useState, useEffect } from 'react';
import DatePicker from 'react-datepicker';
import { format, addDays } from 'date-fns';
import 'react-datepicker/dist/react-datepicker.css';
import './App.css';

function App() {
  const [formData, setFormData] = useState({
    date: format(new Date(), 'yyyy-MM-dd'),
    foodName: '',
    subclass: '',
    weight: '',
    weightUnit: 'g',
    calories: '',
    servingSize: '',
    servingSizeUnit: 'g',
    fat: '',
    saturatedFat: '',
    transFat: '',
    carbs: '',
    fiber: '',
    sugarAlcohol: '',
    protein: '',
    sodium: '',
    cholesterol: '',
    weightPounds: '',
    weightOunces: '',
    servingSizePounds: '',
    servingSizeOunces: ''
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

    // Using the GET method in the controller to pull FoodItem objects in the DB for this date.
    fetch(`http://127.0.0.1:5000/api/fooditems?date=${dateKey}`)
      .then(response => response.json())
      .then(data => {
        setEntriesByDate(prevEntries => ({
          ...prevEntries,
          [dateKey]: data
        }));

        const newTotals = data.reduce(
          (acc, entry) => {
            const regex = /(\d+(\.\d+)?) calories, (\d+(\.\d+)?)g of protein, (\d+(\.\d+)?)g of carbs, (\d+(\.\d+)?)g of fat/;
            const matches = entry.result.match(regex);
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
          calories: Math.round(newTotals.calories * 100) / 100,
          protein: Math.round(newTotals.protein * 100) / 100,
          carbs: Math.round(newTotals.carbs * 100) / 100,
          fat: Math.round(newTotals.fat * 100) / 100
        });
      })
      .catch(error => {
        console.error('Error fetching food items:', error);
      });
  }, [currentDate, entriesByDate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevFormData) => ({
      ...prevFormData,
      [name]: value < 0 ? 0 : value
    }));
  };

  const handleKeyDown = (e) => {
    const invalidChars = ['e', 'E', '+', '-'];
    if (invalidChars.includes(e.key)) {
      e.preventDefault();
    }
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
  
    fetch('http://127.0.0.1:5000/api/fooditems', {
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
        [dateKey]: [...(prevEntries[dateKey] || []), data]
      }));
    })
    .catch(error => {
      console.error('Error:', error);
    });
  };

  const handleDelete = (id) => {
    console.log(`The ID to delete: ${id}`);
    fetch(`http://127.0.0.1:5000/api/fooditems/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => response.json())
    .then(data => {
      console.log('Successfully deleted:', data);
      const dateKey = format(currentDate, 'yyyy-MM-dd');
      setEntriesByDate(prevEntries => ({
        ...prevEntries,
        [dateKey]: prevEntries[dateKey].filter(entry => entry.id !== id)
      }));
    })
    .catch(error => {
      console.error('Error while deleting:', error);
    });
  };

  const handleDateChange = (date) => {
    formData.date = format(date, 'yyyy-MM-dd');
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
                  <div className="form-group" style={{ flex: '2' }}>
                    <label>Item:</label>
                    <input type="text" name="foodName" value={formData.foodName} onChange={handleChange} required />
                  </div>
                  {formData.weightUnit === 'lb_oz' ? (
                    <>
                      <div className="form-group" style={{ flex: '1' }}>
                        <label>Weight: (lbs)</label>
                        <input type="number" name="weightPounds" value={formData.weightPounds} onChange={handleChange} onKeyDown={handleKeyDown} />
                      </div>
                      <div className="form-group" style={{ flex: '1' }}>
                        <label>Weight: (oz)</label>
                        <input type="number" name="weightOunces" value={formData.weightOunces} onChange={handleChange} onKeyDown={handleKeyDown} />
                      </div>
                    </>
                  ) : (
                    <div className="form-group" style={{ flex: '1' }}>
                      <label>Weight:</label>
                      <input type="number" name="weight" value={formData.weight} onChange={handleChange} onKeyDown={handleKeyDown} required />
                    </div>
                  )}
                  <div className="form-group" style={{ flex: '1' }}>
                    <label>Unit:</label>
                    <select name="weightUnit" value={formData.weightUnit} onChange={handleChange} required>
                      <option value="g">g</option>
                      <option value="oz">oz</option>
                      <option value="lb_oz">lb & oz</option>
                      <option value="mL">mL</option>
                      <option value="kg">Kg</option>
                    </select>
                  </div>
                </div>
                <div className="form-group">
                  <label>Sub-description:</label>
                  <input type="text" name="subclass" value={formData.subclass} onChange={handleChange} />
                </div>
              </fieldset>
              <fieldset>
                <legend>Nutrition Label Information:</legend>
                <div className="form-group">
                  {formData.servingSizeUnit === 'lb_oz' ? (
                    <>
                      <div className="form-group" style={{ flex: '2' }}>
                        <label>Serving size: (lbs)</label>
                        <input type="number" name="servingSizePounds" value={formData.servingSizePounds} onChange={handleChange} onKeyDown={handleKeyDown} />
                      </div>
                      <div className="form-group" style={{ flex: '2' }}>
                        <label>Serving size: (oz)</label>
                        <input type="number" name="servingSizeOunces" value={formData.servingSizeOunces} onChange={handleChange} onKeyDown={handleKeyDown} />
                      </div>
                    </>
                  ) : (
                    <div className="form-group" style={{ flex: '3' }}>
                      <label>Serving size:</label>
                      <input type="number" name="servingSize" value={formData.servingSize} onChange={handleChange} onKeyDown={handleKeyDown} required />
                    </div>
                  )}
                  <div className="form-group" style={{ flex: '1' }}>
                    <label>Unit:</label>
                    <select name="servingSizeUnit" value={formData.servingSizeUnit} onChange={handleChange} required>
                      <option value="g">g</option>
                      <option value="oz">oz</option>
                      <option value="lb_oz">lb & oz</option>
                      <option value="mL">mL</option>
                      <option value="kg">Kg</option>
                    </select>
                  </div>
                </div>
                <div className="form-group">
                  <div className="form-group half-width" style={{ flex: '1' }}>
                    <label>Fat (g):</label>
                    <input type="number" name="fat" value={formData.fat} onChange={handleChange} onKeyDown={handleKeyDown} required />
                  </div>
                  <div className="form-group half-width" style={{ flex: '1' }}>
                    <label>Carbs (g):</label>
                    <input type="number" name="carbs" value={formData.carbs} onChange={handleChange} onKeyDown={handleKeyDown} required />
                  </div>
                  <div className="form-group half-width" style={{ flex: '1' }}>
                    <label>Protein (g):</label>
                    <input type="number" name="protein" value={formData.protein} onChange={handleChange} onKeyDown={handleKeyDown} required />
                  </div>
                </div>
                <div className="form-group">
                  <div className="form-group half-width" style={{ flex: '1' }}>
                    <label>Saturated Fat (g):</label>
                    <input type="number" name="saturatedFat" value={formData.saturatedFat} onChange={handleChange} onKeyDown={handleKeyDown} />
                  </div>
                  <div className="form-group half-width" style={{ flex: '1' }}>
                    <label>Fiber (g):</label>
                    <input type="number" name="fiber" value={formData.fiber} onChange={handleChange} onKeyDown={handleKeyDown} />
                  </div>
                  <div className="form-group half-width" style={{ flex: '1' }}>
                    <label>Sodium (mg):</label>
                    <input type="number" name="sodium" value={formData.sodium} onChange={handleChange} onKeyDown={handleKeyDown} />
                  </div>
                </div>
                <div className="form-group">
                  <div className="form-group half-width" style={{ flex: '1' }}>
                    <label>Trans Fat (g):</label>
                    <input type="number" name="transFat" value={formData.transFat} onChange={handleChange} onKeyDown={handleKeyDown} />
                  </div>
                  <div className="form-group half-width" style={{ flex: '1' }}>
                    <label>Sugar Alcohol (g):</label>
                    <input type="number" name="sugarAlcohol" value={formData.sugarAlcohol} onChange={handleChange} onKeyDown={handleKeyDown} />
                  </div>
                  <div className="form-group half-width" style={{ flex: '1' }}>
                    <label>Cholesterol (mg):</label>
                    <input type="number" name="cholesterol" value={formData.cholesterol} onChange={handleChange} onKeyDown={handleKeyDown} />
                  </div>
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
                <li key={index}>
                  {result.result}
                  <button onClick={() => handleDelete(result.id)}>X</button>
                </li>
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