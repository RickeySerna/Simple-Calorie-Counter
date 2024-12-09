from flask import Blueprint, request, jsonify
from models import db, FoodItem
from utils import *

food_item_bp = Blueprint('food_item_bp', __name__)

@food_item_bp.route('/api/fooditems', methods=['POST'])
def add_food_item():
    data = request.get_json()
    print("Received data:", data)  # Debug print

    new_food_item = FoodItem(
        name=data['foodName'],
        sub_description=data.get('subclass', ''),
        calories=to_decimal(data.get('calories')),
        protein=to_decimal(data.get('protein')),
        carbs=to_decimal(data.get('carbs')),
        fat=to_decimal(data.get('fat'))
    )
    db.session.add(new_food_item)
    db.session.commit()
    print("Added new food item:", new_food_item)  # Debug print

    result_string = format_food_item_string(new_food_item)
    return jsonify({'message': 'Food item added successfully', 'result': result_string}), 201

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

def format_food_item_string(item):
    formatted_fat = format_macros(to_decimal(item.fat))
    formatted_protein = format_macros(to_decimal(item.protein))
    formatted_net_carbs = format_macros(to_decimal(item.carbs))
    calories = round(to_decimal(item.calories))

    result_string = f"{item.name}{f' ({item.sub_description})' if item.sub_description else ''}: {calories} calories, {formatted_protein}g of protein, {formatted_net_carbs}g of carbs, {formatted_fat}g of fat"
    return result_string