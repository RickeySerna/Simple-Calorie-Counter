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
def convert_to_grams(weight, unit, ounces=0.0):
    if unit == 'kg':
        return weight * 1000
    elif unit == 'oz':
        return weight * 28.3495
    elif unit == 'lb':
        return weight * 453.592
    elif unit == 'mL':
        return weight
    elif unit == 'lb_oz':
        return (weight * 453.592) + (ounces * 28.3495)
    # Or just return it as is if the user used grams.
    else:
        return weight

def format_weight(weight):
    if weight == int(weight):
        return str(int(weight))
    else:
        return str(weight)

@app.route('/api/calories', methods=['POST'])
def calculate_macros():
    data = request.get_json()
    print("Received data:", data)

    # Defining all of the different bits of info we got from the frontend.
    food_name = data.get('foodName')
    subclass = data.get('subclass')
    weight = to_float(data.get('weight'))
    weight_unit = data.get('weightUnit')
    serving_size = to_float(data.get('servingSize'))
    serving_size_unit = data.get('servingSizeUnit')
    fat_per_serving = to_float(data.get('fat'))
    protein_per_serving = to_float(data.get('protein'))
    carbs_per_serving = to_float(data.get('carbs'))
    fiber_per_serving = to_float(data.get('fiber'))
    sugar_alcohol_per_serving = to_float(data.get('sugarAlcohol'))
    sodium = to_float(data.get('sodium'))
    cholesterol = to_float(data.get('cholesterol'))
    weight_pounds = to_float(data.get('weightPounds'))
    weight_ounces = to_float(data.get('weightOunces'))
    serving_size_pounds = to_float(data.get('servingSizePounds'))
    serving_size_ounces = to_float(data.get('servingSizeOunces'))

    # Convert weight and serving size to grams
    if weight_unit == 'lb_oz':
        weight_in_grams = convert_to_grams(weight_pounds, weight_unit, weight_ounces)
    else:
        weight_in_grams = convert_to_grams(weight, weight_unit)

    if serving_size_unit == 'lb_oz':
        serving_size_in_grams = convert_to_grams(serving_size_pounds, serving_size_unit, serving_size_ounces)
    else:
        serving_size_in_grams = convert_to_grams(serving_size, serving_size_unit)

    # Calculating the main macros.
    fat = (fat_per_serving / serving_size_in_grams) * weight_in_grams
    protein = (protein_per_serving / serving_size_in_grams) * weight_in_grams
    net_carbs_per_serving = carbs_per_serving - fiber_per_serving - sugar_alcohol_per_serving
    net_carbs = (net_carbs_per_serving / serving_size_in_grams) * weight_in_grams

    # Calculating the calories from the macros we just calculated.
    calories = (fat * 9) + (protein * 4) + (net_carbs * 4)

    # Rounding the final results.
    fat = round(fat)
    protein = round(protein)
    net_carbs = round(net_carbs)
    calories = round(calories)

    # Format the weight for the result string.
    formatted_weight = format_weight(weight)
    formatted_weight_pounds = format_weight(weight_pounds)
    formatted_weight_ounces = format_weight(weight_ounces)

    # Create the result string that will be passed back to the client.
    if weight_unit == 'lb_oz':
        result_string = f"{formatted_weight_pounds} lbs & {formatted_weight_ounces} oz of {food_name} ({subclass}): {calories} calories, {protein}g of protein, {net_carbs}g of carbs, {fat}g of fat"
    else:
        result_string = f"{formatted_weight}{weight_unit} of {food_name} ({subclass}): {calories} calories, {protein}g of protein, {net_carbs}g of carbs, {fat}g of fat"

    print(result_string)

    return jsonify({
        'result': result_string,
        'foodName': food_name,
        'subclass': subclass,
        'amount': weight,
        'unit': weight_unit,
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