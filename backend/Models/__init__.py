from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .FoodItem import FoodItem
from .Macros import Macros

FoodItem.macros = db.relationship('Macros', backref='food_item', uselist=False, cascade="all, delete-orphan")