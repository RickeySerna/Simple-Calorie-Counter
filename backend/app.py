from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

@app.route('/api/calories', methods=['POST'])
def calculate_macros():
    data = request.get_json()
    print("Received data:", data)

    # Defining all of the different bits of info we got from the frontend.
    food_name = data.get('foodName')
    subclass = data.get('subclass')
    weight = round(to_float(data.get('weight')))
    serving_size = to_float(data.get('servingSize'))
    fat_per_serving = to_float(data.get('fat'))
    protein_per_serving = to_float(data.get('protein'))
    carbs_per_serving = to_float(data.get('carbs'))
    fiber_per_serving = to_float(data.get('fiber'))
    sugar_alcohol_per_serving = to_float(data.get('sugarAlcohol'))
    sodium = to_float(data.get('sodium'))
    cholesterol = to_float(data.get('cholesterol'))

    # Calculating the main macros.
    fat = round((fat_per_serving / serving_size) * weight)
    protein = round((protein_per_serving / serving_size) * weight)
    net_carbs_per_serving = carbs_per_serving - fiber_per_serving - sugar_alcohol_per_serving
    net_carbs = round((net_carbs_per_serving / serving_size) * weight)

    # Calculating the calories from the macros we just calculated.
    calories = (fat * 9) + (protein * 4) + (net_carbs * 4)

    # Create the result string that will be passed back to the client.
    result_string = f"{weight}g of {food_name} ({subclass}): {calories} calories, {protein}g of protein, {net_carbs}g of carbs, {fat}g of fat"

    print(result_string)

    return jsonify({
        'result': result_string,
        'foodName': food_name,
        'subclass': subclass,
        'amount': weight,
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