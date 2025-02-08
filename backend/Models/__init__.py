from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .FoodItem import FoodItem
from .Macros import Macros

FoodItem.macros = db.relationship('Macros', backref='food_item', uselist=False, cascade="all, delete-orphan")

# Explicitly defining what will be imported from this package from an import * statement.
__all__ = ['db', 'FoodItem']