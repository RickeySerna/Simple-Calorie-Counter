from decimal import Decimal, getcontext, ROUND_HALF_UP
import re

def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

# Using Decimal to avoid any long floating points where they don't belong.
## For example, if a computation should come out to 58.0, it can become 57.99999999 using normal floats. Decimal avoids that.

# Set precision
getcontext().prec = 10  # Adjust precision as needed
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
        "mL": Decimal("1"),
        "mg": Decimal("0.001")
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

# Now that weight_value is sent as a separate function, we need a method to send lb_oz values as a single value.
# For that, we're converting the value into a single lbs value. That'll get converted back later where needed.
# UPDATE: Changing the way we handle lb & oz flow. I want to give the ability to add decimal place values into the lbs and oz fields if they want.
# As such, no more calculations here; just slap the values as we got them (after formatting) and return that to be added to the DB.
# It'll be split and broken up later when generating the result string, with decimal places preserved.
def handle_lboz_flow(pounds, ounces):

    # Just slap them together with an "&" in the middle. This will be used to split them later.
    lbozString = f"{pounds}&{ounces}"
    
    return lbozString

def format_weight(weight):
    weight_str = str(weight).rstrip('0').rstrip('.')
    return weight_str if '.' in weight_str else str(int(weight))

def format_macros(macro: Decimal) -> str:
    # For better precision, now using the quantize and ROUND_HALF_UP methods from Decimal for rounding. Basically rounds to the nearest hundreths place.
    rounded_macro = macro.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Now go back to the original logic; convert to a str and check if it ends with .00.
    rounded_str = str(rounded_macro)
    if rounded_str.endswith('.00'):
        # If so, strip those zeros by converting to an int and then back to the string.
        return str(int(rounded_macro))
    else:
        # Otherwise, just get rid of any trailing zeros.
        return rounded_str.rstrip('0').rstrip('.')

def calculate_macros(data):
    # Defining all of the different bits of info we got from the frontend.
    date = data.get('date')
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
        print("hello we are in lboz flow")
        print(f"weight_in_grams in lboz flow: {weight_in_grams}")
    else:
        weight_in_grams = convert_to_grams(weight, weight_unit)
        print("WE ARE NOT IN LBOZ FLOW")

    if serving_size_unit == 'lb_oz':
        serving_size_in_grams = convert_to_grams(serving_size_pounds, serving_size_unit, serving_size_ounces)
    else:
        serving_size_in_grams = convert_to_grams(serving_size, serving_size_unit)

    # Making sure the calculation variables are in Decimal too.
    weight_in_grams = to_decimal(weight_in_grams)
    serving_size_in_grams = to_decimal(serving_size_in_grams)

    # Calculating the main macros.
    fat = (fat_per_serving / serving_size_in_grams) * weight_in_grams
    protein = (protein_per_serving / serving_size_in_grams) * weight_in_grams
    net_carbs_per_serving = carbs_per_serving - fiber_per_serving - sugar_alcohol_per_serving
    net_carbs = (net_carbs_per_serving / serving_size_in_grams) * weight_in_grams

    # Calculating the calories from the macros we just calculated.
    calories = (fat * Decimal('9')) + (protein * Decimal('4')) + (net_carbs * Decimal('4'))

    print(f"Macros before rounding: fat - {fat}, protein - {protein}, carbs - {net_carbs}, and calories - {calories}")

    print(f"type of fat before formatting: {type(fat)}")

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

    print(f"formatted weight pounds: {formatted_weight_pounds}")
    print(f"formatted weight ounces: {formatted_weight_ounces}")

    # Create the result string that will be passed back to the client.
    if weight_unit == 'lb_oz':
        #result_string = f"{formatted_weight_pounds} lbs & {formatted_weight_ounces} oz of {food_name}{f' ({subclass})' if subclass else ''}: {calories} calories, {formatted_protein}g of protein, {formatted_net_carbs}g of carbs, {formatted_fat}g of fat"
        #weight_string = f"{formatted_weight_pounds} lbs & {formatted_weight_ounces} oz"
        weight_string = handle_lboz_flow(formatted_weight_pounds, formatted_weight_ounces)
        print(f"Weight string in lb oz flow: {weight_string}")
    else:
        weight_string = formatted_weight
        print(f"Weight string in non-lb oz flow: {weight_string}")
        # if weight_unit in ['g', 'kg']:
        #     #result_string = f"{formatted_weight}{weight_unit} of {food_name}{f' ({subclass})' if subclass else ''}: {calories} calories, {formatted_protein}g of protein, {formatted_net_carbs}g of carbs, {formatted_fat}g of fat"
        #     weight_string = f"{formatted_weight}{weight_unit}"
        # else:
        #     #result_string = f"{formatted_weight} {weight_unit} of {food_name}{f' ({subclass})' if subclass else ''}: {calories} calories, {formatted_protein}g of protein, {formatted_net_carbs}g of carbs, {formatted_fat}g of fat"
        #     weight_string = f"{formatted_weight} {weight_unit}"

    print(f"weight_string to be stored: {weight_string}")

    macros_dict = {
        "date": date,
        "food_name": food_name,
        "subclass": subclass,
        "weight_value": weight_string,
        "weight_unit": weight_unit,
        "calories": str(calories),
        "protein": str(formatted_protein),
        "carbs": str(formatted_net_carbs),
        "fat": str(formatted_fat),
    }

    return(macros_dict)

