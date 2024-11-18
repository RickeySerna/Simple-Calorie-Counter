from flask import Flask, request, jsonify
from flask_cors import CORS
from decimal import Decimal, getcontext

app = Flask(__name__)
CORS(app)
getcontext().prec = 10

def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

# Using Decimal to avoid any long floating points where they don't belong.
## For example, if a computation should come out to 58.0, it can become 57.99999999 using normal floats. Decimal avoids that.
def to_decimal(value, default=Decimal('0.0')):
    try:
        # Checking if the var is empty to avoid conversion errors.
        if value is None or value == '':
            return default
        return Decimal(value)
    except (TypeError, ValueError, InvalidOperation):
        return default

# Formula to convert food weight and serving size form whatever unit the user used to grams.
def convert_to_grams(weight: Decimal, unit: str, ounces: Decimal = Decimal('0.0')) -> Decimal:
    # UPDATE: The function now uses a dictionary to pull the conversion rate.
    conversion_factors = {
        "kg": Decimal("1000"),
        "oz": Decimal("28.3495"),
        "lb": Decimal("453.592"),
        "mL": Decimal("1")
    }
    # For most units, we just return weight * the conversion factor passed on the function call.
    if unit in conversion_factors:
        return weight * conversion_factors[unit]
    # Lbs and oz is a slightly special case so we call those explicitly here.
    elif unit == "lb_oz":
        return (weight * conversion_factors["lb"]) + (ounces * conversion_factors["oz"])
    # This is triggered is the unit is "g" as that is not in conversion_factors. In that case, just return the weight.
    else:
        return weight

def format_weight(weight):
    if weight == int(weight):
        return str(int(weight))
    else:
        return str(weight)

def format_macros(macro):
    if macro == int(macro):
        return str(int(macro))
    else:
        return str(round(macro, 2))

@app.route('/api/calories', methods=['POST'])
def calculate_macros():
    data = request.get_json()
    print("Received data:", data)

    # Defining all of the different bits of info we got from the frontend.
    food_name = data.get('foodName')
    subclass = data.get('subclass')
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
        result_string = f"{formatted_weight_pounds} lbs & {formatted_weight_ounces} oz of {food_name} ({subclass}): {calories} calories, {formatted_protein}g of protein, {formatted_net_carbs}g of carbs, {formatted_fat}g of fat"
    else:
        if weight_unit in ['g', 'kg']:
            result_string = f"{formatted_weight}{weight_unit} of {food_name} ({subclass}): {calories} calories, {formatted_protein}g of protein, {formatted_net_carbs}g of carbs, {formatted_fat}g of fat"
        else:
            result_string = f"{formatted_weight} {weight_unit} of {food_name} ({subclass}): {calories} calories, {formatted_protein}g of protein, {formatted_net_carbs}g of carbs, {formatted_fat}g of fat"

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