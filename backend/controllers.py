from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, FoodItem
from utils import *

food_item_bp = Blueprint('food_item_bp', __name__, url_prefix='/api')

@food_item_bp.route('/fooditems', methods=['POST'])
def add_food_item():
    data = request.get_json()
    print("Received data:", data)

    macros = calculate_macros(data)
    print(f"Macros in add_food_item: ", macros)

    new_food_item = FoodItem(
        date=datetime.strptime(macros["date"], '%Y-%m-%d').date(),
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

    return jsonify({'message': 'Food item added successfully', 'id': new_food_item.id}), 201

@food_item_bp.route('/fooditems', methods=['GET'])
def get_food_items_by_date():
    date_str = request.args.get('date')
    print(f"Date in server: {date_str}")
    
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    items = FoodItem.query.filter_by(date=date_obj).all()
    
    if not items:
        return jsonify([])
    
    food_data = [{
        'id': item.id,
        'name': item.name,
        'sub_description': item.sub_description,
        'weight': item.weight,
        'calories': item.calories,
        'protein': item.protein,
        'carbs': item.carbs,
        'fat': item.fat,
        'result': generate_result_string(item)
    } for item in items]
    
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