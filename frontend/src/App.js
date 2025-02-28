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

  const [currentDate, setCurrentDate] = useState(new Date());
  const [currentEntries, setCurrentEntries] = useState([]);
  const [totals, setTotals] = useState({
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0
  });

  // State tracking for the edit functionality.
  const [editingId, setEditingId] = useState(null);
  const [initialValues, setInitialValues] = useState({
    weight: '',
    weightUnit: '',
    name: '',
    sub_description: '',
    calories: '',
    protein: '',
    carbs: '',
    fat: ''
  });

  const [editValues, setEditValues] = useState({
    weight: '',
    weightUnit: '',
    name: '',
    sub_description: '',
    calories: '',
    protein: '',
    carbs: '',
    fat: ''
  });

  // This state contains the full set of FoodLog objects for the entire month.
  // When the fetch call to the /search endpoint is successful, that data is returned and set to this state.
  const [thisMonthsFoodLogs, setThisMonthsFoodLogs] = useState([]);

  // This state will be used to track all FoodLogs pulled in the fetchFoodLogs function.
  // We'll use this to determine what to do when a new FoodItem is created; either create the new FoodLog altogether or just update an existing one.
  const [existingFoodLogs, setExistingFoodLogs] = useState([]);

  // This const is checking if the day set in the currentDate state is in the existingFoodLogs array.
  // If True, then the FoodLob object exists. If False, it doesn't. This is used for conditional rendering later.
  // UPDATE: Changing this logic a bit! We'll kill two birds with one stone here; get the condition for the conditional rendering and get today's specific FoodLog.
  // Start by immediatey getting the day part of the currentDate state.
  // Now use the find() method on the thisMonthsFoodLogs to iterate over each log inside of it and search for a log where the day attribute = the day we just grabbed.
  // If there exists one, then currentFoodLog will = that specific FoodLog object. If not, then it'll equal null.
  // Now we have the FoodLog we need to display the FoodItems for the date the user is on and we can also just use that as the condition to render the Create or Update button.
  const currentDay = currentDate.getDate();
  const currentFoodLog = thisMonthsFoodLogs.find(log => log.day === currentDay) || null;
  console.log("Today's FoodLog: ", currentFoodLog);


  useEffect(() => {
    const dateKey = formData.date;

    console.log("Date key to send to the server: ", dateKey);

    fetchFoodLogs(dateKey);
    //fetchFoodItems(dateKey);
  }, [currentDate]);

  // Just adding a useEffect() to the existingFoodLogs state for logging purposes.
  useEffect(() => {
    console.log("Existing FoodLogs this month from the DB: ", existingFoodLogs);
  }, [existingFoodLogs]);

  useEffect(() => {
    console.log("FoodLogs as they are set in the thisMonthsFoodLogs state: ", thisMonthsFoodLogs);
  }, [thisMonthsFoodLogs]);

  const fetchFoodLogs = (dateKey) => {

    console.log("Date in fetchFoodLogs: ", dateKey);
    console.log("Type of date in fetchFoodLogs: ", typeof(dateKey));

    // The dateKey is a string when it's passed into the function so we pass it directly into the query.
    fetch(`http://127.0.0.1:5000/api/foodlog/search?date=${dateKey}`)
      .then(response => response.json())
      .then(data => {
          console.log("FoodLogs pulled from /search endpoint: ", data);
          // Taking the data we got and setting it as the thisMonthsFoodLogs state.
          // With this, we now have access to all of these FoodLogs throughout the code and can display them in the results panel.
          setThisMonthsFoodLogs(data);

          // Creating a new array consisting all of the days in the FoodLog objects that were pulled.
          const daysPulled = data.map(log => log.day);
          // Setting that array as the existingFoodLogs state.
          setExistingFoodLogs(daysPulled);
      })
      .catch(error => {
          console.error("Error while attempting to fetch FoodLogs: ", error);
      });

  }

  // Moving the fetching logic into it's own function call.
  // This allows us to readily call this function in more places, like right after the POST call to update the food log right after a new food item is added.
  const fetchFoodItems = (dateKey) => {
    // Using the GET method in the controller to pull FoodItem objects in the DB for this date.
    fetch(`http://127.0.0.1:5000/api/foodlog?date=${dateKey}`)
      .then(response => response.json())
      .then(data => {
        console.log('Data received from server:', data);
        setCurrentEntries(data);

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
  }

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

  const onCreate = (e) => {
    console.log("We are in the onCreate function!");

    fetch('http://127.0.0.1:5000/api/foodlog', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
      console.log('Success: ', data);
    })
    .catch(error => {
      console.error('Error:', error);
    });
  };

  const onUpdate = (e) => {
    console.log("We are in the onUpdate function!");

    fetch('http://127.0.0.1:5000/api/foodlog', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData),
    })
    .then(response => response.json())
    .then(data => {
      console.log('Success: ', data);
    })
    .catch(error => {
      console.error('Error:', error);
    });
  };