def generate_result_string(item):
    print(f"Item in generate_result_string: {item}")
    
    weight_value = item.weight_value
    weight_unit = item.weight_unit

    print(f"The weight to split: {weight_value}")
    print(f"The item's weight unit: {weight_unit}")

    # The past logic is mostly not needed anymore now that weight_value and weight_unit come in split already.
    # All that needs to be done is to convert the weight_value back to lbs&oz format if that's the format it was chosen in.
    # UPDATE: Lb&oz flow is handled differently now. All that we're going to get here is a string like: "lb&oz"
    # So all we need to do is split the string based on the "&" and create the weight_value string from that.
    if weight_unit == 'lb_oz':
        print(f"lboz weight string in generate_result_string: {weight_value}")
        poundsAndOunces = weight_value.split("&")
        pounds = poundsAndOunces[0]
        ounces = poundsAndOunces[1]
        print(f"Pounds after splitting in generate_result_string: {pounds}")
        print(f"Ounces after splitting in generate_result_string: {ounces}")
        weight_value = f"{pounds} lb{'s' if pounds != 1 else ''} & {ounces} oz"

    print(f"Weight value after the lboz if statement: {weight_value}")

    # Create the result string based on the weight unit
    if weight_unit in ['lb_oz']:
        return f"{weight_value} of {item.name}{f' ({item.sub_description})' if item.sub_description else ''}: {item.calories} calories, {item.protein}g of protein, {item.carbs}g of carbs, {item.fat}g of fat"
    elif weight_unit in ['g', 'kg']:
        return f"{weight_value}{weight_unit} of {item.name}{f' ({item.sub_description})' if item.sub_description else ''}: {item.calories} calories, {item.protein}g of protein, {item.carbs}g of carbs, {item.fat}g of fat"
    else:
        return f"{weight_value} {weight_unit} of {item.name}{f' ({item.sub_description})' if item.sub_description else ''}: {item.calories} calories, {item.protein}g of protein, {item.carbs}g of carbs, {item.fat}g of fat"

    # # Using a regular expression to get the unit and thus the correct formatting for the result string.
    # # In the simplest case, we just see if the user used lbs & oz format. If the did, just set the weight value as the entire string from the object.
    # if 'lbs &' in weight:
    #     weight_value = weight
    #     # Still set this so we know when to use this weight_value.
    #     weight_unit = 'lbs & oz'
    # # Other wise, the regular expression comes in.
    # else:
    #     # The match function captures two groups; the weight and the weight unit. Weight is numeric, weight unit is non-numeric.
    #     match = re.match(r"([0-9.]+)\s*(\D+)", weight)
    #     if match:
    #         weight_value, weight_unit = match.groups()
    #     # In case a string comes in with a bad format, we add this to make sure the whole thing doesn't break. Shouldn't happen, but just in case.
    #     else:
    #         weight_value, weight_unit = "Bad format!", ''    

    # # The attributes all come in with a .0, so wrapping them all in str(int()) to strip that.
    # if weight_unit == 'lbs & oz':
    #     return f"{weight_value} of {item.name}{f' ({item.sub_description})' if item.sub_description else ''}: {str(int(item.calories))} calories, {str(int(item.protein))}g of protein, {str(int(item.carbs))}g of carbs, {str(int(item.fat))}g of fat"
    # elif weight_unit in ['g', 'kg']:
    #     return f"{weight_value}{weight_unit} of {item.name}{f' ({item.sub_description})' if item.sub_description else ''}: {str(int(item.calories))} calories, {str(int(item.protein))}g of protein, {str(int(item.carbs))}g of carbs, {str(int(item.fat))}g of fat"
    # else:
    #     return f"{weight_value} {weight_unit} of {item.name}{f' ({item.sub_description})' if item.sub_description else ''}: {str(int(item.calories))} calories, {str(int(item.protein))}g of protein, {str(int(item.carbs))}g of carbs, {str(int(item.fat))}g of fat"