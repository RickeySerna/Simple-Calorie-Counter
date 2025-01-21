from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from utils import *

db = SQLAlchemy()

class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    name = db.Column(db.String(100), nullable=False)
    sub_description = db.Column(db.String(200))
    weight_value = db.Column(db.String(100), nullable=False)
    weight_unit = db.Column(db.String(10), nullable=False)
    macros = db.relationship('Macros', backref='food_item', uselist=False, cascade="all, delete-orphan")

    # calories = db.Column(db.String(100), nullable=False)
    # protein = db.Column(db.String(100), nullable=False)
    # carbs = db.Column(db.String(100), nullable=False)
    # fat = db.Column(db.String(100), nullable=False)

    def __init__(self, data):
        print("Data from frontend in FoodItem constructor: ", data)
        self.date = datetime.strptime(data.get("date", date.today().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
        self.name = data.get("foodName")
        self.sub_description = data.get("subclass")
        self.weight_value = data.get("weight")
        self.weight_unit = data.get("weightUnit")
        self.macros = self.Macros.Macro_construction(data)

    class Macros(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        food_item_id = db.Column(db.Integer, db.ForeignKey('food_item.id'), nullable=False)
        calories = db.Column(db.String(100), nullable=False)
        protein = db.Column(db.String(100), nullable=False)
        carbs = db.Column(db.String(100), nullable=False)
        fat = db.Column(db.String(100), nullable=False)

        def __init__(self, calories, protein, carbs, fat):
            self.calories = calories
            self.protein = protein
            self.carbs = carbs
            self.fat = fat

        @staticmethod
        def Macro_construction(data):
            print("Data from frontend in Macro_construction: ", data)

            # Defining all of the different bits of info we got from the frontend.
            # date = data.get('date')
            # food_name = data.get('foodName')
            # subclass = data.get('subclass').strip()
            # weight = to_decimal(data.get('weight'))
            # weight_unit = data.get('weightUnit')
            # serving_size = to_decimal(data.get('servingSize'))
            # serving_size_unit = data.get('servingSizeUnit')
            # fat_per_serving = to_decimal(data.get('fat'))
            # protein_per_serving = to_decimal(data.get('protein'))
            # carbs_per_serving = to_decimal(data.get('carbs'))
            # fiber_per_serving = to_decimal(data.get('fiber'))
            # sugar_alcohol_per_serving = to_decimal(data.get('sugarAlcohol'))
            # sodium = to_decimal(data.get('sodium'))
            # cholesterol = to_decimal(data.get('cholesterol'))
            # weight_pounds = to_decimal(data.get('weightPounds'))
            # weight_ounces = to_decimal(data.get('weightOunces'))
            # serving_size_pounds = to_decimal(data.get('servingSizePounds'))
            # serving_size_ounces = to_decimal(data.get('servingSizeOunces'))

            # Convert weight and serving size to grams.
            weights_in_grams = FoodItem.Macros.convert_to_grams(data)

            # Run macro calculation.
            calculated_macros = FoodItem.Macros.calculate_macros(data, weights_in_grams)

            # Now that the macros are calculated, pass them into format_macros to be formatted properly.
            formatted_macros = FoodItem.Macros.format_macros(calculated_macros)
            print(f"formatted_macros dict as returned from the function in models: {formatted_macros}")

            weights_to_format = {
                "weight": Decimal(data.get('weight') or '0.0'),
                "weight_pounds": Decimal(data.get('weightPounds') or '0.0'),
                "weight_ounces": Decimal(data.get('weightOunces') or '0.0')
            }

            formatted_weights = FoodItem.Macros.format_weights(weights_to_format)

            #print(f"Macros after rounding: fat - {formatted_fat}, protein - {formatted_protein}, carbs - {formatted_net_carbs}, and calories - {calories}")

            # Format the weight for the result string.
            # formatted_weight = format_weight(weight)
            # formatted_weight_pounds = format_weight(weight_pounds)
            # formatted_weight_ounces = format_weight(weight_ounces)

            print(f"formatted weight pounds: {formatted_weight_pounds}")
            print(f"formatted weight ounces: {formatted_weight_ounces}")

            # Create the weight value based on the unit used.
            if weight_unit == 'lb_oz':
                weight_string = handle_lboz_flow(formatted_weight_pounds, formatted_weight_ounces)
                print(f"Weight string in lb oz flow: {weight_string}")
            else:
                weight_string = formatted_weight
                print(f"Weight string in non-lb oz flow: {weight_string}")

            print(f"weight_string to be stored: {weight_string}")

            return FoodItem.Macros(
                calories=calories,
                protein=formatted_protein,
                carbs=formatted_net_carbs,
                fat=formatted_fat
            )
        
        # Formula to convert food weight and serving size form whatever unit the user used to grams.
        @staticmethod
        def convert_to_grams(data):

            #weight: Decimal, unit: str, ounces: Decimal = Decimal('0.0')) -> Decimal:

            # UPDATE: The function now uses a dictionary to pull the conversion rate.
            conversion_factors = {
                "kg": Decimal("1000"),
                "oz": Decimal("28.3495"),
                "lb": Decimal("453.592"),
                "mL": Decimal("1"),
                "mg": Decimal("0.001")
            }

            # For most units, we just return weight * the conversion factor passed on the function call.
            if data.get('weightUnit') in conversion_factors:
                weight_in_grams = Decimal(data.get('weight')) * conversion_factors[data.get('weightUnit')]
            # Lbs and oz is a slightly special case so we call those explicitly here.
            elif data.get('weightUnit') == "lb_oz":
                weight_in_grams = Decimal((data.get('weightPounds')) * conversion_factors["lb"]) + Decimal((data.get('weightOunces')) * conversion_factors["oz"])
            # This is triggered is the unit is "g" as that is not in conversion_factors. In that case, just return the weight.
            else:
                weight_in_grams = Decimal(data.get('weight'))

            if data.get('servingSizeUnit') in conversion_factors:
                serving_size_in_grams = Decimal(data.get('servingSize')) * conversion_factors[data.get('servingSizeUnit')]
            elif data.get('servingSizeUnit') == "lb_oz":
                serving_size_in_grams = Decimal((data.get('servingSizePounds')) * conversion_factors["lb"]) + Decimal((data.get('servingSizeOunces')) * conversion_factors["oz"])
            else:
                serving_size_in_grams = Decimal(data.get('servingSize'))

            weights = {
                "weight_in_grams": weight_in_grams,
                "serving_size_in_grams": serving_size_in_grams
            }

            print(f"weights being returned in convert_to_grams in model: {weights}")

            return weights
        
        @staticmethod
        def calculate_macros(data, weights):

            # Grabbing the weights calculated in convert_to_grams and passed into this function.
            weight_in_grams = weights["weight_in_grams"]
            serving_size_in_grams = weights["serving_size_in_grams"]

            # Grabbing the macros we need from the data object.
            fat_per_serving = Decimal(data.get('fat'))
            protein_per_serving = Decimal(data.get('protein'))
            carbs_per_serving = Decimal(data.get('carbs'))
            fiber_per_serving = Decimal(data.get('fiber') or '0.0')
            sugar_alcohol_per_serving = Decimal(data.get('sugarAlcohol') or '0')
            print(f"fiber after formatting with conditional: {fiber_per_serving}")

            print(f"Converted weight from convert_to_grams in calculate_macros: {weight_in_grams}")
            print(f"Converted serving size from convert_to_grams in calculate_macros: {serving_size_in_grams}")

            # Making sure the calculation variables are in Decimal too.

            # Calculating the main macros.
            fat = (fat_per_serving / serving_size_in_grams) * weight_in_grams
            protein = (protein_per_serving / serving_size_in_grams) * weight_in_grams
            net_carbs_per_serving = carbs_per_serving - fiber_per_serving - sugar_alcohol_per_serving
            net_carbs = (net_carbs_per_serving / serving_size_in_grams) * weight_in_grams

            # Calculating the calories from the macros we just calculated.
            calories = (fat * Decimal('9')) + (protein * Decimal('4')) + (net_carbs * Decimal('4'))

            print(f"Macros as calculated in calculate_macros: fat - {fat}, protein - {protein}, carbs - {net_carbs}, and calories - {calories}")

            calculated_macros = {
                "fat": fat,
                "protein": protein,
                "carbs": net_carbs,
                "calories": calories
            }

            print(f"calculated_macros being returned in calculate_macros in model: {calculated_macros}")

            return calculated_macros
        
        @staticmethod
        def format_macros(macros):
            print(f"calculated_macros passed into format_macros in the model: {macros}")

            # Creating an empty dictionary which the updated values from macros will be added into.
            formatted_macros = {}

            for key, value in macros.items():
                # We round calories differently from the rest; just get it to the nearest whole number, cast it as a string, and that's it.
                if key == 'calories':
                    rounded_value = str(round(value))
                else:
                    # For the other macros, we keep the same logic that was in the utils function; just going through the dict and applying it to each one.
                    # For better precision, now using the quantize and ROUND_HALF_UP methods from Decimal for rounding.
                    rounded_value = value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    rounded_str = str(rounded_value)
                    if rounded_str.endswith('.00'):
                        # If so, strip those zeros by converting to an int and then back to the string.
                        rounded_value = str(int(rounded_value))
                    else:
                        # Otherwise, just get rid of any trailing zeros.
                        rounded_value = rounded_str.rstrip('0').rstrip('.')

                # Now the formatting is done, add the value to the new dictionary.
                formatted_macros[key] = rounded_value

            return formatted_macros

        @staticmethod
        def format_weights(weights):
            print(f"weights dictionary in format_weights: {weights}")

            formatted_weights = {}

            for key, value in weights.items():
                weight_str = str(value).rstrip('0').rstrip('.')
                if ('.' in weight_str):
                    final_weight = weight_str
                else:
                    final_weight = str(int(value))
                
                formatted_weights[key] = final_weight

            print(f"weights dictionary being returned by format_weights: {formatted_weights}")

            return formatted_weights
