from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from utils import *
from Models import db
#from Models.Macros import Macros

#db = SQLAlchemy()

class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    name = db.Column(db.String(100), nullable=False)
    sub_description = db.Column(db.String(200))
    weight_value = db.Column(db.String(100), nullable=False)
    weight_unit = db.Column(db.String(10), nullable=False)
    #macros = db.relationship('Macros', backref='food_item', uselist=False, cascade="all, delete-orphan")

    # calories = db.Column(db.String(100), nullable=False)
    # protein = db.Column(db.String(100), nullable=False)
    # carbs = db.Column(db.String(100), nullable=False)
    # fat = db.Column(db.String(100), nullable=False)

    def __init__(self, data):
        from Models.Macros import Macros
        print("Data from frontend in FoodItem constructor: ", data)
        self.date = datetime.strptime(data.get("date", date.today().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
        self.name = data.get("foodName")
        self.sub_description = data.get("subclass")
        self.weight_value = data.get("weight")#self.__format_weight(data)
        self.weight_unit = data.get("weightUnit")
        self.macros = Macros(data)

    def __format_weight(self, data):
        print(f"data as it is passed into FoodItem's __format_weights method: {data}")

        weight_unit = data.get("weightUnit")

        if weight_unit == "lb_oz":
            weightLbs = str(Decimal(data.get("weightPounds"))).rstrip('0').rstrip('.')
            weightOz = str(Decimal(data.get("weightOunces"))).rstrip('0').rstrip('.')

            weight_str = f"{weightLbs}&{weightOz}"
            print(f"weight string to be returned in the lb oz flow: {weight_str}")
            
            return weight_str
        else:
            weight = Decimal(data.get("weight"))
            weight_str = str(weight).rstrip('0').rstrip('.')
            return weight_str if '.' in weight_str else str(int(weight))