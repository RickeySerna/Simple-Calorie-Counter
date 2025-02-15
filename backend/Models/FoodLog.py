from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from Models import db

class FoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    total_calories = db.Column(db.String(100), nullable=False)
    total_protein = db.Column(db.String(100), nullable=False)
    total_carbs = db.Column(db.String(100), nullable=False)
    total_fat = db.Column(db.String(100), nullable=False)