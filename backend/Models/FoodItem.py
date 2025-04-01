from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from Models import db
from .Macros import Macros

class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_log_id = db.Column(db.Integer, db.ForeignKey('food_log.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    sub_description = db.Column(db.String(200))
    weight_value = db.Column(db.String(100), nullable=False)
    weight_unit = db.Column(db.String(10), nullable=False)
    serving_size_value = db.Column(db.String(100), nullable=False)
    serving_size_unit = db.Column(db.String(100), nullable=False)
    protein_per_serving = db.Column(db.String(100), nullable=False)
    carbs_per_serving = db.Column(db.String(100), nullable=False)
    fat_per_serving = db.Column(db.String(100), nullable=False)
    macros = db.relationship('Macros', backref='food_item', uselist=False, cascade='all, delete-orphan')

    def __init__(self, data):
        print("Data from frontend in FoodItem constructor: ", data)

        existing_ID = data.get("id")
        if existing_ID:
            self.id = existing_ID

        date_str = data.get("date")
        if date_str:
            self.year = int(date_str[0:4])
            self.month = int(date_str[5:7])
            self.day = int(date_str[8:10])
        else:
            self.year = data.get("year")
            self.month = data.get("month")
            self.day = data.get("day")
        self.name = data.get("name")
        self.sub_description = data.get("sub_description")
        self.weight_value = data.get("weight_value")
        self.weight_unit = data.get("weight_unit")
        self.serving_size_value = data.get("serving_size_value")
        self.serving_size_unit = data.get("serving_size_unit")
        self.protein_per_serving = data.get("protein_per_serving")
        self.carbs_per_serving = data.get("carbs_per_serving")
        self.fat_per_serving = data.get("fat_per_serving")
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

    def to_dict(self):
        return {
            'id': self.id,
            'food_log_id': self.food_log_id,
            'year': self.year,
            'month': self.month,
            'day': self.day,
            'name': self.name,
            'sub_description': self.sub_description,
            'weight_value': self.weight_value,
            'weight_unit': self.weight_unit,
            'serving_size_value': self.serving_size_value,
            'serving_size_unit': self.serving_size_unit,
            'protein_per_serving': self.protein_per_serving,
            'carbs_per_serving': self.carbs_per_serving,
            'fat_per_serving': self.fat_per_serving,
            'result': self.generate_result_string(self),
            'macros': self.macros.to_dict()
        }