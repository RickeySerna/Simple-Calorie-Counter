from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

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
            return FoodItem.Macros(
                calories=data.get("calories"),
                protein=data.get("protein"),
                carbs=data.get("carbs"),
                fat=data.get("fat")
            )
