from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from utils import *
from Models import db
from .Macros import Macros

class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    name = db.Column(db.String(100), nullable=False)
    sub_description = db.Column(db.String(200))
    weight_value = db.Column(db.String(100), nullable=False)
    weight_unit = db.Column(db.String(10), nullable=False)

    def __init__(self, data):
        print("Data from frontend in FoodItem constructor: ", data)
        self.date = datetime.strptime(data.get("date", date.today().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
        self.name = data.get("foodName")
        self.sub_description = data.get("subclass")
        self.weight_value = data.get("weight")
        self.weight_unit = data.get("weightUnit")
        self.macros = Macros(data)

    def generate_result_string(self, item):
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

            # Checking that the split actually resulted in two objects.
            if len(poundsAndOunces) == 2:
                pounds = poundsAndOunces[0]
                ounces = poundsAndOunces[1]
                print(f"Pounds after splitting in generate_result_string: {pounds}")
                print(f"Ounces after splitting in generate_result_string: {ounces}")
                weight_value = f"{pounds} lb{'s' if pounds != 1 else ''} & {ounces} oz"
            # If not, then the weight format was not in a format that was expected.
            # To make sure the GET call still works, we just set the weight_value to an error message.
            else:
                print(f"Unexpected weight_value format for lb_oz: {weight_value}")
                weight_value = "Invalid weight format"

        print(f"Weight value after the lboz if statement: {weight_value}")

        # Create the result string based on the weight unit.
        if weight_unit in ['lb_oz']:
            return f"{weight_value} of {item.name}{f' ({item.sub_description})' if item.sub_description else ''}: {item.macros.calories} calories, {item.macros.protein}g of protein, {item.macros.carbs}g of carbs, {item.macros.fat}g of fat"
        elif weight_unit in ['g', 'kg']:
            return f"{weight_value}{weight_unit} of {item.name}{f' ({item.sub_description})' if item.sub_description else ''}: {item.macros.calories} calories, {item.macros.protein}g of protein, {item.macros.carbs}g of carbs, {item.macros.fat}g of fat"
        else:
            return f"{weight_value} {weight_unit} of {item.name}{f' ({item.sub_description})' if item.sub_description else ''}: {item.macros.calories} calories, {item.macros.protein}g of protein, {item.macros.carbs}g of carbs, {item.macros.fat}g of fat"