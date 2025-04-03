from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from decimal import Decimal, getcontext, ROUND_HALF_UP
from Models import db

class Macros(db.Model):
    __tablename__ = 'macros'
    id = db.Column(db.Integer, primary_key=True)
    food_item_id = db.Column(db.Integer, db.ForeignKey('food_item.id'), nullable=False)
    calories = db.Column(db.String(100), nullable=False)
    protein = db.Column(db.String(100), nullable=False)
    carbs = db.Column(db.String(100), nullable=False)
    fat = db.Column(db.String(100), nullable=False)

    def __init__(self, data):
        print("Data from frontend in __init__: ", data)

        existing_ID = data.get("id")
        if existing_ID:
            self.id = existing_ID

        # Convert weight and serving size to grams.
        weights_in_grams = self.__convert_to_grams(data)

        # Run macro calculation.
        calculated_macros = self.__calculate_macros(data, weights_in_grams)

        # Now that the macros are calculated, pass them into format_macros to be formatted properly.
        formatted_macros = self.__format_macros(calculated_macros)
        print(f"formatted_macros dict as returned from the function in models: {formatted_macros}")
        
        self.calories = formatted_macros["calories"]
        self.protein = formatted_macros["protein"]
        self.carbs = formatted_macros["carbs"]
        self.fat = formatted_macros["fat"]
    
    # Formula to convert food weight and serving size form whatever unit the user used to grams.
    def __convert_to_grams(self, data):

        # A dictionary storing the conversion factors for each unit of measurement.
        conversion_factors = {
            "kg": Decimal("1000"),
            "oz": Decimal("28.3495"),
            "lb": Decimal("453.592"),
            "mL": Decimal("1"),
            "mg": Decimal("0.001")
        }

        # For most units, we just return weight * the conversion factor passed on the function call.
        if data.get('weight_unit') in conversion_factors:
            weight_in_grams = Decimal(data.get('weight_value')) * conversion_factors[data.get('weight_unit')]
        # Lbs and oz is a slightly special case so we call those explicitly here.
        elif data.get('weight_unit') == "lb_oz":
            weight_in_grams = (Decimal((data.get('weightPounds'))) * conversion_factors["lb"]) + (Decimal((data.get('weightOunces'))) * conversion_factors["oz"])
        # This is triggered is the unit is "g" as that is not in conversion_factors. In that case, just return the weight.
        else:
            weight_in_grams = Decimal(data.get('weight_value'))

        if data.get('serving_size_unit') in conversion_factors:
            serving_size_in_grams = Decimal(data.get('serving_size_value')) * conversion_factors[data.get('serving_size_unit')]
        elif data.get('serving_size_unit') == "lb_oz":
            serving_size_in_grams = (Decimal((data.get('servingSizePounds'))) * conversion_factors["lb"]) + (Decimal((data.get('servingSizeOunces'))) * conversion_factors["oz"])
        else:
            serving_size_in_grams = Decimal(data.get('serving_size_value'))

        weights = {
            "weight_in_grams": weight_in_grams,
            "serving_size_in_grams": serving_size_in_grams
        }

        print(f"weights being returned in convert_to_grams in model: {weights}")

        return weights
    
    def __calculate_macros(self, data, weights):

        # Grabbing the weights calculated in convert_to_grams and passed into this function.
        weight_in_grams = weights["weight_in_grams"]
        serving_size_in_grams = weights["serving_size_in_grams"]

        # Grabbing the macros we need from the data object.
        fat_per_serving = Decimal(data.get('fat_per_serving'))
        protein_per_serving = Decimal(data.get('protein_per_serving'))
        carbs_per_serving = Decimal(data.get('carbs_per_serving'))
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
    
    def __format_macros(self, macros):
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'food_item_id': self.food_item_id,
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat
        }