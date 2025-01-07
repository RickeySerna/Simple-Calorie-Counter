from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    name = db.Column(db.String(100), nullable=False)
    sub_description = db.Column(db.String(200))
    weight_value = db.Column(db.String(100), nullable=False)
    weight_unit = db.Column(db.String(10), nullable=False)
    calories = db.Column(db.String(100), nullable=False)
    protein = db.Column(db.String(100), nullable=False)
    carbs = db.Column(db.String(100), nullable=False)
    fat = db.Column(db.String(100), nullable=False)

    def __init__(self, date, name, sub_description, weight_value, weight_unit, calories, protein, carbs, fat):
        self.date = date
        self.name = name
        self.sub_description = sub_description
        self.weight_value = weight_value
        self.weight_unit = weight_unit
        self.calories = calories
        self.protein = protein
        self.carbs = carbs
        self.fat = fat