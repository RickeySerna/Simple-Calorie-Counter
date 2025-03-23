from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from Models import db
from .FoodItem import FoodItem

class FoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    total_calories = db.Column(db.String(100), nullable=False)
    total_protein = db.Column(db.String(100), nullable=False)
    total_carbs = db.Column(db.String(100), nullable=False)
    total_fat = db.Column(db.String(100), nullable=False)

    def __init__(self, data):
        print("Data from frontend in FoodLog constructor: ", data)

        # Creating the initial FoodItem outside of the food_items array so that we can use it's initial macros as the starting point for the FoodLogs' macros attributes.
        foodItems = []
        for i, v in enumerate(data.get("food_items")):
            foodItems.append(FoodItem(v))

        self.year = data.get("year")
        self.month = data.get("month")
        self.day = data.get("day")
        self.total_calories = data.get("total_calories")
        self.total_protein = data.get("total_protein")
        self.total_carbs = data.get("total_carbs")
        self.total_fat = data.get("total_fat")
        self.food_items = foodItems

    def to_dict(self):
        return {
            'id': self.id,
            'year': self.year,
            'month': self.month,
            'day': self.day,
            'total_calories': self.total_calories,
            'total_protein': self.total_protein,
            'total_carbs': self.total_carbs,
            'total_fat': self.total_fat,
            'food_items': [item.to_dict() for item in self.food_items]
        }