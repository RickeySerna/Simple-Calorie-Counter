from flask import Blueprint, request, jsonify
from models import db, FoodItem
from utils import *

food_item_bp = Blueprint('food_item_bp', __name__)

@food_item_bp.route('/api/fooditems', methods=['POST'])
def add_food_item():
    data = request.get_json()
    print("Received data:", data)

    macros = calculate_macros(data)
    print(f"Macros in add_food_item: ", macros)

    new_food_item = FoodItem(
        name=macros["food_name"],
        sub_description=macros["subclass"],
        weight=macros["weight"],
        calories=macros["calories"],
        protein=macros["protein"],
        carbs=macros["carbs"],
        fat=macros["fat"],
    )

    db.session.add(new_food_item)
    db.session.commit()
    print("Added new food item:", new_food_item)

    return jsonify({'message': 'Food item added successfully', 'result': macros["result_string"]}), 201

@food_item_bp.route('/api/fooditems', methods=['GET'])
def get_food_items():
    food_items = FoodItem.query.all()
    result = []
    for item in food_items:
        food_data = {
            'id': item.id,
            'name': item.name,
            'sub_description': item.sub_description,
            'calories': item.calories,
            'protein': item.protein,
            'carbs': item.carbs,
            'fat': item.fat
        }
        result.append(food_data)
    return jsonify(result)

@food_item_bp.route('/api/fooditems/<int:id>', methods=['GET'])
def get_food_item(id):
    item = FoodItem.query.get_or_404(id)
    food_data = {
        'id': item.id,
        'name': item.name,
        'sub_description': item.sub_description,
        'calories': item.calories,
        'protein': item.protein,
        'carbs': item.carbs,
        'fat': item.fat
    }
    return jsonify(food_data)

@food_item_bp.route('/api/fooditems/<int:id>', methods=['PUT'])
def update_food_item(id):
    data = request.get_json()
    item = FoodItem.query.get_or_404(id)
    item.name = data['name']
    item.sub_description = data.get('sub_description', item.sub_description)
    item.calories = data['calories']
    item.protein = data['protein']
    item.carbs = data['carbs']
    item.fat = data['fat']
    db.session.commit()
    return jsonify({'message': 'Food item updated successfully'})

@food_item_bp.route('/api/fooditems/<int:id>', methods=['DELETE'])
def delete_food_item(id):
    item = FoodItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Food item deleted successfully'})