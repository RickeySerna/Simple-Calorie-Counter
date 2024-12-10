from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sub_description = db.Column(db.String(200))
    weight = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)

    def __init__(self, name, sub_description, weight, calories, protein, carbs, fat):
        self.name = name
        self.sub_description = sub_description
        self.weight = weight
        self.calories = calories
        self.protein = protein
        self.carbs = carbs
        self.fat = fat