/*  const handleSubmit = (e) => {
    e.preventDefault();
  
    const { carbs, fiber, sugarAlcohol } = formData;
    const fiberValue = parseFloat(fiber) || 0;
    const sugarAlcoholValue = parseFloat(sugarAlcohol) || 0;
    const carbsValue = parseFloat(carbs) || 0;
  
    if (fiberValue + sugarAlcoholValue > carbsValue) {
      alert("Fiber and sugar alcohols together cannot exceed total carbs.");
      return;
    }

    // To relieve some pressure from the server, we're doing the weight formatting here before the data is ever sent off.
    if (formData.weightUnit === "lb_oz") {
      formData.weightPounds = parseFloat(formData.weightPounds).toString().replace(/(\.\d*[1-9])0+$/, '$1').replace(/\.0+$/, '');
      formData.weightOunces = parseFloat(formData.weightOunces).toString().replace(/(\.\d*[1-9])0+$/, '$1').replace(/\.0+$/, '');

      // Also going to create the "&" string here as a template literal.
      // This way the server doesn't have to do any formatting at all. Regardless of flow, formData.weight will have the exact weight in the exact format we need.
      formData.weight = (`${formData.weightPounds}&${formData.weightOunces}`)
      
      console.log("Formatted weightPounds: ", formData.weightPounds);
      console.log("Formatted weightOunces: ", formData.weightOunces);
      console.log("Formatted weight: ", formData.weight);
    }
    else {
      formData.weight = parseFloat(formData.weight).toString().replace(/(\.\d*[1-9])0+$/, '$1').replace(/\.0+$/, '');
      console.log("Formatted weight: ", formData.weight);
    }
    
    fetch('http://127.0.0.1:5000/api/foodlog', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
      console.log('Success: ', data);

      // Now that a new a food item is successfully created, immediately update the log which now includes said new item.
      fetchFoodItems(formData.date);
    })
    .catch(error => {
      console.error('Error:', error);
    });
  };*/

  const handleDelete = (id) => {
    console.log(`The ID to delete: ${id}`);
    fetch(`http://127.0.0.1:5000/api/foodlog/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => response.json())
    .then(data => {
      console.log('Successfully deleted:', data);

      // FoodItem was successfully deleted, now update the result-panel with a new GET call so that the deleted FoodItem doesn't linger.
      fetchFoodItems(formData.date);
    })
    .catch(error => {
      console.error('Error while deleting:', error);
    });
  };

  const handleDateChange = (date) => {
    formData.date = format(date, 'yyyy-MM-dd');
    setCurrentDate(date);
  };

  // Handler function for clicking the edit button.
  // Immediately sets the state for the initialValues and editValues and captures the ID of the FoodItem we're editing.
  const handleEdit = (id, item) => {
    setEditingId(id);

    console.log("The item we're editing: ", item);

    setInitialValues({
      weight: item.weight_value,
      weightUnit: item.weight_unit,
      name: item.name,
      sub_description: item.sub_description,
      calories: item.macros.calories,
      protein: item.macros.protein,
      carbs: item.macros.carbs,
      fat: item.macros.fat
    });

    setEditValues({
      weight: item.weight_value,
      weightUnit: item.weight_unit,
      name: item.name,
      sub_description: item.sub_description,
      calories: item.macros.calories,
      protein: item.macros.protein,
      carbs: item.macros.carbs,
      fat: item.macros.fat
    });
  };

  // Handler function for any changes to the edit fields that are rendered.
  // initialValues ALWAYS remains the same, but this one changes editValues to whatever the user changed them to.
  const handleEditChange = (e) => {
    console.log("triggered");
    const { name, value } = e.target;
  
    setEditValues((prevValues) => {
      let newValue;
  
      // To ensure that no type mismatches occur between initialValues and editValues, we set the type based on the field.
      // Calories, carbs, fat, protein, and weight are cast as Numbers if that's the field edited.
      if (['calories', 'carbs', 'fat', 'protein', 'weight'].includes(name)) {
        newValue = value === '' ? '' : Number(value) < 0 ? 0 : Number(value);
      } else {
        // If it's another, then it can become a string and that's fine because those fields are also strings in initialValues.
        newValue = value;
      }

      // To make sure that the user doesn't save mismatched weight and weight unit values, we clear the weight field when switching between values here.
      // This is so they don't do something like switch from g to kg, forget to change the weight value, then save the FoodItem as 350kg instead of 350g. Big difference there.
      // So first identify that the change happened to the weight unit.
      if (name === 'weightUnit') {
        // Now we return a new object composed of the values before editing with the new weightUnit and weight set as an empty string.
        return {
          // Use the spread operator to break apart prevValues are return all of it's attributes.
          ...prevValues,
          // BUT with these two explicitly set. So basically, keep everything else, but change these two.
          weight: '',
          weightUnit: value
        };
      }

      // Lb&oz flow provides a bit of a different case since that turns into two fields when editing.
      // So first we check if the field being edited is either of those fields.
      if (name === 'weightLbs' || name === 'weightOz') {

        // Now we dynamically set both weightLbs and weightOz; we check for the field we're editing first.
        // If the condition comes back as true (which means it's the field they're editing), the newValue will be set (what the user entered).
        // If the condition comes back as false, it gets the previous/existing value (which means they were editing the other field).
        const weightLbs = name === 'weightLbs' ? newValue : prevValues.weight.split('&')[0];
        const weightOz = name === 'weightOz' ? newValue : prevValues.weight.split('&')[1];

        // Now we've got our new lb&oz value, slap 'em back together and set that string as the weight value!
        newValue = `${weightLbs}&${weightOz}`;
        return {
          ...prevValues,
          weight: newValue
        };
      }
  
      return {
        ...prevValues,
        [name]: newValue
      };
    });
  };

  // Handler function for clicking the save button on the edit feature.
  const handleEditSave = (id) => {
    const changes = {};
    let isChanged = false;

    console.log("Item ID to edit: ", id);
    console.log("initialValues when save button clicked: ", initialValues);
    console.log("editValues when save button clicked: ", editValues);
    console.log("Type of initialValues items: ", (typeof initialValues.calories))
    console.log("Type of editValues items: ", (typeof editValues.calories))

    // Ensuring that the weight field(s) are filled out.
    // First check what the user set as the weightUnit.
    if (editValues.weightUnit === 'lb_oz') {
      // If they chose lb_oz, then we split weight into the two separate lb & oz values.
      const [weightLbs, weightOz] = editValues.weight.split('&');
      // Then we check that they're both filled.
      if (!weightLbs || !weightOz) {
        // If not, throw an error, reset the edit ID to bring the field back to nornal, and return - no HTTP request sent whatsoever.
        console.log('Weight fields must be filled when editing.');
        setEditingId(null);
        return;
      }
    }
    else {
      // Same deal the other weight units, just don't have to do the splitting then.
      // So just check if weight is empty and throw an error and return if so.
      if (!editValues.weight) {
        console.log('Weight field must be filled when editing.');
        setEditingId(null);
        return;
      }
    }

    // initialValues were save right when the edit button was click, along with the editValues.
    // editValues may or may not have been updated by any change in the edit fields by handleEditChange.
    // We compare each value with this for loop.
    for (const key in initialValues) {
      console.log("initialValues key being compared: ", initialValues[key])
      console.log("editValues key being compared: ", editValues[key])
      // If any value does not match, we determine changes have been made and log the changes.
      // When values are changed, they come back in editValues as strings. This can lead to false positives here;
      // For example, if the field detects input, but the input ends up being the same as the initial value, this condition will still trigger since it's then comparing a Number to a string.
      // To avoid that, we cast the editValue being compared as a Number. This way, it's always comparing a Number object to a Number object. No false positives.

      // UPDATE: We now explicitly set the type when editing, so no need to cast here anymore
      if (initialValues[key] !== editValues[key]) {
        changes[key] = editValues[key];
        isChanged = true;
      }
    }

    console.log("changes object: ", changes)

    // If no changes, we just log that and do not send any requests.
    if (!isChanged) {
      console.log('No changes detected, no request sent.');
      // Set the editingId back to null so that it renders in the result panel with the normal format.
      setEditingId(null);
      return;
    }

    // Determining which HTTP verb to send based on the number of changes made.
    // If changes and initialValues have the same number of properties, that means the user changed everything so we send a PUT.
    // Otherwise, the user only made some changes and so PATCH is the appropriate verb to send.
    const method = Object.keys(changes).length === Object.keys(initialValues).length ? 'PUT' : 'PATCH';
    console.log("HTTP verb = ", method);

    // Send the request to the server.
    fetch(`http://127.0.0.1:5000/api/foodlog/${id}`, {
      method: method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(changes)
    })
    .then(response => response.json())
    .then(data => {
      console.log('Successfully updated: ', data);

      // Set the editingId back to null so that it renders in the result panel with the normal format.
      setEditingId(null);

      // Update the list to display the updated values.
      fetchFoodItems(formData.date);
    })
    .catch(error => {
      console.error('Error while updating: ', error);
    });
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Simple Calorie Counter</h1>
        <div className="container">
          <div className="form-panel">
            <form /*onSubmit={handleSubmit}*/>
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
              {currentFoodLog ? (
                <button type="button" onClick={onUpdate}>Update</button>
              ) : (
                <button type="button" onClick={onCreate}>Create</button>
              )}
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
                <li key={index} className="list-item">
                {editingId === result.id ? (
                  <>
                    <span className="result-text">
                    {editValues.weightUnit === "lb_oz" ? (
                      <>
                        <input
                          type="number"
                          name="weightLbs"
                          value={editValues.weight.split("&")[0] || ""}
                          onChange={handleEditChange}
                          className="small-input"
                          placeholder="Lbs"
                        />
                        <input
                          type="number"
                          name="weightOz"
                          value={editValues.weight.split("&")[1] || ""}
                          onChange={handleEditChange}
                          className="small-input"
                          placeholder="Oz"
                        />
                      </>
                    ) : (
                      <input
                        type="number"
                        name="weight"
                        value={editValues.weight}
                        onChange={handleEditChange}
                        className="small-input"
                        placeholder="Weight"
                      />
                    )}
                      <select
                        name="weightUnit"
                        value={editValues.weightUnit}
                        onChange={handleEditChange}
                        className="small-input"
                      >
                        <option value="g">g</option>
                        <option value="oz">oz</option>
                        <option value="lb_oz">lb & oz</option>
                        <option value="mL">mL</option>
                        <option value="kg">Kg</option>
                      </select> of
                      <input
                        type="text"
                        name="name"
                        value={editValues.name}
                        onChange={handleEditChange}
                        className="small-input"
                      /> (
                      <input
                        type="text"
                        name="sub_description"
                        value={editValues.sub_description}
                        onChange={handleEditChange}
                        className="small-input"
                      />)
                      <input
                        type="number"
                        name="calories"
                        value={editValues.calories}
                        onChange={handleEditChange}
                        className="small-input"
                      /> calories, 
                      <input
                        type="number"
                        name="protein"
                        value={editValues.protein}
                        onChange={handleEditChange}
                        className="small-input"
                      />g of protein, 
                      <input
                        type="number"
                        name="carbs"
                        value={editValues.carbs}
                        onChange={handleEditChange}
                        className="small-input"
                      />g of carbs, 
                      <input
                        type="number"
                        name="fat"
                        value={editValues.fat}
                        onChange={handleEditChange}
                        className="small-input"
                      />g of fat
                    </span>
                    <button className="button-common edit-save-button" onClick={() => handleEditSave(result.id)}>Save</button>
                  </>
                ) : (
                  <>
                    <span className="result-text">{result.result}</span>
                    <button className="button-common delete-button" onClick={() => handleDelete(result.id)} title="Press this button to delete this item from the log">X</button>
                    <button className="button-common edit-button" onClick={() => handleEdit(result.id, result)} title="Press this button to edit this item">Edit</button>
                  </>
                )}
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