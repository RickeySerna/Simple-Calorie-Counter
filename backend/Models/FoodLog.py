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
    food_items = db.relationship('FoodItem', backref='food_log', lazy="dynamic", cascade="all, delete-orphan")

    def __init__(self, data):
        print("Data from frontend in FoodLog constructor: ", data)

        foodItems = []
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0

        for item in data.get("food_items", []):
            newFoodItem = FoodItem(item) 
            print(f"Here's our new FoodItem in the FoodLog constructor: {newFoodItem}")
            foodItems.append(newFoodItem)
            total_calories += float(newFoodItem.macros.calories)
            total_protein += float(newFoodItem.macros.protein)
            total_carbs += float(newFoodItem.macros.carbs)
            total_fat += float(newFoodItem.macros.fat)

        print("foodItems array after everything: ", foodItems)
        first_item = foodItems[0]
        self.year = first_item.year
        self.month = first_item.month
        self.day = first_item.day
        self.total_calories = str(total_calories)
        self.total_protein = str(total_protein)
        self.total_carbs = str(total_carbs)
        self.total_fat = str(total_fat)
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