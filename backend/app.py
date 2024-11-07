from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

# Formula to convert food weight and serving size form whatever unit the user used to grams.
def convert_to_grams(weight, unit):
    if unit == 'kg':
        return weight * 1000
    elif unit == 'oz':
        return weight * 28.3495
    elif unit == 'lb':
        return weight * 453.592
    elif unit == 'mL':
        return weight
    elif unit == 'lb_oz':
        parts = weight.split()
        pounds = float(parts[0])
        ounces = float(parts[2])
        return (pounds * 453.592) + (ounces * 28.3495)
    # Or just return it as is if the user used grams.
    else:
        return weight

@app.route('/api/calories', methods=['POST'])
def calculate_macros():
    data = request.get_json()
    print("Received data:", data)

    # Defining all of the different bits of info we got from the frontend.
    food_name = data.get('foodName')
    subclass = data.get('subclass')
    weight = round(to_float(data.get('weight')))
    serving_size = to_float(data.get('servingSize'))
    unit = data.get('unit')
    fat_per_serving = to_float(data.get('fat'))
    protein_per_serving = to_float(data.get('protein'))
    carbs_per_serving = to_float(data.get('carbs'))
    fiber_per_serving = to_float(data.get('fiber'))
    sugar_alcohol_per_serving = to_float(data.get('sugarAlcohol'))
    sodium = to_float(data.get('sodium'))
    cholesterol = to_float(data.get('cholesterol'))

    # Use the above formula to convert weight and serving size to grams.
    weight_in_grams = convert_to_grams(weight, unit)
    serving_size_in_grams = convert_to_grams(serving_size, unit)

    # Calculating the main macros.
    fat = round((fat_per_serving / serving_size_in_grams) * weight_in_grams)
    protein = round((protein_per_serving / serving_size_in_grams) * weight_in_grams)
    net_carbs_per_serving = carbs_per_serving - fiber_per_serving - sugar_alcohol_per_serving
    net_carbs = round((net_carbs_per_serving / serving_size_in_grams) * weight_in_grams)

    # Calculating the calories from the macros we just calculated.
    calories = (fat * 9) + (protein * 4) + (net_carbs * 4)

    # Create the result string that will be passed back to the client.
    result_string = f"{weight}g of {food_name} ({subclass}): {calories} calories, {protein}g of protein, {net_carbs}g of carbs, {fat}g of fat"
    result_string = f"{weight}{unit} of {food_name} ({subclass}): {calories} calories, {protein}g of protein, {net_carbs}g of carbs, {fat}g of fat"

    print(result_string)

    return jsonify({
        'result': result_string,
        'foodName': food_name,
        'subclass': subclass,
        'amount': weight,
        'unit': unit,
        'calories': calories,
        'fat': fat,
        'protein': protein,
        'carbs': net_carbs,
        'fiber': fiber_per_serving,
        'sugarAlcohol': sugar_alcohol_per_serving,
        'sodium': sodium,
        'cholesterol': cholesterol
    })

if __name__ == '__main__':
    app.run(debug=True)