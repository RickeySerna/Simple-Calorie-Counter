from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/calories', methods=['POST'])
def calculate_calories():
    data = request.get_json()
    print("Received data:", data)
    
    food_name = data.get('foodName')
    subclass = data.get('subclass')
    amount = data.get('amount')
    calories = data.get('calories')
    fat = data.get('fat')
    protein = data.get('protein')
    carbs = data.get('carbs')
    fiber = data.get('fiber')
    sodium = data.get('sodium')

    return jsonify({
        'foodName': food_name,
        'subclass': subclass,
        'amount': amount,
        'calories': calories,
        'fat': fat,
        'protein': protein,
        'carbs': carbs,
        'fiber': fiber,
        'sodium': sodium
    })

if __name__ == '__main__':
    app.run(debug=True)