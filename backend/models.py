from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    name = db.Column(db.String(100), nullable=False)
    sub_description = db.Column(db.String(200))
    weight = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)

    def __init__(self, date, name, sub_description, weight, calories, protein, carbs, fat):
        self.date = date
        self.name = name
        self.sub_description = sub_description
        self.weight = weight
        self.calories = calories
        self.protein = protein
        self.carbs = carbs
        self.fat = fat