from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .FoodLog import FoodLog
from .FoodItem import FoodItem
from .Macros import Macros

#FoodLog.food_items = db.relationship('FoodItem', backref='food_log', lazy="dynamic", cascade="all, delete-orphan")
#FoodItem.macros = db.relationship('Macros', backref='food_item', uselist=False, cascade="all, delete-orphan")

# Explicitly defining what will be imported from this package from an import * statement.
__all__ = ['db', 'FoodItem', 'FoodLog', 'Macros']