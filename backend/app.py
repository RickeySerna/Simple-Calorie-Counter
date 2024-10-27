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
    calories = data.get('calories')
    servingSize = float(data.get('servingSize'))
    fat_per_serving = float(data.get('fat'))
    protein_per_serving = float(data.get('protein'))
    carbs_per_serving = float(data.get('carbs'))
    fiber = data.get('fiber')
    sodium = data.get('sodium')

    # Calculating the main macros.
    fat = (fat_per_serving / servingSize) * weight
    protein = (protein_per_serving / servingSize) * weight
    carbs = (carbs_per_serving / servingSize) * weight
    
    # Calculating the calories from the macros we just calculated.
    calories = (fat * 9) + (protein * 4) + (carbs * 4)

    # Create the result string that will be passed back to the client.
    result_string = f"{calories:.2f} calories, {protein:.2f}g of protein, {carbs:.2f}g of carbs, {fat:.2f}g of fat"

    print(result_string)

    return jsonify({
        'result': result_string,
        'foodName': food_name,
        'subclass': subclass,
        'weight': weight,
        'calories': calories,
        'servingSize': servingSize,
        'fat': fat,
        'protein': protein,
        'carbs': carbs,
        'fiber': fiber,
        'sodium': sodium
    })

if __name__ == '__main__':
    app.run(debug=True)