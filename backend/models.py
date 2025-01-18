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
        self.macros = self.Macros.calculate_macros(data)

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
        def calculate_macros(data):
            print("Data from frontend in calculate_macros: ", data)

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

            # Convert weight and serving size to grams.
            weights_in_grams = FoodItem.Macros.convert_to_grams(data)

            weight_in_grams = weights_in_grams["weight_in_grams"]
            serving_size_in_grams = weights_in_grams["serving_size_in_grams"]

            print(f"Converted weight from convert_to_grams in model: {weight_in_grams}")
            print(f"Converted serving size from convert_to_grams in model: {serving_size_in_grams}")

            # if weight_unit == 'lb_oz':
            #     weight_in_grams = convert_to_grams(weight_pounds, weight_unit, weight_ounces)
            #     print(f"weight_in_grams in lboz flow: {weight_in_grams}")
            # else:
            #     weight_in_grams = convert_to_grams(weight, weight_unit)
            #     print("WE ARE NOT IN LBOZ FLOW")

            # if serving_size_unit == 'lb_oz':
            #     serving_size_in_grams = convert_to_grams(serving_size_pounds, serving_size_unit, serving_size_ounces)
            # else:
            #     serving_size_in_grams = convert_to_grams(serving_size, serving_size_unit)

            # Making sure the calculation variables are in Decimal too.

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
            formatted_fat = str(format_macros(fat))
            formatted_protein = str(format_macros(protein))
            formatted_net_carbs = str(format_macros(net_carbs))
            calories = str(round(calories))

            print(f"Macros after rounding: fat - {formatted_fat}, protein - {formatted_protein}, carbs - {formatted_net_carbs}, and calories - {calories}")

            # Format the weight for the result string.
            formatted_weight = format_weight(weight)
            formatted_weight_pounds = format_weight(weight_pounds)
            formatted_weight_ounces = format_weight(weight_ounces)

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
