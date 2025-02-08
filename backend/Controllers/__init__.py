from flask import Blueprint
from .FoodItemController import food_item_bp

# List of blueprints to be registered. This will be expanded as we add more and more controllers.
blueprints = [food_item_bp]

# Setting up the above blueprints to be sent when this 'package' is imported.
__all__ = ['blueprints']