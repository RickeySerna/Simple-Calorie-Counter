from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/calories', methods=['POST'])
def calculate_macros():
    data = request.get_json()
    print("Received data:", data)

    # Defining all of the different bits of info we got from the frontend.
    food_name = data.get('foodName')
    subclass = data.get('subclass')
    weight = float(data.get('weight'))
    serving_size = float(data.get('servingSize'))
    fat_per_serving = float(data.get('fat'))
    protein_per_serving = float(data.get('protein'))
    carbs_per_serving = float(data.get('carbs'))
    fiber_per_serving = float(data.get('fiber', 0))
    sugar_alcohol_per_serving = float(data.get('sugarAlcohol', 0))
    sodium = data.get('sodium', 0)
    cholesterol = data.get('cholesterol', 0)

    # Calculating the main macros.
    fat = (fat_per_serving / serving_size) * weight
    protein = (protein_per_serving / serving_size) * weight
    net_carbs_per_serving = carbs_per_serving - fiber_per_serving - sugar_alcohol_per_serving
    net_carbs = (net_carbs_per_serving / serving_size) * weight

    # Calculating the calories from the macros we just calculated.
    calories = (fat * 9) + (protein * 4) + (net_carbs * 4)

    # Create the result string that will be passed back to the client.
    result_string = f"{weight}g of {food_name} ({subclass}): {calories:.2f} calories, {protein:.2f}g of protein, {net_carbs:.2f}g of carbs, {fat:.2f}g of fat"

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