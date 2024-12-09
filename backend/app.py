import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal, getcontext
from models import db
from controllers import food_item_bp


# Specifying the domain (currently just localhost) we'll be receiving request from to avoid CORS issues.
# When we move to prod, this will have to be updated to whatever the domain name ends up being.
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'fooditems.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

app.register_blueprint(food_item_bp)

getcontext().prec = 10

with app.app_context():
    print("Creating all tables...")
    try:
        db.create_all()
        print("Tables created.")
    except Exception as e:
        print("Error creating tables:", e)

if __name__ == '__main__':
    app.run(debug=True)

""" @app.route('/api/calories', methods=['POST'])
def calculate_macros():
    data = request.get_json()
    print("Received data:", data)

    # Defining all of the different bits of info we got from the frontend.
    food_name = data.get('foodName')
    subclass = data.get('subclass').strip()
    weight = to_decimal(data.get('weight'))
    weight_unit = data.get('weightUnit')
    serving_size = to_decimal(data.get('servingSize'))
    serving_size_unit = data.get('servingSizeUnit')
    fat_per_serving = to_decimal(data.get('fat'))
    protein_per_serving = to_decimal(data.get('protein'))
    carbs_per_serving = to_decimal(data.get('carbs'))
    fiber_per_serving = to_decimal(data.get('fiber'))
    sugar_alcohol_per_serving = to_decimal(data.get('sugarAlcohol'))
    sodium = to_decimal(data.get('sodium'))
    cholesterol = to_decimal(data.get('cholesterol'))
    weight_pounds = to_decimal(data.get('weightPounds'))
    weight_ounces = to_decimal(data.get('weightOunces'))
    serving_size_pounds = to_decimal(data.get('servingSizePounds'))
    serving_size_ounces = to_decimal(data.get('servingSizeOunces'))

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
    calories = (fat * Decimal('9')) + (protein * Decimal('4')) + (net_carbs * Decimal('4'))

    print(f"Macros before rounding: fat - {fat}, protein - {protein}, carbs - {net_carbs}, and calories - {calories}")

    # Formatting the final macros.
    formatted_fat = format_macros(fat)
    formatted_protein = format_macros(protein)
    formatted_net_carbs = format_macros(net_carbs)
    calories = round(calories)

    print(f"Macros after rounding: fat - {formatted_fat}, protein - {formatted_protein}, carbs - {formatted_net_carbs}, and calories - {calories}")

    # Format the weight for the result string.
    formatted_weight = format_weight(weight)
    formatted_weight_pounds = format_weight(weight_pounds)
    formatted_weight_ounces = format_weight(weight_ounces)

    # Create the result string that will be passed back to the client.
    if weight_unit == 'lb_oz':
        result_string = f"{formatted_weight_pounds} lbs & {formatted_weight_ounces} oz of {food_name}{f' ({subclass})' if subclass else ''}: {calories} calories, {formatted_protein}g of protein, {formatted_net_carbs}g of carbs, {formatted_fat}g of fat"
    else:
        if weight_unit in ['g', 'kg']:
            result_string = f"{formatted_weight}{weight_unit} of {food_name}{f' ({subclass})' if subclass else ''}: {calories} calories, {formatted_protein}g of protein, {formatted_net_carbs}g of carbs, {formatted_fat}g of fat"
        else:
            result_string = f"{formatted_weight} {weight_unit} of {food_name}{f' ({subclass})' if subclass else ''}: {calories} calories, {formatted_protein}g of protein, {formatted_net_carbs}g of carbs, {formatted_fat}g of fat"

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
    }) """