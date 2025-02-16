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
        self.year = int(data.get("date")[0:4])
        self.month = int(data.get("date")[5:7])
        self.day = int(data.get("date")[8:10])
        self.total_calories = "0"
        self.total_protein = "0"
        self.total_carbs = "0"
        self.total_fat = "0"
        self.food_items = [FoodItem(data)]